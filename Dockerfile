# Usar Python 3.11 como base
FROM python:3.11-slim

# Instalar dependencias del sistema necesarias para pyswisseph
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements primero para aprovechar caché de Docker
COPY requirements.txt .

# Actualizar pip e instalar dependencias de Python
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copiar archivos necesarios para el build
COPY build.sh .
COPY download_eph.py .

# Hacer ejecutable el script de build
RUN chmod +x build.sh

# Ejecutar script de configuración (solo efemérides)
RUN ./build.sh

# Copiar el resto del código después del build
COPY . .

# Crear variable de entorno por defecto
ENV PORT=8000

# Exponer puerto
EXPOSE $PORT

# Comando para iniciar la aplicación
CMD uvicorn carta_app:app --host 0.0.0.0 --port $PORT
