# WTS Translator v1.1.0 — Release Notes

## Nuevas características

### Pestaña de Configuración
- Nueva pestaña **Configuración** con todas las opciones en un solo lugar
- Soporte para múltiples proveedores de IA: **Ollama, Anthropic, OpenAI, Gemini, DeepSeek**
- Campo de API Key con botón para mostrar/ocultar
- Botón **Probar conexión** para verificar que la API Key funciona antes de traducir
- Configuración guardada automáticamente entre sesiones

### Selector de tema
- Cambiar entre **Oscuro / Claro / Sistema** en tiempo real desde Configuración

### Idioma de la interfaz
- El selector de idioma (Español / English) se movió a la pestaña Configuración

---

## Correcciones

### Glosario no se guardaba en la versión instalada
- **Problema:** Al instalar la app en `Program Files`, Windows bloqueaba la escritura
  del `glossary.json` por permisos, por lo que los cambios se perdían al cerrar.
- **Solución:** El glosario y la configuración ahora se guardan en
  `%APPDATA%\WTS Translator\`, que siempre tiene permisos de escritura.
  En la primera ejecución se copia automáticamente el glosario por defecto.

### Categorías nuevas del glosario no se aplicaban al traducir
- **Problema:** El motor de traducción tenía hardcodeadas 7 categorías fijas.
  Cualquier categoría nueva creada por el usuario (ej. "Objetos") era ignorada.
- **Solución:** `preprocess_glossary` ahora itera dinámicamente sobre todas las
  categorías del JSON, sin importar cuántas ni cómo se llamen.
- **Bonus:** Los términos de todas las categorías ahora se ordenan globalmente
  de mayor a menor longitud, evitando que términos cortos reemplacen partes de
  términos más largos (ej. "Knight" dentro de "Death Knight").

### Tema claro mostraba fondos oscuros en la pestaña Configuración
- Labels y frames en la pestaña Configuración ahora usan `fg_color="transparent"`
  para heredar correctamente el color de fondo en cualquier tema.

---

## Notas técnicas
- El proveedor, modelo y API Key quedan guardados en `%APPDATA%\WTS Translator\config.json`
- El glosario editable queda en `%APPDATA%\WTS Translator\glossary.json`
- Los SDKs de Anthropic, OpenAI y Gemini se importan de forma lazy (solo cuando se usan)
