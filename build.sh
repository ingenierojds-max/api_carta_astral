#!/bin/bash

# Script de build para Railway
echo "=== Iniciando build de Carta Astral ==="

# Instalar dependencias de Python
echo "Instalando dependencias..."
pip install -r requirements.txt

# Ejecutar script de descarga de efemérides
echo "Configurando efemérides..."
python download_eph.py

# Verificar que los archivos fueron creados
echo "Verificando archivos de efemérides..."
ls -la ephe/ || echo "Directorio ephe no encontrado"

echo "=== Build completado ==="
