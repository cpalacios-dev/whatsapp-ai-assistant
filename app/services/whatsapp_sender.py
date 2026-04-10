import time
import urllib.parse
import os
import sys       
import asyncio   
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

# =================================================================
# CONFIGURACIÓN DE COMPATIBILIDAD Y RUTAS
# =================================================================
# Parche vital para Windows + Streamlit
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Al estar en app/services/whatsapp_sender.py, subimos dos niveles para la raíz del proyecto
ruta_raiz = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Cargamos el .env desde la nueva ubicación: app/config/.env
ruta_env = os.path.join(ruta_raiz, 'app', 'config', '.env')
load_dotenv(dotenv_path=ruta_env)

def enviar_mensajes(lista_mensajes):
    """
    Controla el navegador Chromium para enviar mensajes automáticos.
    """
    # 1. LEER CONFIGURACIÓN DESDE EL .ENV
    modo_headless = os.getenv("HEADLESS_MODE", "False").lower() == "true"
    tiempo_espera_login = int(os.getenv("WAIT_TIME_LOGIN", 90))
    tiempo_espera_envio = int(os.getenv("WAIT_TIME_AFTER_SEND", 5))

    if not lista_mensajes:
        print("No hay mensajes para enviar.")
        return

    # =================================================================
    # GESTIÓN DE SESIÓN (COOKIES)
    # =================================================================
    # IMPORTANTE: Ahora guardamos la sesión en app/data/session/
    ruta_sesion = os.path.join(ruta_raiz, 'app', 'data', 'session')
    os.makedirs(ruta_sesion, exist_ok=True)

    print("Iniciando Playwright...")
    with sync_playwright() as p:
        print(f"\n🌐 Navegador iniciado (Modo Headless: {modo_headless})")
        
        # launch_persistent_context mantiene la sesión iniciada
        browser = p.chromium.launch_persistent_context(
            user_data_dir=ruta_sesion,
            headless=modo_headless,
            args=["--start-maximized"]
        )

        page = browser.new_page()
        page.goto("https://web.whatsapp.com/")
        
        print(f"⏳ Esperando conexión (Máximo {tiempo_espera_login}s)...")
        try:
            # Esperamos el panel lateral de chats como señal de que cargó correctamente
            page.wait_for_selector('#pane-side', timeout=tiempo_espera_login * 1000)
            print("✅ Sesión activa.")
        except Exception:
            print("❌ Tiempo de espera agotado. ¿Escaneaste el código QR?")
            browser.close()
            return

        for contacto in lista_mensajes:
            nombre = contacto['nombre']
            numero = str(contacto['numero']).strip().replace('.0', '')
            mensaje = contacto['mensaje']
            
            # Codificamos el mensaje para URL
            mensaje_url = urllib.parse.quote(mensaje)
            
            print(f"\n🚀 Preparando envío para: {nombre} ({numero})...")
            page.goto(f"https://web.whatsapp.com/send?phone={numero}&text={mensaje_url}")

            try:
                # IDENTIFICADOR DEL BOTÓN ENVIAR: data-icon="wds-ic-send-filled"
                boton_enviar = page.wait_for_selector('span[data-icon="wds-ic-send-filled"]', timeout=30000)
                
                # Pausa técnica para simular comportamiento humano
                time.sleep(2) 
                
                boton_enviar.click()
                print(f"   ✅ Mensaje despachado a {nombre}")
                
                # Tiempo de espera configurado en el .env antes de pasar al siguiente
                time.sleep(tiempo_espera_envio)
                contacto['enviado'] = True 
                
            except Exception as e:
                print(f"   ❌ Falló el envío para {nombre}. Revisa el número o el formato.")
                contacto['enviado'] = False 
                
        print("\n🎉 ¡Todos los envíos finalizados! Cerrando navegador...")
        browser.close()