import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import json
import os
import sys
from translator import translate_wts

def resource_path(relative):
    """Devuelve la ruta correcta tanto en desarrollo como compilado con PyInstaller."""
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Intentar cargar tkinterdnd2
try:
    from tkinterdnd2 import TkinterDnD, DND_FILES as _DND_FILES
    _DND_AVAILABLE = True
except ImportError:
    _DND_AVAILABLE = False

# ══════════════════════════════════════════════════════════════════════════════
#  PROVIDER CONFIG
# ══════════════════════════════════════════════════════════════════════════════
PROVIDERS = {
    "ollama":    {"label": "Ollama (local)",  "needs_key": False, "models": ["gemma2", "llama3", "mistral", "phi3"]},
    "anthropic": {"label": "Anthropic",       "needs_key": True,  "models": ["claude-haiku-4-5", "claude-sonnet-4-5"]},
    "openai":    {"label": "OpenAI",          "needs_key": True,  "models": ["gpt-4o-mini", "gpt-4o"]},
    "gemini":    {"label": "Gemini",          "needs_key": True,  "models": ["gemini-1.5-flash", "gemini-1.5-pro"]},
    "deepseek":  {"label": "DeepSeek",        "needs_key": True,  "models": ["deepseek-chat", "deepseek-reasoner"]},
}
PROVIDER_LABELS = [v["label"] for v in PROVIDERS.values()]
PROVIDER_KEYS   = list(PROVIDERS.keys())

def get_data_dir():
    """Writable data folder — works both in dev and when installed in Program Files.

    When running normally: %APPDATA%\WTS Translator\
    Fallback (non-Windows): ~/.wts_translator/
    """
    appdata = os.environ.get("APPDATA")
    if appdata:
        folder = os.path.join(appdata, "WTS Translator")
    else:
        folder = os.path.join(os.path.expanduser("~"), ".wts_translator")
    os.makedirs(folder, exist_ok=True)
    return folder

def get_config_path():
    return os.path.join(get_data_dir(), "config.json")

