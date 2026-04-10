import streamlit as st
import sys
import os
from dotenv import load_dotenv

# 1. LOCALIZACIÓN DE RUTAS (El corazón de la organización)
# Obtenemos la ruta de la carpeta raíz (message-generator)
# Subimos 3 niveles: desde app/ui/dashboard.py -> app/ui -> app -> raíz
ruta_raiz = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ruta_raiz)

# Definimos rutas útiles basadas en la raíz
ruta_config = os.path.join(ruta_raiz, 'app', 'config')
ruta_output = os.path.join(ruta_raiz, 'app', 'data', 'output')

# Cargamos el .env desde su nueva ubicación en app/config/
ruta_env = os.path.join(ruta_config, '.env')
load_dotenv(dotenv_path=ruta_env)

# 2. IMPORTACIÓN DISTRIBUIDA
# Ahora traemos la lógica desde el motor (core)
from app.core.engine import generar_mensajes_desde_nube

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Asistente de Obispado SUD", page_icon="🕊️", layout="centered")

# --- DISEÑO VISUAL ---
st.title("🤖 Panel de Automatización")
st.markdown("Generador de mensajes para asignaciones sacramentales.")
st.divider()

# --- CONFIGURACIÓN DINÁMICA ---
config_env_headless = os.getenv("HEADLESS_MODE", "False").lower() == "true"

st.sidebar.header("Configuración del Bot")
ver_navegador = st.sidebar.toggle(
    "Ver navegador en vivo", 
    value=not config_env_headless,
    help="Si está activado, se abrirá una ventana de Chrome para que veas el envío de WhatsApp."
)

col1, col2 = st.columns(2)
with col1:
    st.info("📊 **Base de datos:** Google Sheets conectado.")
with col2:
    st.info("🧠 **Motor IA:** Gemini 2.5 Flash en línea.")

st.divider()
st.write("Haz clic en el botón de abajo para iniciar el ciclo.")

# --- BOTÓN DE ACCIÓN ---
if st.button("🚀 Iniciar Ciclo de Notificaciones", use_container_width=True, type="primary"):
    
    # Pasamos la elección del usuario al entorno para que los servicios la lean
    os.environ["HEADLESS_MODE"] = str(not ver_navegador)
    
    with st.spinner('El bot está trabajando. No cierres esta ventana...'):
        try:
            # Apuntamos a la nueva carpeta de salida
            ruta_del_txt = os.path.join(ruta_output, 'mensajes_generados.txt')
            
            # Ejecución
            generar_mensajes_desde_nube(ruta_del_txt)
            
            st.success("✅ ¡Proceso finalizado! Revisa la nube.")
            st.balloons() 
            
        except Exception as e:
            st.error(f"❌ Error crítico: {e}")

st.divider()
st.caption("Desarrollado por Cristian | Portfolio Engineering")