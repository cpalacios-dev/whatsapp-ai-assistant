# 🕊️ Asistente Automatizado de Asignaciones SUD (WhatsApp Bot)

<p align="center">
  <img src="https://img.shields.io/badge/Python_3.12-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white"/>
  <img src="https://img.shields.io/badge/Playwright-009943?style=for-the-badge&logo=playwright&logoColor=white"/>
  <img src="https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white"/>
  <img src="https://img.shields.io/badge/Google_Gemini-8E75B2?style=for-the-badge&logo=googlegemini&logoColor=white"/>
  <img src="https://img.shields.io/badge/Google_Sheets-34A853?style=for-the-badge&logo=googlesheets&logoColor=white"/>
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white"/>
</p>

Un sistema integral de automatización diseñado para gestionar, redactar y enviar mensajes personalizados de WhatsApp con asignaciones para la Reunión Sacramental de La Iglesia de Jesucristo de los Santos de los Últimos Días.
 
Este proyecto combina **Web Scraping dinámico, Inteligencia Artificial y Automatización de Navegadores** bajo una arquitectura de software modular, limpia y escalable.

## ✨ Características Principales
 
- 📊 **Sincronización en la Nube:** Conexión en tiempo real con Google Sheets para leer pendientes y marcar las asignaciones enviadas de forma bidireccional (`gspread`).
- 🧠 **Redacción Inteligente (IA):** Generación de mensajes cálidos y personalizados utilizando Google Gemini 2.5 Flash, con un sistema de respaldo (fallback) estático en caso de fallas de red.
- 🌐 **Web Scraping Avanzado:** Algoritmo de extracción multinivel adaptativo que burla bloqueos web, analiza etiquetas ocultas (Dublin Core, bylines) y deduce inteligentemente el título eclesiástico (Presidente, Élder, Hermana) según el cargo del autor (`BeautifulSoup4` + `regex`).
- 💬 **Envío Autónomo:** Control de navegador en segundo plano (Headless) para enviar los mensajes a través de WhatsApp Web (`Playwright`).
- 🖥️ **Interfaz de Usuario:** Panel de control interactivo para gestionar la ejecución del bot (`Streamlit`).
- 🧪 **Entorno de Testing:** Sistema de Mocking nativo integrado para simular envíos y fallas sin consumir cuota de IA ni enviar mensajes reales (`unittest.mock`).
  
## 🛠️ Tecnologías y Librerías
  
- **Lenguaje:** Python 3.12
- **IA:** Google GenAI SDK (Gemini)
- **Automatización:** Playwright
- **Scraping:** BeautifulSoup4, Requests, Regex
- **Datos:** Pandas
- **Nube:** Google Auth, API de Google Sheets
- **UI:** Streamlit
  
## 📁 Arquitectura del Proyecto
El proyecto sigue principios de ***Separation of Concerns*** (Separación de responsabilidades):
 
```text
📦 message-generator/
├── 🙈 .gitignore
├── 🐳 Dockerfile
├── 📖 README.md
├── 📋 requirements.txt
├── 🧪 test.py                     # Entorno de pruebas y mocking
└── 📁 app/
    ├── 📁 config/                 # Variables de entorno y credenciales
    │   ├── ⚙️ .env
    │   └── 🔑 service_account.json
    ├── 📁 core/                   # Lógica de negocio (Cerebro)
    │   ├── 🐍 engine.py           # Orquestador del sistema
    │   └── 🐍 scraper.py          # Motor de extracción web
    ├── 📁 data/                   # Almacenamiento local aislado
    │   ├── 📁 input/
    │   ├── 📁 output/             # Respaldo en texto de mensajes generados
    │   └── 📁 session/            # Sesión encriptada de WhatsApp Web
    ├── 📁 logs/                   # Auditoría y trazabilidad del sistema
    ├── 📁 services/               # Integración con APIs externas
    │   ├── 🐍 google_sheets.py
    │   └── 🐍 whatsapp_sender.py
    └── 📁 ui/                     # Frontend
        └── 🐍 dashboard.py
```

## ⚙️ Configuración e Instalación

1. **Clonar el repositorio y crear entorno virtual:**

```bash
git clone <tu-url-de-github>
cd message-generator
python -m venv venv
source venv/Scripts/activate # En Windows
```

2. **Instalar dependencias y navegadores:**

```bash
pip install -r requirements.txt
playwright install chromium
```

3. **Configurar Credenciales:**
- Coloca tu archivo de Google Cloud en `app/config/service_account.json`.
- Crea un archivo `app/config/.env` basándote en la siguiente estructura:

```dotenv
GEMINI_API_KEY="tu_api_key_aqui"
GOOGLE_SHEET_ID="id_de_tu_hoja"
HEADLESS_MODE=False
AI_MODEL=gemini-2.5-flash

```

## 🚀 Uso del Sistema

**Modo Producción (Interfaz Gráfica)** Para iniciar el ciclo de envío real con interfaz web:

```bash
streamlit run app/ui/dashboard.py
```

**Modo Testing (Terminal)** Para probar la lógica, el scraper y el flujo sin enviar WhatsApps ni gastar saldo de IA:

```bash
python test.py
```

----------
**Desarrollado por [Cristian Palacios](https://cpalacios-dev.github.io/)** - _Ingeniero Informático | Portfolio Engineer | RPA & Cloud Specialist_
