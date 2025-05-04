# 🧪 Medical Chatbot

¡Bienvenido/a al repositorio de **Medical Chatbot**!  
Este es un chatbot médico construido en **Python 3.12**, que utiliza **Gradio** para ofrecer una interfaz web interactiva y **Ollama** como motor de lenguaje para generar respuestas naturales y útiles.

---

## 📋 Requisitos previos

- Python **3.12**
- `pip` instalado
- Tener instalado **[Ollama](https://ollama.com/)**
- (Opcional) `virtualenv` o `conda` para crear entornos virtuales

---

## 🛠️ Instalación de dependencias

Las dependencias necesarias están listadas en el archivo `requirements.txt`.

### 📁 Opción 1: Usando `virtualenv`

```bash
# Instalar virtualenv si no lo tienes
pip install virtualenv

# Crear entorno virtual
virtualenv venv

# Activar entorno virtual
# En Windows
.\venv\Scripts\activate
# En macOS/Linux
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

---

### 🐍 Opción 2: Usando `conda`

```bash
# Crear entorno con Python 3.12
conda create -n medical-chatbot python=3.12

# Activar entorno
conda activate medical-chatbot

# Instalar dependencias
pip install -r requirements.txt
```

---

## ⚡️ Configuración de variables de entorno

Antes de ejecutar el chatbot, debes configurar las variables de entorno necesarias:

1. Copia el archivo `.env-example` y renómbralo como `.env`:

```bash
cp .env-example .env
```

2. Abre el archivo `.env` y reemplaza los valores faltantes con los adecuados para tu entorno:

```dotenv
OLLAMA_HOST="http://localhost:11434"
OLLAMA_LLM_MODEL="gemma3:12b"
OLLAMA_EMBEDDINGS_MODEL="all-minilm"
DATABASE_CONNECTION=""
```

---

## ▶️ Cómo ejecutar el chatbot

1. Asegúrate de tener **Ollama** instalado y ejecutando un modelo compatible (como `llama2`, `gemma3`, etc.).  
   Puedes iniciarlo así (ejemplo con `gemma3:12b`):

```bash
ollama run gemma3:12b
```

2. Luego, ejecuta la aplicación:

```bash
python3.12 main.py
```

3. Se abrirá una interfaz en tu navegador (cortesía de **Gradio**) donde podrás interactuar con el chatbot.

---

## 🚧 En desarrollo

Este proyecto está en constante evolución.  
¡Tus ideas, sugerencias y reportes de errores son más que bienvenidos!

---

## 📄 Licencia

Este proyecto está bajo la licencia [MIT](LICENSE).

---

¡Gracias por visitar **Medical Chatbot**! 💬

