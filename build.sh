#!/bin/bash
set -e

echo "=== Iniciando build de Carta Astral Expandida ==="

# Definir la ruta raíz del proyecto
export APP_DIR=$(pwd)

# Instalar dependencias de Python
echo "Instalando dependencias..."
pip install --no-cache-dir -r requirements.txt

# Crear directorio de efemérides si no existe
echo "Creando directorio de efemérides..."
mkdir -p ephe

# Ejecutar script de descarga de efemérides
echo "Configurando efemérides..."
python download_eph.py

# Verificar instalación de pyswisseph
echo "Verificando pyswisseph..."
python -c "import sys; sys.path.append('$APP_DIR'); import carta_app.py; print('✓ carta_app importado correctamente')"

# Verificar que los archivos fueron creados
echo "Verificando archivos de efemérides..."
ls -la ephe/ || echo "Directorio ephe no encontrado"

# Probar importación del calculador
echo "Probando importación del calculador..."
python -c "import sys; sys.path.append('$APP_DIR'); from astral_calculator import realizar_calculo_astral; print('✓ Calculador importado correctamente')"

echo "=== Build completado exitosamente ==="

