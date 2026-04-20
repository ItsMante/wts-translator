# WTS Translator — Historial de cambios

---

## v1.3.0

### Nuevas características

**Cache de traducciones**
- Los strings ya traducidos se guardan en `%APPDATA%\WTS Translator\cache.json`
- En traducciones posteriores del mismo mapa (o mapas que comparten strings),
  los strings cacheados se recuperan al instante sin llamar al LLM
- El log muestra cuántos strings vinieron del cache vs cuántos se tradujeron
- Sección "Cache de traducciones" en Configuración con contador de entradas
  y botón para limpiar el cache cuando sea necesario

**Vista previa diff**
- Ventana modal que aparece al terminar la traducción, antes de guardar el archivo
- Tabla con tres columnas: ID | Original | Traducido
- La columna Traducido es editable — podés corregir strings directo ahí
- Filas en amarillo = strings con advertencias (sin traducir o alucinación)
- Strings del cache aparecen en verde
- Botones: Seleccionar todo / Deseleccionar todo / Solo advertencias
- Los strings desmarcados se revierten al original al guardar
- Cancelar descarta todo sin escribir ningún archivo
- Activada por defecto, se puede desactivar en Configuración

**Importar / Exportar glosario**
- Botón Exportar — guarda el glosario actual como .json donde el usuario elija
- Botón Importar — carga un .json externo con validación de estructura
- Al importar, muestra cuántos términos son nuevos vs conflictos
- Dos modos: Combinar (añade sin pisar existentes) o Reemplazar (reemplaza todo)
- La UI del glosario se recarga automáticamente tras importar

---

## v1.2.0

### Nuevas características

**Pestaña de Configuración**
- Soporte para múltiples proveedores de IA: Ollama, Anthropic, OpenAI, Gemini, DeepSeek
- Campo de API Key con botón mostrar/ocultar
- Botón Probar conexión para verificar la API Key antes de traducir
- Selector de tema: Oscuro / Claro / Sistema
- Selector de idioma de la interfaz movido a Configuración
- Configuración guardada entre sesiones en `%APPDATA%\WTS Translator\config.json`

### Correcciones

- Glosario no se guardaba en la versión instalada (permisos de Program Files)
- Categorías nuevas del glosario no se aplicaban al traducir
- Tema claro mostraba fondos oscuros en la pestaña Configuración

---

## v1.1.0

### Correcciones

- Interfaz bilingüe ES/EN no funcionaba en el exe compilado

---

## v1.0.0

- Lanzamiento inicial
- Traducción automática de archivos .wts de Warcraft III (EN a ES)
- Motor local con Ollama + gemma2
- Protección de tags de color
- Glosario personalizable por categorías
- Traducción en lotes con reintentos automáticos
- Interfaz bilingüe Español / English
- Drag & Drop de archivos .wts
- Perfiles de rendimiento CPU / GPU
