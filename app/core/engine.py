import pandas as pd
import time
import os
import logging
from google import genai
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
# Al inicio de app/core/engine.py
from app.services.whatsapp_sender import enviar_mensajes 
from app.core.scraper import extraer_info_discurso 
from app.services.google_sheets import leer_asignaciones, actualizar_estado_notificado
# =================================================================
# CONFIGURACIÓN DE RUTAS Y SEGURIDAD
# =================================================================
# Al estar en app/core/, subimos dos niveles para llegar a la raíz
ruta_raiz = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Definimos las rutas a las carpetas de configuración y logs
ruta_config = os.path.join(ruta_raiz, 'app', 'config')
ruta_logs = os.path.join(ruta_raiz, 'app', 'logs')

ruta_env = os.path.join(ruta_config, '.env')
ruta_json = os.path.join(ruta_config, 'service_account.json')

load_dotenv(dotenv_path=ruta_env)

# Variables de entorno
API_KEY = os.getenv("GEMINI_API_KEY")
MODELO_IA = os.getenv("AI_MODEL", "gemini-2.5-flash")
ID_HOJA = os.getenv("GOOGLE_SHEET_ID")

cliente_gemini = genai.Client(api_key=API_KEY)

# =================================================================
# SISTEMA DE LOGS
# =================================================================
ruta_log_file = os.path.join(ruta_logs, 'bot_auditoria.log')
os.makedirs(os.path.dirname(ruta_log_file), exist_ok=True)

logging.basicConfig(
    filename=ruta_log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)


logging.info("Iniciando sistema. Revisar archivo de auditoría para detalles.")
logging.info("=== NUEVA EJECUCIÓN DEL BOT INICIADA ===")


def redactar_mensaje_con_ia(nombre, tema, fecha, tiempo, autor, titulo, link, max_intentos=3):
    """
    Redacción con IA. Si cambias de modelo (ej. gemini-2.0-pro), modifícalo abajo.
    """
    prompt = f"""
    Eres un miembro del obispado de La Iglesia de Jesucristo de los Santos de los Últimos Días (SUD). Redacta un mensaje de WhatsApp amigable, cercano y espiritual para {nombre}, asignándole un discurso para la próxima Reunión Sacramental.
    
    Instrucciones estrictas:
    1. Saluda a la persona cálidamente.
    2. Menciona que como obispado han meditado y orado para darle esta asignación.
    3. Indica que puede usar escrituras, discursos u otras fuentes inspiradas.
    4. Incluye estos detalles exactos usando emojis y negritas (con asteriscos) para que resalten en WhatsApp:
       - Tema: {tema}
       - Fecha: Domingo {fecha}
       - Tiempo: {tiempo}
    """
    
    if link and str(link).startswith('http'):
        prompt += f"""
    5. Agrega una sección de "Material de apoyo sugerido" mencionando que le comparten un mensaje titulado "{titulo}" por {autor}.
    6. Pon este enlace exactamente como está al final: {link}
    """
    else:
        prompt += "\n5. No menciones ningún material de apoyo en específico, ya que no hay un link asignado para esta ocasión."

        
    prompt += f"""\n\nRedacta solo el mensaje listo para enviar, sin notas adicionales ni marcadores de posición. 
    IMPORTANTE: El mensaje DEBE terminar obligatoriamente con una frase cálida de cierre similar a: "Cualquier pregunta o si necesita algo, por favor no dudes en contactarnos." o "Si tienes dudas con el tema, avísanos para ayudarte."
    NO incluyas nombres ni firmas formales debajo de esa frase (omite por completo cosas como 'Un fuerte abrazo', 'Atentamente' o 'El Obispado'). Termina exactamente en la frase de ayuda."""

    for intento in range(max_intentos):
        try:
            respuesta = cliente_gemini.models.generate_content(
                model= MODELO_IA,  # <--- Cambia el modelo aquí si Google lanza uno nuevo
                contents=prompt,
            )
            time.sleep(5) 
            return respuesta.text.strip()
            
        except Exception as e:
            error_msg = str(e)
            if "503" in error_msg or "429" in error_msg:
                logging.info(f"   ⚠️ Servidor ocupado (Intento {intento + 1}). Esperando...")
                time.sleep(5) 
            else:
                logging.error(f"   ❌ Error desconocido: {repr(e)}")
                return None 
                
    return None


