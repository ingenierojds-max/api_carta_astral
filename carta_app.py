# --- START OF FILE carta_app.py ---

from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
import swisseph as swe
import os

# Importamos la función de cálculo desde nuestro motor
from astral_calculator import realizar_calculo_astral

app = FastAPI()

# ==============================================================================
# ======>  BLOQUE DE CONFIGURACIÓN DE EFEMÉRIDES (ESTA ES LA SOLUCIÓN)  <======
# ==============================================================================
# Le decimos a la aplicación dónde están los archivos de datos que descargamos.

# Directorio donde nuestro script de build descarga los archivos de efemérides
EPH_PATH = "ephe"

# Configurar swisseph para que encuentre los archivos en esa ruta
try:
    if os.path.exists(EPH_PATH):
        swe.set_ephe_path(EPH_PATH)
        # Este print aparecerá en los logs de Railway y nos confirmará que todo va bien
        print(f"✓ Ruta de efemérides configurada correctamente en: '{EPH_PATH}'")
    else:
        # Esto nos avisaría si la carpeta no se creó por alguna razón
        print(f"⚠️  ADVERTENCIA: El directorio de efemérides '{EPH_PATH}' no fue encontrado.")
except Exception as e:
    print(f"❌ ERROR CRÍTICO configurando la ruta de efemérides: {e}")

# ==============================================================================

# Leer la clave secreta desde las variables de entorno
API_KEY_SECRET = os.getenv("API_KEY")

# Función "guardián" para la seguridad (esto ya está bien)
async def get_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY_SECRET:
        raise HTTPException(status_code=401, detail="Invalid API Key")

# El modelo de entrada no cambia
class CartaAstralInput(BaseModel):
    nombre: str
    anio: int
    mes: int
    dia: int
    hora: int
    minuto: int
    ciudad: str
    lat: float
    lng: float

# El endpoint raíz no cambia
@app.get("/")
def read_root():
    return {"status": "Servidor de Carta Astral funcionando correctamente"}

# El endpoint principal, protegido con la clave de API
@app.post("/carta-astral", dependencies=[Depends(get_api_key)])
def calcular_carta_astral_endpoint(data: CartaAstralInput):
    """
    Este endpoint recibe los datos, los pasa al motor de cálculo y devuelve el resultado.
    """
    try:
        resultado_calculado = realizar_calculo_astral(data)
        return resultado_calculado
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        # Capturamos cualquier error interno del motor de cálculo
        print(f"ERROR en el motor de cálculo: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno al calcular la carta astral: {str(e)}")
