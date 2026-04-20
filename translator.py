import re
import json
import os

# Providers are imported lazily inside _call_llm to avoid hard dependencies
# — the user only needs the SDK for the provider they actually use.

# ══════════════════════════════════════════════════════════════════════════════
#  GLOSSARY
# ══════════════════════════════════════════════════════════════════════════════
def _get_appdata_glossary():
    """Return the writable glossary path in AppData (mirrors app.py logic)."""
    appdata = os.environ.get("APPDATA")
    if appdata:
        folder = os.path.join(appdata, "WTS Translator")
    else:
        folder = os.path.join(os.path.expanduser("~"), ".wts_translator")
    return os.path.join(folder, "glossary.json")

def load_glossary(path=None):
    """Load glossary — prefers the writable AppData copy, falls back to bundled."""
    if path is None:
        appdata_path = _get_appdata_glossary()
        if os.path.exists(appdata_path):
            path = appdata_path
        else:
            # Fallback: bundled glossary next to the script (dev mode)
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "glossary.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# ══════════════════════════════════════════════════════════════════════════════
#  WTS PARSER / BUILDER
# ══════════════════════════════════════════════════════════════════════════════
def parse_wts(filepath):
    with open(filepath, "r", encoding="utf-8-sig") as f:
        raw = f.read()
    pattern = re.compile(
        r'STRING\s+(\d+)\s*(?://(.*?)\n)?\{\s*(.*?)\s*\}',
        re.DOTALL
    )
    blocks = []
    for m in pattern.finditer(raw):
        text = m.group(3)
        blocks.append({
            "id":      int(m.group(1)),
            "comment": m.group(2).strip() if m.group(2) else None,
            "text":    text,
            "empty":   text.strip() == ""
        })
    return blocks

def build_wts(blocks):
    lines = []
    for b in blocks:
        lines.append(f"STRING {b['id']}")
        if b["comment"]:
            lines.append(f"// {b['comment']}")
        lines.append("{")
        lines.append(b.get("translated", b["text"]))
        lines.append("}")
        lines.append("")
    return "\n".join(lines)

# ══════════════════════════════════════════════════════════════════════════════
#  TAG PROTECTION  |cXXXXXXXX / |r  →  @@T0@@
# ══════════════════════════════════════════════════════════════════════════════
COLOR_RE  = re.compile(r'\|c[0-9a-fA-F]{8}|\|r')
HOTKEY_RE = re.compile(r'\|c[0-9a-fA-F]{8}([A-Za-z])\|r')

# Detects a color tag wrapping ONE letter immediately followed by more word
# characters WITHOUT a space — i.e. the color splits a single word.
# Example: |cffffcc00A|rpothecary  →  group(1)='A', group(2)='pothecary'
# We strip the color and merge so the LLM sees the full word: 'Apothecary'.
_SPLIT_WORD_RE = re.compile(
    r'\|c[0-9a-fA-F]{8}([A-Za-z])\|r([A-Za-z]+)'
)

def merge_split_words(text):
    """Remove color codes that split a single word across colored/plain fragments.

    |cffffcc00A|rpothecary  ->  Apothecary   (color spans only first letter)
    |cffffcc00Nivel|r 1     ->  left alone   (space after |r: not a split word)
    """
    return _SPLIT_WORD_RE.sub(lambda m: m.group(1) + m.group(2), text)

def strip_tags(text):
    return COLOR_RE.sub("", text).strip()

def protect_tags(text):
    # Step 0: fuse any color-split words BEFORE protecting anything.
    # This ensures the LLM always sees complete, translatable words.
    text = merge_split_words(text)

    tag_map = {}
    ctr     = [0]

    def new_key():
        k = f"@@T{ctr[0]}@@"
        ctr[0] += 1
        return k

    # Protect hotkey patterns first  |cXXXXS|r  ->  single placeholder
    def hotkey_rep(m):
        k = new_key()
        tag_map[k] = m.group(0)
        return k
    text = HOTKEY_RE.sub(hotkey_rep, text)

    # Protect remaining individual tags
    def tag_rep(m):
        k = new_key()
        tag_map[k] = m.group(0)
        return k
    text = re.sub(r'\|c[0-9a-fA-F]{8}|\|r', tag_rep, text)
    return text, tag_map

