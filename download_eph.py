import os
import requests
import zipfile
import io

# URL del archivo zip de las efemérides básicas de Swiss Ephemeris
EPH_URL = "https://www.astro.com/ftp/swisseph/ephe/sweph.zip"
# Directorio donde guardaremos los archivos
EPH_PATH = "ephe"

def download_and_extract_eph():
    """
    Descarga y extrae los archivos de efemérides en el directorio EPH_PATH.
    """
    if os.path.exists(EPH_PATH):
        print(f"El directorio '{EPH_PATH}' ya existe. No se necesita descarga.")
        return

    print(f"Directorio '{EPH_PATH}' no encontrado. Descargando efemérides...")
    os.makedirs(EPH_PATH)

    try:
        print(f"Descargando desde: {EPH_URL}")
        response = requests.get(EPH_URL, stream=True)
        response.raise_for_status()  # Lanza un error si la descarga falla

        # Usamos io.BytesIO para tratar el contenido descargado como un archivo en memoria
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            z.extractall(EPH_PATH)
        
        print("Efemérides descargadas y extraídas correctamente en el directorio 'ephe'.")

    except requests.exceptions.RequestException as e:
        print(f"Error al descargar los archivos: {e}")
        exit(1)
    except zipfile.BadZipFile:
        print("Error: El archivo descargado no es un zip válido.")
        exit(1)

if __name__ == "__main__":
    download_and_extract_eph()