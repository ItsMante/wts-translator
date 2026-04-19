# WTS Translator

<p align="center">
  <img src="logo.png" alt="WTS Translator Logo" width="120"/>
</p>

<p align="center">
  <strong>Herramienta de traducción de archivos .wts de Warcraft III impulsada por IA local</strong><br/>
  <em>Warcraft III .wts translation tool powered by local AI</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-blue"/>
  <img src="https://img.shields.io/badge/platform-Windows-lightgrey"/>
  <img src="https://img.shields.io/badge/license-MIT-green"/>
  <img src="https://img.shields.io/badge/AI-Ollama%20%2B%20gemma2-orange"/>
</p>

---

## ¿Qué es?

**WTS Translator** es una aplicación de escritorio para Windows que traduce automáticamente los archivos `.wts` de mapas personalizados de Warcraft III del **inglés al español latino**, usando modelos de IA que corren **100% en tu PC** sin enviar datos a ningún servidor externo.

Está diseñada para que los creadores y traductores de mapas puedan localizar su contenido de forma rápida, respetando los códigos de color y formato propios del motor de WC3.

---

## Características

- 🤖 **IA local con Ollama** — sin APIs de pago, sin internet requerido para traducir
- 🎨 **Protección de tags de color** — los códigos `|cXXXXXXXX...|r` se preservan intactos
- 📖 **Glosario personalizable** — terminología específica del mapa (facciones, unidades, lugares, habilidades...)
- ⚡ **Traducción en lotes** — procesa múltiples strings por llamada para mayor velocidad
- 🔁 **Reintentos automáticos** — detecta strings sin traducir y los reintenta individualmente
- 🌐 **Interfaz bilingüe** — cambiá entre Español e Inglés con un clic
- 🖱️ **Drag & Drop** — arrastrá el archivo `.wts` directamente a la ventana
- 📊 **Consola en tiempo real** — seguí el progreso string por string

---

## Requisitos

- Windows 10 / 11
- [Ollama](https://ollama.com) instalado y corriendo
- Modelo `gemma2` descargado (`ollama pull gemma2`)

> **Nota:** Ollama pesa ~1.8 GB y gemma2 ~5 GB. El instalador te ofrece descargarlos automáticamente.

---

## Instalación

### Opción A — Instalador (recomendado)

1. Descargá el instalador desde [Releases](https://github.com/ItsMante/wts-translator/releases)
2. Ejecutá `WTSTranslator_Setup_v1.0.0.exe`
3. Seguí los pasos — podés elegir instalar Ollama y descargar gemma2 desde el propio instalador

### Opción B — Desde el código fuente

```bash
git clone https://github.com/ItsMante/wts-translator.git
cd wts-translator
pip install customtkinter tkinterdnd2 Pillow ollama
python app.py
```

---

## Uso

1. Abrí **WTS Translator**
2. Asegurate de que **Ollama esté corriendo** en segundo plano
3. Arrastrá tu archivo `.wts` al área de drop, o usá el botón **Examinar**
4. Elegí la carpeta de destino
5. Seleccioná el modelo y el perfil de rendimiento según tu PC
6. Hacé clic en **▶ Traducir**

El archivo traducido se guarda como `nombreoriginal_es.wts` en la carpeta de destino.

### Perfil de rendimiento

| Perfil | Descripción |
|--------|-------------|
| 🐢 Bajo | Solo CPU — más lento pero funciona en cualquier PC |
| ⚡ Normal | GPU + CPU — balance recomendado |
| 🚀 Alto | GPU máximo — más rápido, requiere GPU dedicada con VRAM suficiente |

---

## Glosario

La pestaña **Glosario** te permite definir términos que no deben traducirse o que tienen una traducción específica para tu mapa (nombres de facciones, unidades, lugares, habilidades, etc.).

El glosario se aplica **antes** de enviar el texto al modelo, garantizando consistencia en toda la traducción.

---

## Estructura del proyecto

```
wts-translator/
├── app.py          # Interfaz gráfica (CustomTkinter)
├── translator.py   # Motor de traducción y pipeline LLM
├── glossary.json   # Glosario de términos por defecto
├── LICENSE.txt
├── CREDITS.txt
└── WTSTranslator_Setup.iss  # Script del instalador (Inno Setup)
```

---

## Roadmap

- [ ] Soporte para múltiples APIs (Anthropic, OpenAI, Gemini, DeepSeek)
- [ ] Traducción a idiomas distintos del español
- [ ] Cache de traducciones para no re-traducir strings ya procesados
- [ ] Vista previa diff antes de guardar

---

## Créditos y licencias

Desarrollado por **Mateo Neufeld (SoyMante)** con asistencia de **Claude (Anthropic)**.

Librerías utilizadas: `customtkinter`, `tkinterdnd2`, `Pillow`, `ollama-python` — todas bajo licencia MIT.

Modelo de IA: `gemma2` por Google DeepMind.

Ver [`CREDITS.txt`](CREDITS.txt) y [`LICENSE.txt`](LICENSE.txt) para más detalles.

---

## Contacto

- GitHub: [@ItsMante](https://github.com/ItsMante)
