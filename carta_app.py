# --- START OF FILE carta_app.py ---

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.responses import FileResponse
from pydantic import BaseModel
import swisseph as swe
import os
import tempfile
from pathlib import Path

# Importar nuestros módulos (ACTUALIZADO - usar el nombre correcto de tu archivo)
from astral_calculator import realizar_calculo_astral
from generador_carta_astral_visual import generar_carta_astral_imagen

app = FastAPI()

# --- CONFIGURACIÓN INICIAL ---
EPH_PATH = "ephe"
swe.set_ephe_path(EPH_PATH)

# ======> PASO 2: Leer la clave secreta desde las variables de entorno <======
API_KEY_SECRET = os.getenv("API_KEY")

# ======> PASO 3: Crear la función "guardián" (Dependencia) <======
async def get_api_key(x_api_key: str = Header(None)):
    """
    Verifica que la cabecera x-api-key enviada por el cliente
    coincide con nuestra clave secreta.
    """
    if not API_KEY_SECRET:
        print("ADVERTENCIA: No se ha definido una API_KEY en el entorno. La API no es segura.")
        return

    if x_api_key != API_KEY_SECRET:
        raise HTTPException(status_code=401, detail="Invalid API Key")

# --- Modelos ---
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

@app.get("/")
def read_root():
    return {"status": "Servidor de Carta Astral funcionando correctamente"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# ======> ENDPOINT EXISTENTE (JSON) <======
@app.post("/carta-astral", dependencies=[Depends(get_api_key)])
def calcular_carta_astral_endpoint(data: CartaAstralInput):
    """
    Endpoint existente que devuelve los datos JSON de la carta astral.
    """
    try:
        resultado_calculado = realizar_calculo_astral(data)
        return resultado_calculado
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"ERROR en el motor de cálculo: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno al calcular la carta astral: {str(e)}")

# ======> NUEVO ENDPOINT (IMAGEN) <======
@app.post("/carta-astral/imagen", dependencies=[Depends(get_api_key)])
def generar_carta_astral_imagen_endpoint(data: CartaAstralInput):
    """
    NUEVO: Endpoint que genera y devuelve la imagen de la carta astral.
    
    Uso:
    POST /carta-astral/imagen
    Headers: x-api-key: tu_clave_secreta
    Body: {mismo JSON que el endpoint anterior}
    
    Respuesta: Archivo PNG de la carta astral
    """
    try:
        # 1. Calcular los datos de la carta
        datos_carta = realizar_calculo_astral(data)
        
        # 2. Crear archivo temporal para la imagen
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            temp_path = tmp_file.name
        
        # 3. Generar la imagen
        generar_carta_astral_imagen(datos_carta, temp_path, tamaño_figura=(10, 10))
        
        # 4. Verificar que el archivo se creó
        if not os.path.exists(temp_path):
            raise HTTPException(status_code=500, detail="Error generando la imagen")
        
        # 5. Devolver la imagen como respuesta
        filename = f"carta_astral_{data.nombre.replace(' ', '_')}.png"
        
        def cleanup():
            """Limpiar archivo temporal después de enviar la respuesta"""
            try:
                os.unlink(temp_path)
            except:
                pass
        
        return FileResponse(
            path=temp_path,
            media_type='image/png',
            filename=filename,
            background=cleanup  # Limpia automáticamente después del envío
        )
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"ERROR generando imagen: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno generando imagen: {str(e)}")

# ======> ENDPOINT COMBINADO (JSON + URL de imagen) <======
@app.post("/carta-astral/completa", dependencies=[Depends(get_api_key)])
def generar_carta_completa_endpoint(data: CartaAstralInput):
    """
    NUEVO: Endpoint que devuelve tanto los datos JSON como guarda la imagen.
    
    Respuesta:
    {
        "datos_carta": {...},
        "imagen_generada": true,
        "mensaje": "Carta astral calculada e imagen generada exitosamente"
    }
    """
    try:
        # 1. Calcular los datos
        datos_carta = realizar_calculo_astral(data)
        
        # 2. Crear directorio para imágenes si no existe
        images_dir = Path("generated_charts")
        images_dir.mkdir(exist_ok=True)
        
        # 3. Generar nombre de archivo único
        filename = f"carta_{data.nombre.replace(' ', '_')}_{data.anio}_{data.mes}_{data.dia}.png"
        image_path = images_dir / filename
        
        # 4. Generar la imagen
        generar_carta_astral_imagen(datos_carta, str(image_path), tamaño_figura=(10, 10))
        
        # 5. Respuesta completa
        return {
            "datos_carta": datos_carta,
            "imagen_generada": os.path.exists(image_path),
            "imagen_filename": filename,
            "mensaje": "Carta astral calculada e imagen generada exitosamente"
        }
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"ERROR en carta completa: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
