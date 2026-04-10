import gspread
import os
import pandas as pd
import logging
from google.oauth2.service_account import Credentials

# Rutas calculadas desde este archivo
ruta_raiz = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ruta_json = os.path.join(ruta_raiz, 'app', 'config', 'service_account.json')

def conectar_hoja():
    """Establece conexión con la API de Google."""
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    if not os.path.exists(ruta_json):
        raise FileNotFoundError(f"🚨 No se encontró service_account.json en: {ruta_json}")
    
    creds = Credentials.from_service_account_file(ruta_json, scopes=scopes)
    return gspread.authorize(creds)

def leer_asignaciones(id_hoja):
    """Trae los datos de la nube y los entrega como un DataFrame limpio."""
    try:
        cliente = conectar_hoja()
        sh = cliente.open_by_key(id_hoja)
        hoja = sh.get_worksheet(0)
        return pd.DataFrame(hoja.get_all_records())
    except Exception as e:
        logging.error(f"❌ Error leyendo Sheets: {e}")
        return None

def actualizar_estado_notificado(id_hoja, lista_mensajes, columna_estado=7):
    """
    Recibe la lista completa de diccionarios y actualiza Sheets solo si 'enviado' es True.
    """
    try:
        cliente = conectar_hoja() # Tu función que usa service_account.json
        hoja = cliente.open_by_key(id_hoja).get_worksheet(0)

        for contacto in lista_mensajes:
            # Verificamos si el mensaje realmente se envió
            if contacto.get('enviado') is True:
                fila = contacto.get('fila_sheets')
                if fila:
                    hoja.update_cell(fila, columna_estado, "Notificado")
                    logging.info(f"   ✔ Estado actualizado para: {contacto['nombre']}")
    except Exception as e:
        logging.error(f"❌ Error actualizando estado: {e}")