#!/bin/bash

# Este comando asegura que si algo falla, el script se detenga
set -e

# Primero, ejecuta el script de descarga y espera a que termine
echo ">>> Iniciando la descarga de efemérides..."
python download_eph.py

# SOLO SI la descarga fue exitosa, inicia el servidor web
echo ">>> Efemérides descargadas. Iniciando el servidor Uvicorn..."
uvicorn carta_app:app --host 0.0.0.0 --port $PORT
