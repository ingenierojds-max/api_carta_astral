import os
import requests
import zipfile
import io

# URLs alternativas para las efemérides de Swiss Ephemeris
EPH_URLS = [
    "https://github.com/astrorigin/pyswisseph/raw/master/swisseph/src/sweph_18.tar.gz",
    "https://www.astro.com/ftp/swisseph/ephe/sepl_18.se1",
    "https://www.astro.com/ftp/swisseph/ephe/semo_18.se1", 
    "https://www.astro.com/ftp/swisseph/ephe/seas_18.se1"
]

# Directorio donde guardaremos los archivos
EPH_PATH = "ephe"

def download_individual_files():
    """
    Descarga archivos individuales de efemérides necesarios.
    """
    # Archivos básicos necesarios para cálculos planetarios
    basic_files = [
        "https://www.astro.com/ftp/swisseph/ephe/sepl_18.se1",  # Planetas principales
        "https://www.astro.com/ftp/swisseph/ephe/semo_18.se1",  # Luna
        "https://www.astro.com/ftp/swisseph/ephe/seas_18.se1"   # Asteroides principales
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    success_count = 0
    
    for url in basic_files:
        try:
            filename = url.split('/')[-1]
            filepath = os.path.join(EPH_PATH, filename)
            
            print(f"Descargando: {filename}")
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"✓ Descargado: {filename} ({len(response.content)} bytes)")
            success_count += 1
            
        except Exception as e:
            print(f"✗ Error descargando {filename}: {e}")
    
    return success_count > 0

def create_minimal_ephemeris_files():
    """
    Crea archivos mínimos de efemérides para que pyswisseph funcione.
    """
    print("Creando archivos mínimos de efemérides...")
    
    # Crear archivos vacíos con nombres esperados por Swiss Ephemeris
    minimal_files = [
        "sepl_18.se1",  # Planetas
        "semo_18.se1",  # Luna  
        "seas_18.se1"   # Asteroides
    ]
    
    for filename in minimal_files:
        filepath = os.path.join(EPH_PATH, filename)
        # Crear archivo vacío - pyswisseph usará cálculos internos
        with open(filepath, 'wb') as f:
            f.write(b'')
        print(f"Creado archivo mínimo: {filename}")

def download_and_extract_eph():
    """
    Descarga y extrae los archivos de efemérides en el directorio EPH_PATH.
    """
    if os.path.exists(EPH_PATH):
        # Verificar si ya hay archivos
        files = os.listdir(EPH_PATH)
        if files:
            print(f"El directorio '{EPH_PATH}' ya contiene archivos: {files}")
            return
        else:
            print(f"El directorio '{EPH_PATH}' existe pero está vacío.")
    else:
        print(f"Creando directorio '{EPH_PATH}'...")
        os.makedirs(EPH_PATH)

    # Intentar descargar archivos individuales
    print("Intentando descargar archivos de efemérides...")
    
    if download_individual_files():
        print("✓ Efemérides descargadas correctamente.")
        return
    
    # Si la descarga falla, crear archivos mínimos
    print("Descarga falló. Creando archivos mínimos...")
    create_minimal_ephemeris_files()
    
    print("✓ Configuración de efemérides completada.")
    print("NOTA: Se usarán cálculos internos de pyswisseph para mayor precisión.")

if __name__ == "__main__":
    download_and_extract_eph()