def restore_tags(text, tag_map):
    for k, v in tag_map.items():
        text = text.replace(k, v)
    return text

def has_orphan_placeholders(text):
    return bool(re.search(r'@@T\d+@@', text))

# ══════════════════════════════════════════════════════════════════════════════
#  LANGUAGE DETECTION
# ══════════════════════════════════════════════════════════════════════════════
# Only unambiguously English words — excludes: may, no, is, general, can,
# must, or, for, fatal, base, local, etc. (also valid in Spanish).
_EN = re.compile(
    r'\b(the|and|but|our|you|we|are|was|were|have|has|that|this|'
    r'with|from|they|not|be|by|an|if|do|he|she|his|her|let|will|'
    r'would|could|should|might|shall|just|their|them|there|'
    r'then|than|these|those|only|even|still|been|had|did|get|got|'
    r'when|who|what|where|how|into|upon|about|above|after|'
    r'before|between|through|during|against|without|within|along|across|'
    r'once|very|over|under|until|while|since|though|already|again|'
    r'ever|never|always|soon|later|back|away|down|keep|stay|'
    r'give|take|make|come|see|know|look|want|need|find|tell|'
    r'ask|feel|try|leave|hold|turn|move|stand|lose|bring|'
    r'show|hear|run|fight|fall|push|send|march|attack|defend|prepare|'
    r'gather|watch|wait|follow|lead|serve|protect|survive)\b',
    re.I
)

# Unambiguous Spanish words — if any of these appear, it's likely Spanish
_ES_ANCHORS = re.compile(
    r'\b(los|las|una|unos|unas|del|también|pero|porque|cuando|como|'
    r'esta|esto|estos|estas|para|con|sin|sobre|entre|hacia|desde|'
    r'hasta|durante|después|antes|aunque|mientras|además|embargo|'
    r'debe|pueden|tiene|tienen|siendo|siendo|había|habrá|será|'
    r'nuestro|nuestra|vuestro|ellos|ellas|nosotros|ustedes)\b',
    re.I
)

def is_english(text):
    plain = re.sub(r'@@T\d+@@', '', strip_tags(text)).strip()
    if not plain:
        return False
    words = plain.split()
    if len(words) < 3:  # Too short to judge reliably
        return False
    # If strong Spanish markers are present, trust it's Spanish
    if _ES_ANCHORS.search(plain):
        return False
    en_ratio = len(_EN.findall(plain)) / len(words)
    return en_ratio > 0.30  # Raised threshold to reduce false positives

# ══════════════════════════════════════════════════════════════════════════════
#  SKIP FILTERS
# ══════════════════════════════════════════════════════════════════════════════
_NUM        = re.compile(r'^\s*[\d\s%.,]+\s*$')
_SINGLE_CHR = re.compile(r'^\s*[A-Za-z]\s*$')
_CODE_STR   = re.compile(r'^[A-Za-z0-9]{3,5}\d+$')

def _apply_glossary_direct(text, glossary):
    clean = strip_tags(text).strip()
    for mapping in [glossary.get("quest_keywords", {}),
                    glossary.get("units", {}),
                    glossary.get("factions", {}),
                    glossary.get("places", {}),
                    glossary.get("abilities", {})]:
        if clean in mapping:
            return text.replace(clean, mapping[clean])
    return None

def should_skip(text, glossary):
    s = text.strip()
    if not s:                       return True, "vacío",         text
    if _NUM.match(s):               return True, "número/código", text
    if _SINGLE_CHR.match(s):        return True, "letra hotkey",  text
    if _CODE_STR.match(s):          return True, "código interno",text
    if not strip_tags(s):           return True, "solo tags",     text
    d = _apply_glossary_direct(s, glossary)
    if d is not None:               return True, "glosario",      d
    proper = glossary.get("proper_nouns_keep", {})
    if s in proper:                 return True, "nombre propio", proper[s]
    return False, "", ""

