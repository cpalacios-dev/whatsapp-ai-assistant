# 1. Imagen oficial de Python estable (3.12 como configuramos en tu PC)
FROM python:3.12-slim

# 2. Instalamos dependencias del sistema necesarias para Playwright/Browsers
# Las distros 'slim' son ligeras pero no traen librerías de sistema para navegadores
RUN apt-get update && apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    librandr2 \
    libgbm1 \
    libasound2 \
    libpangocairo-1.0-0 \
    libxml2 \
    && rm -rf /var/lib/apt/lists/*

# 3. Directorio de trabajo
WORKDIR /app

# 4. Instalamos las librerías de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. PASO CRUCIAL: Instalamos el navegador dentro del contenedor
# Sin esto, Playwright fallará porque no encontrará Chromium
RUN playwright install chromium
RUN playwright install-deps chromium

# 6. Copiamos el resto del proyecto
# Importante: El .gitignore evitará que se copien carpetas pesadas como __pycache__
COPY . .

# 7. Exponemos el puerto que usa Streamlit (8501 por defecto)
EXPOSE 8501

# 8. Comando para ejecutar el Dashboard (UI)
# Usamos el flag --server.address=0.0.0.0 para que sea accesible desde fuera del contenedor
CMD ["streamlit", "run", "app/ui/dashboard.py", "--server.address=0.0.0.0"]