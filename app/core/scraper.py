import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
import logging

def extraer_info_discurso(url):
    if pd.isna(url) or not str(url).startswith('http'):
        return "un líder de la Iglesia", "este discurso"
        
    logging.info(f"🔎 SCRAPER: Iniciando extracción para URL: {url}")
        
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...',
            'Accept-Language': 'es-CL,es-ES;q=0.9,en;q=0.8',
            'Referer': 'https://www.google.com/'
        }
        
        respuesta = requests.get(url, headers=headers, timeout=15)
        respuesta.encoding = 'utf-8' 
        
        autor_raw, rol_raw = "", ""
        titulo = "este discurso"
        
        if respuesta.status_code == 200:
            soup = BeautifulSoup(respuesta.text, 'html.parser')
            
            # --- 1. TÍTULO ---
            t_meta = soup.find('meta', attrs={'property': 'og:title'})
            if t_meta: titulo = t_meta.get('content')
            else:
                h1 = soup.find('h1')
                if h1: titulo = h1.get_text()
            
            titulo = re.split(r' - | \| | — | – ', titulo)[0].strip()

            # --- 2. AUTOR Y CARGO (Extracción simultánea) ---
            byline = soup.find(class_=re.compile(r"byline|author-container", re.I))
            
            if byline:
                parrafos = byline.find_all(['p', 'span', 'h6'])
                if len(parrafos) > 0: autor_raw = parrafos[0].get_text().strip()
                if len(parrafos) > 1: rol_raw = parrafos[1].get_text().strip()
            else:
                # Respaldo para páginas antiguas
                p1 = soup.find(attrs={"id": "p1"})
                p2 = soup.find(attrs={"id": "p2"})
                if p1: autor_raw = p1.get_text()
                if p2: rol_raw = p2.get_text()
                
                # Si no hay p1, buscamos en los metas
                if not autor_raw:
                    meta_auth = soup.find('meta', attrs={'name': 'author'})
                    if meta_auth: autor_raw = meta_auth.get('content')

            # Corrección de formato (Ej: Camargo, Marcos A.)
            if ',' in autor_raw and len(autor_raw.split(',')) == 2:
                partes = autor_raw.split(',')
                autor_raw = f"{partes[1].strip()} {partes[0].strip()}"

            # --- 3. LIMPIEZA PARA OBTENER EL NOMBRE PURO ---
            nombre_puro = autor_raw
            patrones_limpieza = [
                r'(?i)^Presentado por el presidente ', r'(?i)^Presentado por el ', r'(?i)^Presentado por ',
                r'(?i)^Por el ', r'(?i)^Por la ', r'(?i)^Por ', r'(?i)^Elder ', 
                r'(?i)^Élder ', r'(?i)^Hermana presidenta ', r'(?i)^Presidenta ', 
                r'(?i)^Presidente ', r'(?i)^Hermano ', r'(?i)^Hermana ', r'(?i)^Obispo ', 
                r'(?i),? de los Setenta.*'
            ]
            for r in patrones_limpieza:
                nombre_puro = re.sub(r, '', nombre_puro).strip()
            
            nombre_puro = nombre_puro.replace('\xa0', ' ').strip().rstrip(',')

            # --- 4. DEDUCCIÓN INTELIGENTE DE TÍTULO (Jerarquía Estricta) ---
            texto_pista = f"{autor_raw} {rol_raw}".lower()
            prefijo = ""
            
            lista_vip = ["nelson", "oaks", "eyring", "monson", "hinckley", "hunter", "benson", "kimball", "ballard", "christofferson"]
            es_vip = any(vip in nombre_puro.lower() for vip in lista_vip)

            # 1. Presidenta (Debe ir antes de 'Hermana')
            if "presidenta" in texto_pista:
                prefijo = "la Presidenta"
            # 2. Presidente (VIPs o Primera Presidencia)
            elif "presidente" in texto_pista or "primera presidencia" in texto_pista or es_vip:
                prefijo = "el Presidente"
            # 3. Autoridades Generales
            elif "élder" in texto_pista or "elder" in texto_pista or "doce" in texto_pista or "setenta" in texto_pista or "twelve" in texto_pista or "seventy" in texto_pista:
                prefijo = "el Élder"
            # 4. Obispado Presidente
            elif "obispo" in texto_pista or "bishop" in texto_pista:
                prefijo = "el Obispo"
            # 5. Oficiales Generales (Hermanas)
            elif "hermana" in texto_pista or "sociedad de socorro" in texto_pista or "mujeres jóvenes" in texto_pista or "primaria" in texto_pista or "sister" in texto_pista:
                prefijo = "la Hermana"
            # 6. Oficiales Generales (Hermanos)
            elif "hermano" in texto_pista or "escuela dominical" in texto_pista or "hombres jóvenes" in texto_pista or "brother" in texto_pista:
                prefijo = "el Hermano"
            
            # Unimos el título deducido con el nombre limpio
            autor_final = f"{prefijo} {nombre_puro}".strip() if prefijo else nombre_puro
            
            # --- 5. VALIDACIÓN FINAL ---
            titulo = titulo.replace('\xa0', ' ').strip()
            if len(nombre_puro) > 50 or len(nombre_puro) < 3:
                logging.warning(f"⚠️ SCRAPER: Nombre inválido. Usando genérico.")
                autor_final = "un líder de la Iglesia"
            else:
                logging.info(f"👔 SCRAPER: Título asignado: [{prefijo}] | Nombre: [{nombre_puro}]")
                    
        logging.info(f"✅ SCRAPER FINALIZADO: [{autor_final}] - [{titulo}]")
        return autor_final, titulo

    except Exception as e:
        logging.error(f"💥 SCRAPER CRASH: {str(e)}")
        return "un líder de la Iglesia", "este discurso"