# ══════════════════════════════════════════════════════════════════════════════
#  GLOSSARY PRE-PROCESSING  (applied to already-protected text)
# ══════════════════════════════════════════════════════════════════════════════
def preprocess_glossary(text, glossary):
    """Replace glossary terms in protected text.

    Iterates over ALL categories in the glossary dict dynamically, so
    user-added categories (e.g. 'objects', 'spells') are picked up
    automatically without any code changes.

    Longer terms are applied before shorter ones to avoid partial matches
    (e.g. 'Death Knight' before 'Knight').
    """
    result = text

    # Collect every entry from every category, sort longest-first globally
    all_entries = []
    for category, mapping in glossary.items():
        if not isinstance(mapping, dict):
            continue
        for en, es in mapping.items():
            if en and es and en != es:
                all_entries.append((en, es))

    # Sort longest term first to prevent shorter terms clobbering longer ones
    all_entries.sort(key=lambda x: -len(x[0]))

    for en, es in all_entries:
        pattern = r'(?<![A-Za-z])' + re.escape(en) + r'(?![A-Za-z])'
        result = re.sub(pattern, es, result)

    return result

# ══════════════════════════════════════════════════════════════════════════════
#  PROMPTS  — no examples, no conditions that cause hallucinations
# ══════════════════════════════════════════════════════════════════════════════
_BATCH_SYSTEM = """\
Eres un traductor de videojuegos especializado en Warcraft III para Latinoamérica.

FORMATO DE ENTRADA Y SALIDA:
Recibirás texto numerado con marcadores <<<N>>>. Responde con el mismo formato.
Cada bloque <<<N>>> es independiente. Traduce cada uno por separado.
No omitas ningún número. No agregues texto fuera de los marcadores.

REGLAS DE TRADUCCIÓN:
- Traduce del inglés al español latino. Todo debe quedar en español.
- Los marcadores @@T0@@, @@T1@@, etc. son formato interno. Cópialos exactamente donde están.
- Las variables %d, %s, %i deben copiarse exactamente.
- Nombres propios ya conocidos del lore no se traducen (Illidan, Arthas, Maiev, etc.)
- Algunos términos ya vendrán en español porque fueron pre-traducidos. Respétalos.
- Si el texto es muy corto (un nombre, una palabra), tradúcelo o cópialo según corresponda.
- Usa español latino natural. No uses "vosotros".\
"""

_SINGLE_SYSTEM = """\
Eres un traductor de videojuegos especializado en Warcraft III para Latinoamérica.

Traduce el texto que recibirás del inglés al español latino. 
Devuelve únicamente la traducción, sin explicaciones ni formato adicional.
Los marcadores @@T0@@, @@T1@@, etc. son formato interno — cópialos exactamente.
Las variables %d, %s deben copiarse exactamente.
Nombres propios del lore de Warcraft no se traducen.
Usa español latino natural. No uses "vosotros".\
"""

# ══════════════════════════════════════════════════════════════════════════════
#  LLM CALL  —  multi-provider dispatcher
# ══════════════════════════════════════════════════════════════════════════════
def _call_llm(user_text, system_text, model, temperature=0.1,
              provider="ollama", api_key=None, perf_opts=None):
    """Call the appropriate LLM provider and return the response string.

    provider: "ollama" | "anthropic" | "openai" | "gemini" | "deepseek"
    api_key:  required for all providers except ollama
    perf_opts: dict of ollama-specific options (ignored for API providers)
    """

    # ── Ollama (local) ────────────────────────────────────────────────────────
    if provider == "ollama":
        import ollama as _ollama
        opts = {"temperature": temperature, "top_p": 0.9, "repeat_penalty": 1.1}
        if perf_opts:
            opts.update(perf_opts)
        resp = _ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": system_text},
                {"role": "user",   "content": user_text}
            ],
            options=opts
        )
        r = resp["message"]["content"].strip()

    # ── Anthropic ─────────────────────────────────────────────────────────────
    elif provider == "anthropic":
        import anthropic as _anthropic
        client = _anthropic.Anthropic(api_key=api_key)
        resp = client.messages.create(
            model=model,
            max_tokens=1024,
            system=system_text,
            messages=[{"role": "user", "content": user_text}]
        )
        r = resp.content[0].text.strip()

    # ── OpenAI ────────────────────────────────────────────────────────────────
    elif provider == "openai":
        import openai as _openai
        client = _openai.OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_text},
                {"role": "user",   "content": user_text}
            ]
        )
        r = resp.choices[0].message.content.strip()

    # ── DeepSeek (OpenAI-compatible API) ─────────────────────────────────────
    elif provider == "deepseek":
        import openai as _openai
        client = _openai.OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        resp = client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_text},
                {"role": "user",   "content": user_text}
            ]
        )
        r = resp.choices[0].message.content.strip()

    # ── Gemini ────────────────────────────────────────────────────────────────
    elif provider == "gemini":
        import google.generativeai as _genai
        _genai.configure(api_key=api_key)
        gemini = _genai.GenerativeModel(
            model_name=model,
            system_instruction=system_text
        )
        resp = gemini.generate_content(user_text)
        r = resp.text.strip()

    else:
        raise ValueError(f"Proveedor desconocido: {provider}")

    # Strip surrounding quotes that some models add
    if r.startswith('"') and r.endswith('"'):
        r = r[1:-1]
    return r

