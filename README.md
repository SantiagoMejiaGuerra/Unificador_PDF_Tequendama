# 📄 Herramienta de Unificación y Organización de Documentos PDF

## Descripción del Proyecto
Esta aplicación de escritorio, desarrollada en Python, automatiza la gestión de archivos PDF. Su funcionalidad principal es **identificar documentos duplicados basados en un patrón de identificación** (ejemplo: tipo y número de ID) y **unificar todo su contenido en un único archivo PDF**.

El objetivo es asegurar que la información completa de cada expediente quede consolidada en un solo documento, eliminando la redundancia y optimizando el flujo de trabajo de organización.

## 🛠️ Tecnologías Utilizadas

* **Lenguaje:** Python 3.x
* **Interfaz Gráfica (GUI):** `customtkinter` (basado en Tkinter)
* **Manipulación de PDF:** `fitz` (PyMuPDF)
* **Gestión de Archivos:** `os`, `shutil`
* **Procesamiento de Texto:** `re` (Expresiones Regulares)
* **Contenedores de Datos:** `collections.defaultdict`

## ✨ Características Principales

### 1. Unificación Inteligente (Basada en RegEx)
* **Criterio de Duplicación:** Los archivos se consideran duplicados y se agrupan si comparten el **Tipo de Documento** (ej. FEV, CRC) y el **Número de Identificación** (ej. CC1001526294), incluso si están en subcarpetas diferentes.
* **Consolidación:** Los documentos duplicados se fusionan página por página en un solo PDF.

### 2. Robustez y Limpieza del Nombramiento
* La lógica de la función `get_display_name` limpia los nombres de archivo eliminando extensiones duplicadas o incorrectas (ej. `nombre.PDF.pdf`).
* Los archivos unificados se nombran con un formato estandarizado basado en la información extraída (Tipo de Documento, Formato, Tipo y Número de ID).

### 3. Interfaz de Usuario (GUI)
* Diseño moderno con `customtkinter`.
* Selector de **Modo de Apariencia** (Claro/Oscuro).
* Selección clara de la **Carpeta de Origen** (donde se busca) y la **Carpeta de Destino** (donde se guardan los resultados).

### 4. Flujo de Procesamiento Garantizado
* **Separación Lógica:** El programa procesa los archivos unificados y los archivos únicos por separado.
* **Manejo de Sobrescritura:** Se implementa una lógica para evitar sobreescribir archivos existentes en el destino, añadiendo un sufijo (`_1`, `_2`, etc.).
* **Cierre Forzado:** Uso de `sys.exit()` para garantizar que el proceso se detenga completamente al cerrar la ventana.

## ⚙️ Uso e Instalación

### Requisitos
Necesitas tener instalado Python 3.x.

### Instalación de Librerías
```bash
pip install customtkinter PyMuPDF pillow