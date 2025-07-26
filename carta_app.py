# --- START OF FILE carta_app.py ---

# ======> PASO 1: Importa lo necesario de FastAPI y `os` para leer variables de entorno <======
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
import swisseph as swe
import os

from astral_calculator import realizar_calculo_astral

app = FastAPI()

# --- CONFIGURACIÓN INICIAL (Esto no cambia) ---
# ... (todo tu bloque de configuración de swisseph se queda igual) ...
EPH_PATH = "ephe"
swe.set_ephe_path(EPH_PATH)
# ... etc ...

# ======> PASO 2: Leer la clave secreta desde las variables de entorno <======
API_KEY_SECRET = os.getenv("API_KEY")

# ======> PASO 3: Crear la función "guardián" (Dependencia) <======
async def get_api_key(x_api_key: str = Header(None)):
    """
    Verifica que la cabecera x-api-key enviada por el cliente
    coincide con nuestra clave secreta.
    """
    if not API_KEY_SECRET:
        # Si no hemos configurado una clave en el servidor, la seguridad está desactivada.
        # Esto es útil para desarrollo local. En producción, SIEMPRE debe estar definida.
        print("ADVERTENCIA: No se ha definido una API_KEY en el entorno. La API no es segura.")
        return

    if x_api_key != API_KEY_SECRET:
        # Si las claves no coinciden, lanza un error 401 Unauthorized.
        raise HTTPException(status_code=401, detail="Invalid API Key")

# --- Modelos y Endpoints que no necesitan protección ---
class CartaAstralInput(BaseModel):
    # ... (esto no cambia) ...
    nombre: str
    anio: int
    mes: int
    dia: int
    hora: int
    minuto: int
    ciudad: str
    lat: float
    lng: float

@app.get("/")
def read_root():
    # ... (esto no cambia) ...
    return {"status": "Servidor de Carta Astral funcionando correctamente"}

@app.get("/health")
def health_check():
    # ... (esto no cambia) ...
    return {"status": "healthy"}


# ======> PASO 4: Proteger el endpoint importante <======
# Añadimos `dependencies=[Depends(get_api_key)]` para activar el guardián.
@app.post("/carta-astral", dependencies=[Depends(get_api_key)])
def calcular_carta_astral_endpoint(data: CartaAstralInput):
    """
    Este endpoint AHORA está protegido. Solo se ejecutará si la clave de API es correcta.
    """
    try:
        resultado_calculado = realizar_calculo_astral(data)
        return resultado_calculado
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"ERROR en el motor de cálculo: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno al calcular la carta astral: {str(e)}")

# El bloque para correr localmente no cambia
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)