def load_config():
    try:
        with open(get_config_path(), "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_config(data):
    with open(get_config_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ══════════════════════════════════════════════════════════════════════════════
#  INTERNATIONALISATION  (ES / EN)
# ══════════════════════════════════════════════════════════════════════════════
STRINGS = {
    "es": {
        # Window & tabs
        "title":                "WTS Translator",
        "tab_translate":        "Traducir",
        "tab_glossary":         "Glosario",

        # Translate tab — file input
        "lbl_wts_file":         "Archivo .wts",
        "drop_hint":            "⬇   Arrastra tu archivo .wts aquí   o   haz clic en Examinar",
        "btn_browse":           "Examinar",
        "placeholder_source":   "Ruta del archivo fuente...",

        # Translate tab — output
        "lbl_output_folder":    "Carpeta de destino",
        "placeholder_output":   "Carpeta de destino...",

        # Translate tab — options
        "lbl_model":            "Modelo:",
        "lbl_performance":      "Rendimiento:",
        "perf_low":             "🐢  Bajo (CPU)",
        "perf_normal":          "⚡  Normal (GPU+CPU)",
        "perf_high":            "🚀  Alto (GPU máximo)",

        # Translate tab — buttons & progress
        "btn_translate":        "▶  Traducir",
        "btn_translating":      "⏳  Traduciendo...",
        "lbl_console":          "Consola",
        "btn_clear":            "Limpiar",
        "progress_starting":    "Iniciando...",
        "progress_done":        "✓ Completado",
        "progress_error":       "Error",

        # Glossary tab
        "lbl_glossary_editor":  "Editor de Glosario",
        "btn_save_glossary":    "💾  Guardar cambios",
        "btn_add_category":     "+ Categoría",
        "lbl_english":          "Inglés",
        "lbl_spanish":          "Español",
        "btn_add_entry":        "+ Añadir",
        "placeholder_en":       "Inglés",
        "placeholder_es":       "Español",
        "new_category_prompt":  "Nombre de la nueva categoría (en inglés, sin espacios):",
        "new_category_title":   "Nueva categoría",

        # Glossary sections
        "sec_factions":         "Facciones",
        "sec_units":            "Unidades",
        "sec_places":           "Lugares",
        "sec_titles":           "Rangos",
        "sec_abilities":        "Habilidades",
        "sec_quests":           "Misiones",
        "sec_proper":           "Nombres propios",

        # Dialogs & messages
        "warn_no_file_title":   "Sin archivo",
        "warn_no_file_msg":     "Selecciona un archivo .wts válido.",
        "warn_no_folder_title": "Sin carpeta",
        "warn_no_folder_msg":   "Selecciona la carpeta de destino.",
        "done_title":           "¡Listo!",
        "done_msg":             "Archivo guardado en:\n{path}",
        "error_title":          "Error",
        "error_ollama":         "{msg}\n\nAsegúrate de que Ollama esté corriendo.",
        "saved_title":          "Guardado",
        "saved_msg":            "Glosario guardado correctamente.",
        "save_error_msg":       "No se pudo guardar el glosario:\n{err}",

        # Log messages
        "log_file":             "Archivo: {path}",
        "log_models":           "Modelos: {models}",
        "log_dest":             "Destino: {path}",
        "log_dnd_unavailable":  "ℹ  Drag & drop no disponible (instala tkinterdnd2 para habilitarlo).",
        "log_dnd_error":        "⚠  Drag & drop: error al registrar ({err})",

        # Config tab
        "tab_config":           "Configuración",
        "cfg_provider":         "Proveedor de IA",
        "cfg_provider_lbl":     "Proveedor:",
        "cfg_model_lbl":        "Modelo:",
        "cfg_apikey_lbl":       "API Key:",
        "cfg_apikey_ph":        "Ingresá tu API Key...",
        "cfg_apikey_show":      "👁",
        "cfg_test_btn":         "🔌  Probar conexión",
        "cfg_test_ok":          "✓ Conexión exitosa — modelo: {model}",
        "cfg_test_fail":        "✗ Error: {err}",
        "cfg_test_running":     "Probando...",
        "cfg_save_btn":         "💾  Guardar configuración",
        "cfg_saved":            "Configuración guardada.",
        "cfg_language":         "Idioma de la interfaz",
        "cfg_theme":            "Tema",
        "cfg_theme_dark":       "Oscuro",
        "cfg_theme_light":      "Claro",
        "cfg_theme_system":     "Sistema",
        "cfg_about":            "Acerca de",
        "cfg_about_text":       "WTS Translator v1.0.0\nDesarrollado por Mateo Neufeld (SoyMante)\nAsistencia: Claude (Anthropic)\ngithub.com/ItsMante/wts-translator",
        "cfg_ollama_note":      "ℹ  Ollama no requiere API Key — corre localmente en tu PC.",
        "cfg_key_needed":       "⚠  Este proveedor requiere una API Key para funcionar.",
    },

    "en": {
        # Window & tabs
        "title":                "WTS Translator",
        "tab_translate":        "Translate",
        "tab_glossary":         "Glossary",

        # Translate tab — file input
        "lbl_wts_file":         ".wts File",
        "drop_hint":            "⬇   Drop your .wts file here   or   click Browse",
        "btn_browse":           "Browse",
        "placeholder_source":   "Source file path...",

        # Translate tab — output
        "lbl_output_folder":    "Output folder",
        "placeholder_output":   "Output folder...",

        # Translate tab — options
        "lbl_model":            "Model:",
        "lbl_performance":      "Performance:",
        "perf_low":             "🐢  Low (CPU)",
        "perf_normal":          "⚡  Normal (GPU+CPU)",
        "perf_high":            "🚀  High (max GPU)",

        # Translate tab — buttons & progress
        "btn_translate":        "▶  Translate",
        "btn_translating":      "⏳  Translating...",
        "lbl_console":          "Console",
        "btn_clear":            "Clear",
        "progress_starting":    "Starting...",
        "progress_done":        "✓ Done",
        "progress_error":       "Error",

        # Glossary tab
        "lbl_glossary_editor":  "Glossary Editor",
        "btn_save_glossary":    "💾  Save changes",
        "btn_add_category":     "+ Category",
        "lbl_english":          "English",
        "lbl_spanish":          "Spanish",
        "btn_add_entry":        "+ Add",
        "placeholder_en":       "English",
        "placeholder_es":       "Spanish",
        "new_category_prompt":  "New category name (no spaces):",
        "new_category_title":   "New category",

        # Glossary sections
        "sec_factions":         "Factions",
        "sec_units":            "Units",
        "sec_places":           "Places",
        "sec_titles":           "Ranks",
        "sec_abilities":        "Abilities",
        "sec_quests":           "Quests",
        "sec_proper":           "Proper nouns",

        # Dialogs & messages
        "warn_no_file_title":   "No file",
        "warn_no_file_msg":     "Please select a valid .wts file.",
        "warn_no_folder_title": "No folder",
        "warn_no_folder_msg":   "Please select an output folder.",
        "done_title":           "Done!",
        "done_msg":             "File saved to:\n{path}",
        "error_title":          "Error",
        "error_ollama":         "{msg}\n\nMake sure Ollama is running.",
        "saved_title":          "Saved",
        "saved_msg":            "Glossary saved successfully.",
        "save_error_msg":       "Could not save glossary:\n{err}",

        # Log messages
        "log_file":             "File: {path}",
        "log_models":           "Models: {models}",
        "log_dest":             "Destination: {path}",
        "log_dnd_unavailable":  "ℹ  Drag & drop unavailable (install tkinterdnd2 to enable it).",
        "log_dnd_error":        "⚠  Drag & drop: registration error ({err})",

        # Config tab
        "tab_config":           "Settings",
        "cfg_provider":         "AI Provider",
        "cfg_provider_lbl":     "Provider:",
        "cfg_model_lbl":        "Model:",
        "cfg_apikey_lbl":       "API Key:",
        "cfg_apikey_ph":        "Enter your API Key...",
        "cfg_apikey_show":      "👁",
        "cfg_test_btn":         "🔌  Test connection",
        "cfg_test_ok":          "✓ Connection successful — model: {model}",
        "cfg_test_fail":        "✗ Error: {err}",
        "cfg_test_running":     "Testing...",
        "cfg_save_btn":         "💾  Save settings",
        "cfg_saved":            "Settings saved.",
        "cfg_language":         "Interface language",
        "cfg_theme":            "Theme",
        "cfg_theme_dark":       "Dark",
        "cfg_theme_light":      "Light",
        "cfg_theme_system":     "System",
        "cfg_about":            "About",
        "cfg_about_text":       "WTS Translator v1.0.0\nDeveloped by Mateo Neufeld (SoyMante)\nAssistance: Claude (Anthropic)\ngithub.com/ItsMante/wts-translator",
        "cfg_ollama_note":      "ℹ  Ollama requires no API Key — it runs locally on your PC.",
        "cfg_key_needed":       "⚠  This provider requires an API Key to work.",
    },
}

# Perf profile keys are internal — labels come from STRINGS
_PERF_OPTIONS = {
    "low":    {"num_gpu": 0,  "num_thread": 4},
    "normal": {"num_gpu": 1,  "num_thread": 8},
    "high":   {"num_gpu": 99, "num_thread": 8},
}

# Glossary section keys -> STRINGS key for label
GLOSSARY_SECTION_KEYS = [
    ("factions",          "sec_factions"),
    ("units",             "sec_units"),
    ("places",            "sec_places"),
    ("titles_and_ranks",  "sec_titles"),
    ("abilities",         "sec_abilities"),
    ("quest_keywords",    "sec_quests"),
    ("proper_nouns_keep", "sec_proper"),
]

def get_ollama_models():
    try:
        models = ollama.list()
        names  = [m["model"].replace(":latest", "") for m in models.get("models", [])]
        return names if names else ["gemma2"]
    except Exception:
        return ["gemma2"]

def get_glossary_path():
    """Glossary lives in AppData so it can be written without admin rights.

    On first run, copies the bundled default glossary.json to AppData
    so the user starts with the pre-filled terms.
    """
    dest = os.path.join(get_data_dir(), "glossary.json")
    if not os.path.exists(dest):
        # Copy the read-only bundled default to the writable AppData folder
        bundled = resource_path("glossary.json")
        if os.path.exists(bundled):
            import shutil
            shutil.copy2(bundled, dest)
    return dest

def load_glossary_file():
    with open(get_glossary_path(), "r", encoding="utf-8") as f:
        return json.load(f)

def save_glossary_file(data):
    with open(get_glossary_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ══════════════════════════════════════════════════════════════════════════════
class WTSTranslatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Language state — default to Spanish
        self._lang = "es"

        # Icon — use Pillow for reliable PNG support in compiled executables.
        # Falls back to tk.PhotoImage if Pillow is not available.
        try:
            from PIL import Image, ImageTk
            img  = Image.open(resource_path("logo.png"))
            icon = ImageTk.PhotoImage(img)
            self.iconphoto(True, icon)
            self._icon_ref = icon  # prevent garbage collection
        except Exception:
            try:
                icon = tk.PhotoImage(file=resource_path("logo.png"))
                self.iconphoto(True, icon)
                self._icon_ref = icon
            except Exception:
                pass

        self.source_path = tk.StringVar()
        self.output_dir  = tk.StringVar()
        self._perf_key   = "normal"   # internal key, independent of display language
        self.is_running  = False

        # Load saved config
        cfg = load_config()
        self._provider   = cfg.get("provider", "ollama")  # internal provider key
        self._api_key    = cfg.get("api_key", "")
        self._lang       = cfg.get("lang", self._lang)

        self.available_models = (
            get_ollama_models() if self._provider == "ollama"
            else PROVIDERS[self._provider]["models"]
        )
        saved_model = cfg.get("model", "")
        self.model_var = tk.StringVar(
            value=saved_model if saved_model else
            (self.available_models[0] if self.available_models else "gemma2")
        )

        self._build_ui()
        self._apply_language()
        self._setup_drag_drop()

    # ── Localisation shortcut ─────────────────────────────────────────────────
    def _(self, key, **kwargs):
        s = STRINGS[self._lang].get(key, key)
        return s.format(**kwargs) if kwargs else s

    # ══════════════════════════════════════════════════════════════════════════
    #  LANGUAGE TOGGLE
    # ══════════════════════════════════════════════════════════════════════════
    def _apply_language(self):
        s = self._

        # Window title
        self.title(s("title"))

        # ── Main tabs: CTkTabview has no rename() — rebuild them ───────────
        # Save which tab is active (translate vs glossary) to restore it
        self._rebuild_main_tabs()

        # ── Translate tab ──────────────────────────────────────────────────
        self.lbl_wts_file.configure(text=s("lbl_wts_file"))
        if not self.source_path.get():
            self.drop_label.configure(text=s("drop_hint"))
        self.browse_src_btn.configure(text=s("btn_browse"))
        self.src_entry.configure(placeholder_text=s("placeholder_source"))

        self.lbl_output_folder.configure(text=s("lbl_output_folder"))
        self.out_entry.configure(placeholder_text=s("placeholder_output"))
        self.browse_out_btn.configure(text=s("btn_browse"))

        self.lbl_model.configure(text=s("lbl_model"))
        self.lbl_performance.configure(text=s("lbl_performance"))

        perf_labels = [s("perf_low"), s("perf_normal"), s("perf_high")]
        perf_keys   = ["low", "normal", "high"]
        self.perf_menu.configure(values=perf_labels)
        self.perf_var.set(perf_labels[perf_keys.index(self._perf_key)])

        if not self.is_running:
            self.translate_btn.configure(text=s("btn_translate"))
        self.lbl_console.configure(text=s("lbl_console"))
        self.clear_btn.configure(text=s("btn_clear"))

        # ── Glossary tab ───────────────────────────────────────────────────
        self.lbl_glossary_editor.configure(text=s("lbl_glossary_editor"))
        self.save_glossary_btn.configure(text=s("btn_save_glossary"))
        self.add_category_btn.configure(text=s("btn_add_category"))

        # Rebuild glossary sub-tabs with new language labels
        self._rebuild_glossary_tabs()

        for key, widgets in self._gloss_section_widgets.items():
            widgets["lbl_en"].configure(text=s("lbl_english"))
            widgets["lbl_es"].configure(text=s("lbl_spanish"))
            widgets["btn_add"].configure(text=s("btn_add_entry"))

    def _rebuild_main_tabs(self):
        """Update main tab labels in the current language.

        CTkTabview has no rename() API, so we reach into its internal
        _tab_dict and update the CTkLabel text directly — the only reliable
        approach that does not require destroying/reparenting widgets.
        """
        s = self._
        # _tab_dict maps tab-name -> CTkFrame; the segmented button that
        # shows the tab label is a separate widget we can update via
        # the tabview's internal segmented button.
        try:
            seg = self.tabs._segmented_button
            # seg._buttons_dict maps current label text -> CTkButton
            old_keys = list(seg._buttons_dict.keys())
            # We always add tabs in order: translate first, glossary second
            new_labels = [s("tab_translate"), s("tab_glossary"), s("tab_config")]
            for old_key, new_label in zip(old_keys, new_labels):
                if old_key != new_label:
                    btn = seg._buttons_dict.pop(old_key)
                    btn.configure(text=new_label)
                    seg._buttons_dict[new_label] = btn
                    # Also update CTkTabview's own _tab_dict
                    frame = self.tabs._tab_dict.pop(old_key)
                    self.tabs._tab_dict[new_label] = frame
            # Refresh the segmented button display
            seg.configure(values=new_labels)
            seg.set(s("tab_translate"))
        except Exception:
            pass  # If internal API changed, silently skip — labels just won't update

    def _rebuild_glossary_tabs(self):
        """Update glossary sub-tab labels using CTkTabview internal API.
        Same approach as _rebuild_main_tabs — no widget destruction needed."""
        s = self._
        try:
            seg = self.gloss_tabs._segmented_button
            for key, str_key in GLOSSARY_SECTION_KEYS:
                old_label = self._gloss_tab_labels.get(key)
                new_label = s(str_key)
                if old_label and old_label != new_label and old_label in seg._buttons_dict:
                    btn = seg._buttons_dict.pop(old_label)
                    btn.configure(text=new_label)
                    seg._buttons_dict[new_label] = btn
                    frame = self.gloss_tabs._tab_dict.pop(old_label)
                    self.gloss_tabs._tab_dict[new_label] = frame
                    self._gloss_tab_labels[key] = new_label
            # Refresh segmented button with updated labels
            known_keys = {k for k, _ in GLOSSARY_SECTION_KEYS}
            all_labels = (
                [self._gloss_tab_labels.get(k, s(sk)) for k, sk in GLOSSARY_SECTION_KEYS] +
                [lbl for k, lbl in self._gloss_tab_labels.items() if k not in known_keys]
            )
            seg.configure(values=all_labels)
        except Exception:
            pass

    # ══════════════════════════════════════════════════════════════════════════
    #  UI BUILD
    # ══════════════════════════════════════════════════════════════════════════
    def _build_ui(self):
        self.geometry("860x700")
        self.minsize(760, 600)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main tab view — tabs named in current language from the start
        self.tabs = ctk.CTkTabview(self)
        self.tabs.grid(row=0, column=0, sticky="nsew", padx=12, pady=(8, 12))
        for key in ("tab_translate", "tab_glossary", "tab_config"):
            self.tabs.add(STRINGS[self._lang][key])

        def _make_content(tab_key):
            f = ctk.CTkFrame(self.tabs.tab(STRINGS[self._lang][tab_key]),
                             fg_color="transparent")
            f.grid(row=0, column=0, sticky="nsew")
            self.tabs.tab(STRINGS[self._lang][tab_key]).grid_columnconfigure(0, weight=1)
            self.tabs.tab(STRINGS[self._lang][tab_key]).grid_rowconfigure(0, weight=1)
            return f

        self._translate_content = _make_content("tab_translate")
        self._glossary_content  = _make_content("tab_glossary")
        self._config_content    = _make_content("tab_config")

        self._build_translate_tab(self._translate_content)
        self._build_glossary_tab(self._glossary_content)
        self._build_config_tab(self._config_content)

    # ── Translate tab ──────────────────────────────────────────────────────
    def _build_translate_tab(self, tab):
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(5, weight=1)

        # File input
        src = ctk.CTkFrame(tab, fg_color="transparent")
        src.grid(row=0, column=0, sticky="ew", pady=(8, 0))
        src.grid_columnconfigure(0, weight=1)

        self.lbl_wts_file = ctk.CTkLabel(src, text="", font=ctk.CTkFont(weight="bold"))
        self.lbl_wts_file.grid(row=0, column=0, columnspan=2, sticky="w",
                                padx=12, pady=(8, 4))

        self.drop_label = ctk.CTkLabel(
            src, text="", text_color="gray", height=50, corner_radius=6,
            fg_color=("gray88", "gray22"), cursor="hand2")
        self.drop_label.grid(row=1, column=0, sticky="ew", padx=(12, 6), pady=(0, 4))
        self.drop_label.bind("<Button-1>", lambda e: self._browse_source())

        self.browse_src_btn = ctk.CTkButton(src, text="", width=100,
                                            command=self._browse_source)
        self.browse_src_btn.grid(row=1, column=1, padx=(4, 12), pady=(0, 4))

        self.src_entry = ctk.CTkEntry(src, textvariable=self.source_path,
                                      placeholder_text="", state="readonly")
        self.src_entry.grid(row=2, column=0, columnspan=2, sticky="ew",
                            padx=12, pady=(0, 10))

        # Output folder
        out = ctk.CTkFrame(tab, fg_color="transparent")
        out.grid(row=1, column=0, sticky="ew", pady=(6, 0))
        out.grid_columnconfigure(0, weight=1)

        self.lbl_output_folder = ctk.CTkLabel(out, text="", font=ctk.CTkFont(weight="bold"))
        self.lbl_output_folder.grid(row=0, column=0, columnspan=2, sticky="w",
                                    padx=12, pady=(8, 4))

        self.out_entry = ctk.CTkEntry(out, textvariable=self.output_dir, placeholder_text="")
        self.out_entry.grid(row=1, column=0, sticky="ew", padx=(12, 6), pady=(0, 10))

        self.browse_out_btn = ctk.CTkButton(out, text="", width=100,
                                            command=self._browse_output)
        self.browse_out_btn.grid(row=1, column=1, padx=(4, 12), pady=(0, 10))

        # Options
        opt = ctk.CTkFrame(tab, fg_color="transparent")
        opt.grid(row=2, column=0, sticky="ew", pady=(6, 0))
        opt.grid_columnconfigure(1, weight=1)
        opt.grid_columnconfigure(3, weight=1)

        self.lbl_model = ctk.CTkLabel(opt, text="", font=ctk.CTkFont(weight="bold"))
        self.lbl_model.grid(row=0, column=0, sticky="w", padx=(12, 6), pady=10)

        self.model_menu = ctk.CTkOptionMenu(opt, variable=self.model_var,
                                            values=self.available_models, width=180)
        self.model_menu.grid(row=0, column=1, sticky="w", padx=(0, 12), pady=10)

        ctk.CTkButton(opt, text="↺", width=32,
                      command=self._refresh_models).grid(row=0, column=2,
                                                         padx=(0, 16), pady=10)

        self.lbl_performance = ctk.CTkLabel(opt, text="", font=ctk.CTkFont(weight="bold"))
        self.lbl_performance.grid(row=0, column=3, sticky="w", padx=(0, 6), pady=10)

        self.perf_var = tk.StringVar()
        self.perf_menu = ctk.CTkOptionMenu(opt, variable=self.perf_var,
                                           values=[], width=210,
                                           command=self._on_perf_change)
        self.perf_menu.grid(row=0, column=4, sticky="w", padx=(0, 12), pady=10)

        # Translate button
        self.translate_btn = ctk.CTkButton(
            tab, text="", height=38,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._start_translation)
        self.translate_btn.grid(row=3, column=0, sticky="ew", pady=(8, 0))

        # Progress
        prog = ctk.CTkFrame(tab, fg_color="transparent")
        prog.grid(row=4, column=0, sticky="ew", pady=(8, 0))
        prog.grid_columnconfigure(0, weight=1)

        self.progress_bar = ctk.CTkProgressBar(prog, height=14)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=0, column=0, sticky="ew")

        self.progress_label = ctk.CTkLabel(prog, text="", text_color="gray",
                                           font=ctk.CTkFont(size=12))
        self.progress_label.grid(row=1, column=0, sticky="w", pady=(2, 0))

        # Console
        con = ctk.CTkFrame(tab, fg_color="transparent")
        con.grid(row=5, column=0, sticky="nsew", pady=(8, 0))
        con.grid_columnconfigure(0, weight=1)
        con.grid_rowconfigure(1, weight=1)
        tab.grid_rowconfigure(5, weight=1)

        hrow = ctk.CTkFrame(con, fg_color="transparent")
        hrow.grid(row=0, column=0, sticky="ew", padx=10, pady=(6, 2))

        self.lbl_console = ctk.CTkLabel(hrow, text="", font=ctk.CTkFont(weight="bold"))
        self.lbl_console.pack(side="left")

        self.clear_btn = ctk.CTkButton(hrow, text="", width=64, height=22,
                                       font=ctk.CTkFont(size=11),
                                       command=self._clear_console)
        self.clear_btn.pack(side="right")

        self.console = ctk.CTkTextbox(con, font=ctk.CTkFont(family="Consolas", size=12),
                                      wrap="word", state="disabled")
        self.console.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))

    # ── Glossary tab ───────────────────────────────────────────────────────
    def _build_glossary_tab(self, tab):
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)

        top = ctk.CTkFrame(tab, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", pady=(4, 6))

        self.lbl_glossary_editor = ctk.CTkLabel(top, text="",
                                                 font=ctk.CTkFont(size=15, weight="bold"))
        self.lbl_glossary_editor.pack(side="left")

        self.save_glossary_btn = ctk.CTkButton(top, text="", width=150, height=30,
                                               command=self._save_glossary)
        self.save_glossary_btn.pack(side="right", padx=(8, 0))

        self.add_category_btn = ctk.CTkButton(top, text="", width=120, height=30,
                                              command=self._add_category)
        self.add_category_btn.pack(side="right")

        self.gloss_tabs = ctk.CTkTabview(self._glossary_content)
        self.gloss_tabs.grid(row=1, column=0, sticky="nsew")

        self._gloss_tab_labels:      dict = {}
        self._gloss_section_widgets: dict = {}
        self._gloss_data:            dict = {}
        self._gloss_frames:          dict = {}

        self._load_glossary_ui()

    def _load_glossary_ui(self):
        data = load_glossary_file()

        for key, str_key in GLOSSARY_SECTION_KEYS:
            label = self._(str_key)
            try:
                self.gloss_tabs.delete(label)
            except Exception:
                pass

        self._gloss_data            = {}
        self._gloss_frames          = {}
        self._gloss_tab_labels      = {}
        self._gloss_section_widgets = {}

        for key, str_key in GLOSSARY_SECTION_KEYS:
            if key not in data:
                data[key] = {}
            self._build_section_tab(key, self._(str_key), data[key])

        known_keys = {k for k, _ in GLOSSARY_SECTION_KEYS}
        for key, entries in data.items():
            if key not in known_keys and isinstance(entries, dict):
                self._build_section_tab(key, key, entries)

    def _build_section_tab(self, key, label, entries):
        self.gloss_tabs.add(label)
        self._gloss_tab_labels[key] = label

        tab = self.gloss_tabs.tab(label)
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)

        hdr = ctk.CTkFrame(tab, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", pady=(4, 2))

        lbl_en = ctk.CTkLabel(hdr, text=self._("lbl_english"),
                               font=ctk.CTkFont(weight="bold"), width=220)
        lbl_en.pack(side="left", padx=(8, 0))

        lbl_es = ctk.CTkLabel(hdr, text=self._("lbl_spanish"),
                               font=ctk.CTkFont(weight="bold"))
        lbl_es.pack(side="left", padx=(12, 0))

        btn_add = ctk.CTkButton(hdr, text=self._("btn_add_entry"), width=80, height=26,
                                command=lambda k=key: self._add_entry(k))
        btn_add.pack(side="right", padx=(0, 8))

        self._gloss_section_widgets[key] = {
            "lbl_en": lbl_en, "lbl_es": lbl_es, "btn_add": btn_add
        }

        scroll = ctk.CTkScrollableFrame(tab)
        scroll.grid(row=1, column=0, sticky="nsew")
        scroll.grid_columnconfigure(1, weight=1)

        self._gloss_frames[key] = scroll
        self._gloss_data[key]   = []

        for en_text, es_text in entries.items():
            self._add_entry_row(key, scroll, en_text, es_text)

    def _add_entry_row(self, key, scroll, en_text="", es_text=""):
        row_idx = len(self._gloss_data[key])
        en_var  = tk.StringVar(value=en_text)
        es_var  = tk.StringVar(value=es_text)

        row_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        row_frame.grid(row=row_idx, column=0, columnspan=3, sticky="ew", padx=4, pady=2)
        row_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkEntry(row_frame, textvariable=en_var, width=210,
                     placeholder_text=self._("placeholder_en")).grid(
            row=0, column=0, padx=(0, 6))
        ctk.CTkEntry(row_frame, textvariable=es_var,
                     placeholder_text=self._("placeholder_es")).grid(
            row=0, column=1, sticky="ew", padx=(0, 6))
        ctk.CTkButton(
            row_frame, text="✕", width=30, height=28,
            fg_color="transparent", border_width=1,
            hover_color=("gray75", "gray30"),
            command=lambda rf=row_frame, k=key, rv=(en_var, es_var):
                self._delete_entry(rf, k, rv)
        ).grid(row=0, column=2)

        self._gloss_data[key].append((en_var, es_var))

    def _add_entry(self, key):
        scroll = self._gloss_frames.get(key)
        if scroll:
            self._add_entry_row(key, scroll)

    def _delete_entry(self, row_frame, key, row_vars):
        row_frame.destroy()
        try:
            self._gloss_data[key].remove(row_vars)
        except ValueError:
            pass

    def _add_category(self):
        dialog = ctk.CTkInputDialog(
            text=self._("new_category_prompt"),
            title=self._("new_category_title"))
        name = dialog.get_input()
        if name:
            name = name.strip().replace(" ", "_")
            if name and name not in self._gloss_frames:
                self._build_section_tab(name, name, {})
                self.gloss_tabs.set(name)

    def _save_glossary(self):
        try:
            data = load_glossary_file()
            for key in self._gloss_data:
                data[key] = {
                    ev.get().strip(): sv.get().strip()
                    for ev, sv in self._gloss_data[key]
                    if ev.get().strip()
                }
            save_glossary_file(data)
            messagebox.showinfo(self._("saved_title"), self._("saved_msg"))
        except Exception as e:
            messagebox.showerror(self._("error_title"),
                                 self._("save_error_msg", err=e))

    # ══════════════════════════════════════════════════════════════════════════
    #  CONFIG TAB
    # ══════════════════════════════════════════════════════════════════════════
    def _build_config_tab(self, tab):
        tab.grid_columnconfigure(0, weight=1)

        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        scroll.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        def section(parent, row, str_key):
            lbl = ctk.CTkLabel(parent, text=self._(str_key),
                               font=ctk.CTkFont(size=14, weight="bold"),
                               fg_color="transparent")
            lbl.grid(row=row, column=0, sticky="w", padx=16, pady=(18, 4))
            sep = ctk.CTkFrame(parent, height=1, fg_color=("gray75", "gray35"))
            sep.grid(row=row+1, column=0, sticky="ew", padx=16, pady=(0, 8))
            return lbl, sep

        # ── AI Provider ───────────────────────────────────────────────────────
        self._cfg_provider_lbl, _ = section(scroll, 0, "cfg_provider")

        prow = ctk.CTkFrame(scroll, fg_color="transparent")
        prow.grid(row=2, column=0, sticky="ew", padx=16, pady=4)
        prow.grid_columnconfigure(1, weight=1)

        self._cfg_lbl_provider = ctk.CTkLabel(prow, text=self._("cfg_provider_lbl"), width=90)
        self._cfg_lbl_provider.grid(row=0, column=0, sticky="w")

        self._cfg_provider_var = tk.StringVar(
            value=PROVIDERS[self._provider]["label"])
        self._cfg_provider_menu = ctk.CTkOptionMenu(
            prow, variable=self._cfg_provider_var,
            values=PROVIDER_LABELS, width=200,
            command=self._on_provider_change)
        self._cfg_provider_menu.grid(row=0, column=1, sticky="w", padx=(8, 0))

        mrow = ctk.CTkFrame(scroll, fg_color="transparent")
        mrow.grid(row=3, column=0, sticky="ew", padx=16, pady=4)
        mrow.grid_columnconfigure(1, weight=1)

        self._cfg_lbl_model = ctk.CTkLabel(mrow, text=self._("cfg_model_lbl"), width=90)
        self._cfg_lbl_model.grid(row=0, column=0, sticky="w")

        self._cfg_model_menu = ctk.CTkOptionMenu(
            mrow, variable=self.model_var,
            values=self.available_models, width=200)
        self._cfg_model_menu.grid(row=0, column=1, sticky="w", padx=(8, 0))

        krow = ctk.CTkFrame(scroll, fg_color="transparent")
        krow.grid(row=4, column=0, sticky="ew", padx=16, pady=4)
        krow.grid_columnconfigure(1, weight=1)

        self._cfg_lbl_apikey = ctk.CTkLabel(krow, text=self._("cfg_apikey_lbl"), width=90)
        self._cfg_lbl_apikey.grid(row=0, column=0, sticky="w")

        self._cfg_apikey_var = tk.StringVar(value=self._api_key)
        self._cfg_apikey_entry = ctk.CTkEntry(
            krow, textvariable=self._cfg_apikey_var,
            placeholder_text=self._("cfg_apikey_ph"),
            show="*", width=320)
        self._cfg_apikey_entry.grid(row=0, column=1, sticky="ew", padx=(8, 4))

        self._cfg_apikey_show_btn = ctk.CTkButton(
            krow, text=self._("cfg_apikey_show"), width=32, height=28,
            fg_color="transparent", border_width=1,
            command=self._toggle_apikey_visibility)
        self._cfg_apikey_show_btn.grid(row=0, column=2, padx=(0, 0))

        # Note about ollama / api key requirement
        self._cfg_note = ctk.CTkLabel(
            scroll, text=self._("cfg_ollama_note"),
            text_color="gray", font=ctk.CTkFont(size=12),
            fg_color="transparent", wraplength=500, justify="left")
        self._cfg_note.grid(row=5, column=0, sticky="w", padx=16, pady=(2, 4))
        self._update_provider_ui()

        # Test + Save buttons
        brow = ctk.CTkFrame(scroll, fg_color="transparent")
        brow.grid(row=6, column=0, sticky="w", padx=16, pady=(6, 4))

        self._cfg_test_btn = ctk.CTkButton(
            brow, text=self._("cfg_test_btn"), width=180,
            command=self._test_connection)
        self._cfg_test_btn.pack(side="left", padx=(0, 10))

        self._cfg_save_btn = ctk.CTkButton(
            brow, text=self._("cfg_save_btn"), width=180,
            command=self._save_config)
        self._cfg_save_btn.pack(side="left")

        self._cfg_status = ctk.CTkLabel(
            scroll, text="", font=ctk.CTkFont(size=12),
            fg_color="transparent", wraplength=520, justify="left")
        self._cfg_status.grid(row=7, column=0, sticky="w", padx=16, pady=(2, 4))

        # ── Language ─────────────────────────────────────────────────────────
        self._cfg_lang_lbl, _ = section(scroll, 8, "cfg_language")

        lang_row = ctk.CTkFrame(scroll, fg_color="transparent")
        lang_row.grid(row=10, column=0, sticky="w", padx=16, pady=4)

        self._cfg_lang_es_btn = ctk.CTkButton(
            lang_row, text="🇦🇷  Español", width=140,
            command=lambda: self._set_language("es"))
        self._cfg_lang_es_btn.pack(side="left", padx=(0, 8))

        self._cfg_lang_en_btn = ctk.CTkButton(
            lang_row, text="🇬🇧  English", width=140,
            command=lambda: self._set_language("en"))
        self._cfg_lang_en_btn.pack(side="left")

        # ── Theme ─────────────────────────────────────────────────────────────
        self._cfg_theme_lbl, _ = section(scroll, 11, "cfg_theme")

        theme_row = ctk.CTkFrame(scroll, fg_color="transparent")
        theme_row.grid(row=13, column=0, sticky="w", padx=16, pady=4)

        for theme, str_key in (("Dark", "cfg_theme_dark"),
                               ("Light", "cfg_theme_light"),
                               ("System", "cfg_theme_system")):
            btn = ctk.CTkButton(
                theme_row, text=self._(str_key), width=110,
                command=lambda t=theme: ctk.set_appearance_mode(t))
            btn.pack(side="left", padx=(0, 8))

        # ── About ─────────────────────────────────────────────────────────────
        self._cfg_about_lbl, _ = section(scroll, 14, "cfg_about")

        self._cfg_about_text = ctk.CTkLabel(
            scroll, text=self._("cfg_about_text"),
            justify="left", font=ctk.CTkFont(size=12),
            fg_color="transparent", wraplength=520)
        self._cfg_about_text.grid(row=16, column=0, sticky="w", padx=16, pady=(4, 16))

    def _on_provider_change(self, label):
        for key, info in PROVIDERS.items():
            if info["label"] == label:
                self._provider = key
                break
        models = (
            get_ollama_models() if self._provider == "ollama"
            else PROVIDERS[self._provider]["models"]
        )
        self.available_models = models
        self._cfg_model_menu.configure(values=models)
        self.model_var.set(models[0] if models else "")
        self._update_provider_ui()

    def _update_provider_ui(self):
        needs_key = PROVIDERS[self._provider]["needs_key"]
        state = "normal" if needs_key else "disabled"
        self._cfg_apikey_entry.configure(state=state)
        self._cfg_apikey_show_btn.configure(state=state)
        note_key = "cfg_key_needed" if needs_key else "cfg_ollama_note"
        self._cfg_note.configure(text=self._(note_key))

    def _toggle_apikey_visibility(self):
        current = self._cfg_apikey_entry.cget("show")
        self._cfg_apikey_entry.configure(show="" if current == "*" else "*")

    def _test_connection(self):
        self._cfg_status.configure(text=self._("cfg_test_running"), text_color="gray")
        self._cfg_test_btn.configure(state="disabled")
        provider = self._provider
        api_key  = self._cfg_apikey_var.get().strip()
        model    = self.model_var.get().strip()

        def run():
            try:
                from translator import _call_llm, _SINGLE_SYSTEM
                result = _call_llm(
                    "Hello", _SINGLE_SYSTEM, model,
                    provider=provider, api_key=api_key or None)
                msg = self._("cfg_test_ok", model=model)
                self.after(0, lambda: self._cfg_status.configure(
                    text=msg, text_color="green"))
            except Exception as e:
                msg = self._("cfg_test_fail", err=str(e)[:120])
                self.after(0, lambda: self._cfg_status.configure(
                    text=msg, text_color="red"))
            finally:
                self.after(0, lambda: self._cfg_test_btn.configure(state="normal"))

        threading.Thread(target=run, daemon=True).start()

    def _save_config(self):
        cfg = load_config()
        cfg["provider"] = self._provider
        cfg["api_key"]  = self._cfg_apikey_var.get().strip()
        cfg["model"]    = self.model_var.get().strip()
        cfg["lang"]     = self._lang
        save_config(cfg)
        self._api_key = cfg["api_key"]
        self._cfg_status.configure(
            text=self._("cfg_saved"), text_color="green")

    def _set_language(self, lang):
        self._lang = lang
        self._apply_language()

    # ══════════════════════════════════════════════════════════════════════════
    #  DRAG & DROP
    # ══════════════════════════════════════════════════════════════════════════
    def _setup_drag_drop(self):
        if _DND_AVAILABLE:
            try:
                self.drop_label.drop_target_register(_DND_FILES)
                self.drop_label.dnd_bind("<<Drop>>", self._on_drop)
            except Exception as e:
                self.after(200, lambda: self._log(self._("log_dnd_error", err=e)))
        else:
            self.after(200, lambda: self._log(self._("log_dnd_unavailable")))

    def _on_drop(self, event):
        path = event.data.strip().strip("{}")
        if os.path.isfile(path):
            self._load_source(path)

    # ══════════════════════════════════════════════════════════════════════════
    #  FILE HELPERS
    # ══════════════════════════════════════════════════════════════════════════
    def _browse_source(self):
        path = filedialog.askopenfilename(
            title=self._("lbl_wts_file"),
            filetypes=[("Warcraft III String Table", "*.wts"), ("*", "*.*")])
        if path:
            self._load_source(path)

    def _load_source(self, path):
        self.source_path.set(path)
        self.drop_label.configure(text=f"📄  {os.path.basename(path)}",
                                  text_color=("black", "white"))
        if not self.output_dir.get():
            self.output_dir.set(os.path.dirname(path))
        self._log(self._("log_file", path=path))

    def _browse_output(self):
        path = filedialog.askdirectory(title=self._("lbl_output_folder"))
        if path:
            self.output_dir.set(path)

    def _refresh_models(self):
        models = get_ollama_models()
        self.available_models = models
        self.model_menu.configure(values=models)
        if self.model_var.get() not in models and models:
            self.model_var.set(models[0])
        self._log(self._("log_models", models=", ".join(models)))

    def _on_perf_change(self, label):
        """Map the displayed perf label back to its internal key."""
        for key in ("low", "normal", "high"):
            if label == self._(f"perf_{key}"):
                self._perf_key = key
                break

    # ══════════════════════════════════════════════════════════════════════════
    #  CONSOLE
    # ══════════════════════════════════════════════════════════════════════════
    def _log(self, msg):
        self.console.configure(state="normal")
        self.console.insert("end", msg + "\n")
        self.console.see("end")
        self.console.configure(state="disabled")

    def _clear_console(self):
        self.console.configure(state="normal")
        self.console.delete("1.0", "end")
        self.console.configure(state="disabled")

    # ══════════════════════════════════════════════════════════════════════════
    #  PROGRESS
    # ══════════════════════════════════════════════════════════════════════════
    def _update_progress(self, current, total):
        if total <= 0:
            return
        pct = current / total
        self.progress_bar.set(pct)
        self.progress_label.configure(
            text=f"{current} / {total} strings  ({int(pct * 100)}%)")
        self.update_idletasks()

    # ══════════════════════════════════════════════════════════════════════════
    #  TRANSLATION
    # ══════════════════════════════════════════════════════════════════════════
    def _start_translation(self):
        if self.is_running:
            return

        src   = self.source_path.get().strip()
        out   = self.output_dir.get().strip()
        model = self.model_var.get().strip()
        perf  = _PERF_OPTIONS[self._perf_key]

        if not src or not os.path.isfile(src):
            messagebox.showwarning(self._("warn_no_file_title"),
                                   self._("warn_no_file_msg"))
            return
        if not out:
            messagebox.showwarning(self._("warn_no_folder_title"),
                                   self._("warn_no_folder_msg"))
            return

        base        = os.path.splitext(os.path.basename(src))[0]
        output_path = os.path.join(out, f"{base}_es.wts")

        self.is_running = True
        self.translate_btn.configure(state="disabled", text=self._("btn_translating"))
        self.progress_bar.set(0)
        self.progress_label.configure(text=self._("progress_starting"))
        self.update_idletasks()

        self._log(f"\n{'─' * 50}")
        self._log(f"Model: {model}  |  {self.perf_var.get()}")
        self._log(self._("log_dest", path=output_path))

        def run():
            try:
                translate_wts(
                    filepath    = src,
                    output_path = output_path,
                    model       = model,
                    perf_opts   = perf,
                    provider    = self._provider,
                    api_key     = self._api_key or None,
                    progress_cb = lambda c, t: self.after(0, self._update_progress, c, t),
                    log_cb      = lambda m:    self.after(0, self._log, m)
                )
                self.after(0, self._on_done, output_path)
            except Exception as e:
                self.after(0, self._on_error, str(e))

        threading.Thread(target=run, daemon=True).start()

    def _on_done(self, output_path):
        self.is_running = False
        self.translate_btn.configure(state="normal", text=self._("btn_translate"))
        self.progress_bar.set(1)
        self.progress_label.configure(text=self._("progress_done"))
        messagebox.showinfo(self._("done_title"), self._("done_msg", path=output_path))

    def _on_error(self, error_msg):
        self.is_running = False
        self.translate_btn.configure(state="normal", text=self._("btn_translate"))
        self.progress_bar.set(0)
        self.progress_label.configure(text=self._("progress_error"))
        self._log(f"\n!! ERROR: {error_msg}")
        messagebox.showerror(self._("error_title"),
                             self._("error_ollama", msg=error_msg))

# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if _DND_AVAILABLE:
        try:
            TkinterDnD._require(ctk.windows.ctk_tk.CTk)
        except Exception:
            pass
    app = WTSTranslatorApp()
    app.mainloop()
