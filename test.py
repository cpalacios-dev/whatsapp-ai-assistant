import os
import sys
import logging
from unittest.mock import patch

# Configuración de ruta
ruta_raiz = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ruta_raiz)

# 🟢 NUEVO: Forzar que los logs del bot salgan en la terminal de VSC
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger()
if not logger.handlers:
    logger.addHandler(logging.StreamHandler(sys.stdout))

from app.core.engine import generar_mensajes_desde_nube

# ==========================================
# ⚙️ PANEL DE CONTROL DE PRUEBAS
# ==========================================
SIMULAR_WHATSAPP = True   
SIMULAR_SHEETS = True     
FORZAR_FALLO_IA = True   
# ==========================================

def ejecutar_pruebas():
    print("\n========================================")
    print("🧪 INICIANDO ENTORNO DE PRUEBAS (MOCKING)")
    print("========================================\n")

    ruta_txt_prueba = os.path.join(ruta_raiz, 'app', 'data', 'output', 'mensajes_testing.txt')
    parches = []

    if SIMULAR_WHATSAPP:
        parche_wsp = patch('app.core.engine.enviar_mensajes')
        mock_wsp = parche_wsp.start()
        mock_wsp.side_effect = lambda msjs: print(f"\n📞 [MOCK] Playwright ignorado. Se enviarían {len(msjs)} mensajes.")
        parches.append(parche_wsp)

    if SIMULAR_SHEETS:
        parche_sheets = patch('app.core.engine.actualizar_estado_notificado')
        mock_sheets = parche_sheets.start()
        mock_sheets.side_effect = lambda id_hoja, msjs: print(f"📊 [MOCK] Sheets ignorado. Se actualizarían {len(msjs)} filas.")
        parches.append(parche_sheets)

    if FORZAR_FALLO_IA:
        print("🔴 SIMULACIÓN: Forzando fallo crítico de Gemini.")
        parche_ia = patch('app.core.engine.redactar_mensaje_con_ia')
        mock_ia = parche_ia.start()
        mock_ia.return_value = None 
        parches.append(parche_ia)
    
    try:
        generar_mensajes_desde_nube(ruta_txt_prueba)
        print(f"\n✅ Ciclo de pruebas finalizado.")
        print(f"📄 Revisa los textos en: {ruta_txt_prueba}\n")
    finally:
        for p in parches:
            p.stop()

if __name__ == '__main__':
    ejecutar_pruebas()