def generar_mensajes_desde_nube(ruta_salida):
    """
    PROCESAMIENTO LÓGICO. 
    Aquí se definen los nombres de las columnas que debe tener tu Excel/Sheet.
    """
    df = leer_asignaciones(ID_HOJA)
    
    if df is None or df.empty:
        logging.info("⚠️ No se encontraron datos en la hoja de cálculo.")
        return

    mensajes_listos_para_enviar = [] 
    # Aseguramos que la carpeta de salida exista
    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)

    with open(ruta_salida, 'w', encoding='utf-8') as archivo_txt:
        logging.info(f"🚀 Iniciando el proceso de generación...")
        
        for index, fila in df.iterrows():
            # MODIFICAR: Estos nombres deben coincidir exactamente con los encabezados de tu Excel:
            nombre = str(fila.get('Hermano/a', ''))
            estado = str(fila.get('Estado', '')) 
            fecha = fila.get('Fecha', '')
            tiempo = fila.get('Tiempo asignado', '')
            tema = fila.get('Tema', '')
            link = fila.get('Material de apoyo sugerido', None)
            telefono = fila.get('Teléfono', None) 
            
            # Filtros de seguridad para no enviar mensajes a filas vacías o informativas
            if "Notificado" in estado:
                logging.info(f"⏭️ Omitiendo a {nombre.upper()}: Ya notificado.")
                continue

            if pd.isna(nombre) or nombre.strip() == '' or 'Ayuno' in nombre or 'Testimonios' in nombre:
                continue
                
            primer_nombre = "Hermano/a" if '[' in nombre else nombre.split()[0]
            
            logging.info(f"⏳ Procesando a: {nombre.upper()}")
            
            autor, titulo = None, None
            if not pd.isna(link) and str(link).startswith('http'):
                autor, titulo = extraer_info_discurso(link)
                

            mensaje = redactar_mensaje_con_ia(primer_nombre, tema, fecha, tiempo, autor, titulo, link)
            

            if not mensaje:
                logging.info("   ⚠️ Generación fallida. Usando mensaje de respaldo estático...")
                
                # Parte inicial del mensaje
                mensaje = (
                    f"Hola {primer_nombre}, ¿cómo estás?\n\n"
                    f"Esperando que estés bien, te escribo para comentarte que como obispado hemos meditado y orado, "
                    f"y sentimos la inspiración de asignarte un mensaje para compartir en la Reunión Sacramental.\n\n"
                    f"Puedes utilizar el material que estimes conveniente: discursos de autoridades de la Iglesia, "
                    f"escrituras, experiencias espirituales, libros o estudios que se relacionen con el tema.\n\n"
                    f"📌 *Detalles de la asignación:*\n"
                    f"🗣️ *Tema:* {fila.get('Tema')}\n"
                    f"🗓️ *Fecha:* Domingo {fila.get('Fecha')}.\n"
                    f"⏰ *Tiempo:* {fila.get('Tiempo asignado')}.\n"
                )

                # Si el scraper logró obtener info del link, la agregamos elegantemente
                if link and str(link).startswith('http'):
                    mensaje += (
                        f"\n📖 *Material de apoyo:* Como guía adicional para tu preparación, "
                        f"te compartimos este excelente recurso de {autor}. Es un mensaje muy poderoso "
                        f"el cual tiene por título \"{titulo}\".\n"
                        f"👉 {link}\n"
                    )
                
                # Cierre del mensaje
                mensaje += "\nAgradecemos mucho tu disposición para compartir tu testimonio con el barrio. ¡Cualquier duda quedamos atentos!"
            
            else:
                logging.info(f"   ✅ Mensaje generado con éxito.")
            
            archivo_txt.write(f"--- PARA: {nombre.upper()} ---\n{mensaje}\n\n" + "="*60 + "\n\n")
            
            telefono = fila.get('Teléfono', None)
            if not pd.isna(telefono) and str(telefono).strip() != '':
                mensajes_listos_para_enviar.append({
                    'nombre': nombre,
                    'numero': telefono,
                    'mensaje': mensaje,
                    'fila_sheets': index + 2 # Cálculo para volver a escribir en la fila correcta de Google
                })

    if mensajes_listos_para_enviar:
        # 1. Ejecutamos el envío masivo por WhatsApp
        enviar_mensajes(mensajes_listos_para_enviar)
        
        # 2. Sincronizamos los resultados con la nube (Google Sheets)
        logging.info("📝 Sincronizando estados de envío con Google Sheets...")
        
        id_hoja = os.getenv("GOOGLE_SHEET_ID")
        # LLAMADA CORRECTA:
        actualizar_estado_notificado(id_hoja, mensajes_listos_para_enviar)
        
        logging.info("✅ Proceso de actualización finalizado.")

# --- EJECUCIÓN ---
if __name__ == '__main__':
    # Define dónde quieres que se guarde el respaldo de los mensajes en texto:
    ruta_backup = os.path.join(ruta_raiz, 'app', 'data', 'output', 'mensajes_generados.txt')
    generar_mensajes_desde_nube(ruta_backup)