# ══════════════════════════════════════════════════════════════════════════════
#  BATCH ENGINE
# ══════════════════════════════════════════════════════════════════════════════
BATCH_SIZE = 6
SEP_RE     = re.compile(r'<<<(\d+)>>>\s*(.*?)(?=<<<\d+>>>|$)', re.DOTALL)

def _build_batch_prompt(protected_texts):
    lines = []
    for i, text in enumerate(protected_texts, 1):
        safe = text.replace("\n", "\\n")
        lines.append(f"<<<{i}>>> {safe}")
    return "\n".join(lines)

def _parse_batch_response(response, count):
    results = {}
    for m in SEP_RE.finditer(response):
        idx  = int(m.group(1))
        text = m.group(2).strip()
        if 1 <= idx <= count:
            # Restore \n only if it looks like our escaped newline sentinel
            # (not part of a literal \\n the model may have written)
            results[idx] = re.sub(r'(?<!\\)\\n', '\n', text)
    return results

def _translate_batch(protected_texts, model, perf_opts=None,
                     provider="ollama", api_key=None):
    if not protected_texts:
        return []
    prompt   = _build_batch_prompt(protected_texts)
    response = _call_llm(prompt, _BATCH_SYSTEM, model,
                         temperature=0.1, provider=provider,
                         api_key=api_key, perf_opts=perf_opts)
    parsed   = _parse_batch_response(response, len(protected_texts))
    return [parsed.get(i + 1) for i in range(len(protected_texts))]

def _translate_single(text, model, glossary, perf_opts=None,
                      provider="ollama", api_key=None):
    # 1. Protect tags first
    protected, tag_map = protect_tags(text)
    # 2. Apply glossary to protected text
    protected = preprocess_glossary(protected, glossary)
    safe      = protected.replace("\n", "\\n")

    result = _call_llm(safe, _SINGLE_SYSTEM, model,
                       temperature=0.15, provider=provider,
                       api_key=api_key, perf_opts=perf_opts)
    result = re.sub(r'(?<!\\)\\n', '\n', result)

    # Retry if still English
    if is_english(strip_tags(result)):
        result2 = _call_llm(safe, _SINGLE_SYSTEM, model,
                            temperature=0.3, provider=provider,
                            api_key=api_key, perf_opts=perf_opts)
        result2 = re.sub(r'(?<!\\)\\n', '\n', result2)
        if not is_english(strip_tags(result2)):
            result = result2

    # Remove any stray <<<N>>> markers
    result = re.sub(r'<<<\d+>>>\s*', '', result).strip()

    result = restore_tags(result, tag_map)

    # Hallucination guard
    if text.strip().count("\n") + 2 < result.strip().count("\n"):
        return text
    return result

# ══════════════════════════════════════════════════════════════════════════════
#  MAIN PIPELINE
# ══════════════════════════════════════════════════════════════════════════════
def translate_wts(filepath, output_path, model="gemma2", perf_opts=None,
                  progress_cb=None, log_cb=None,
                  provider="ollama", api_key=None):
    """Translate a .wts file and write the result to output_path.

    All state (glossary, perf options) is local to this call, making it
    safe to call concurrently from multiple threads.

    provider: 'ollama' | 'anthropic' | 'openai' | 'gemini' | 'deepseek'
    api_key:  required for all providers except ollama
    """
    perf_opts = perf_opts or {}
    glossary  = load_glossary()
    blocks    = parse_wts(filepath)

    # Classify blocks
    to_translate = []
    n_skipped    = 0

    for i, b in enumerate(blocks):
        if b["empty"]:
            b["translated"] = b["text"]
            n_skipped += 1
            continue
        skip, reason, result = should_skip(b["text"], glossary)
        if skip:
            b["translated"] = result
            n_skipped += 1
            if log_cb:
                log_cb(f"[{b['id']}] [{reason}] {strip_tags(b['text']).strip()[:50]}")
        else:
            to_translate.append((i, b))

    total = len(to_translate)
    done  = 0
    stats = {"lote": 0, "retry": 0, "warn": 0}

    if log_cb:
        log_cb(f"\nArchivo: {len(blocks)} strings | {total} a traducir | {n_skipped} omitidos")
        log_cb(f"Modelo: {model} | Lote: {BATCH_SIZE} strings por llamada")
        log_cb("─" * 48)

    for batch_start in range(0, len(to_translate), BATCH_SIZE):
        batch = to_translate[batch_start : batch_start + BATCH_SIZE]

        # Protect tags FIRST, then apply glossary to protected text
        protected_list = []
        tag_map_list   = []

        for (_, b) in batch:
            prot, tm = protect_tags(b["text"])
            prot     = preprocess_glossary(prot, glossary)
            protected_list.append(prot)
            tag_map_list.append(tm)

        if log_cb:
            ids = ", ".join(str(b["id"]) for _, b in batch)
            log_cb(f"Lote [{batch_start+1}–{batch_start+len(batch)}] strings: {ids}")

        # LLM call
        try:
            translated_list = _translate_batch(
                protected_list, model, perf_opts,
                provider=provider, api_key=api_key)
        except Exception as e:
            if log_cb:
                log_cb(f"  !! Error en lote: {e} — reintentando uno a uno")
            translated_list = [None] * len(batch)

        # Process each result
        for pos, ((blk_i, b), tag_map) in enumerate(zip(batch, tag_map_list)):
            translated = translated_list[pos] if pos < len(translated_list) else None

            if translated is None:
                if log_cb:
                    log_cb(f"  [{b['id']}] Reintento individual...")
                try:
                    translated = _translate_single(
                        b["text"], model, glossary, perf_opts,
                        provider=provider, api_key=api_key)
                    stats["retry"] += 1
                except Exception as e2:
                    translated = b["text"]
                    stats["warn"] += 1
                    if log_cb:
                        log_cb(f"  !! Error STRING {b['id']}: {e2}")
            else:
                translated = restore_tags(translated, tag_map)
                translated = re.sub(r'<<<\d+>>>\s*', '', translated).strip()
                stats["lote"] += 1

            # Quality checks
            if has_orphan_placeholders(translated):
                translated = restore_tags(translated, tag_map)
                if has_orphan_placeholders(translated):
                    if log_cb:
                        log_cb(f"  ⚠ Tags sin restaurar — STRING {b['id']}")
                    stats["warn"] += 1

            if is_english(strip_tags(translated)):
                if log_cb:
                    preview = strip_tags(b["text"]).strip()[:45]
                    log_cb(f"  ⚠ Sin traducir — STRING {b['id']}: {preview}")
                stats["warn"] += 1

            orig_lines   = b["text"].strip().count("\n")
            result_lines = translated.strip().count("\n")
            if result_lines > orig_lines + 2:
                if log_cb:
                    log_cb(f"  ⚠ Alucinación — STRING {b['id']} revertido")
                translated = b["text"]
                stats["warn"] += 1

            b["translated"] = translated
            done += 1
            if progress_cb:
                progress_cb(done, total)

    output = build_wts(blocks)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(output)

    if log_cb:
        log_cb("─" * 48)
        log_cb(f"✓ Completado — {stats['lote']} en lote | "
               f"{stats['retry']} reintentados | "
               f"{stats['warn']} advertencias")
        log_cb(f"  Guardado en: {output_path}")

    return output_path
