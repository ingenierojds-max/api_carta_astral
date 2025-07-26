from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import swisseph as swe
import os
from typing import Optional

from astral_calculator import realizar_calculo_astral

app = FastAPI(
    title="API de Carta Astral Expandida",
    description="API completa para cálculo de cartas astrales con planetas, casas, aspectos y más",
    version="2.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de Swiss Ephemeris
EPH_PATH = "ephe"
if os.path.exists(EPH_PATH):
    swe.set_ephe_path(EPH_PATH)
    print(f"✓ Ruta de efemérides configurada: {EPH_PATH}")
else:
    print("⚠ Directorio de efemérides no encontrado, usando cálculos internos")

# Configuración de seguridad API
API_KEY_SECRET = os.getenv("API_KEY")

async def get_api_key(x_api_key: str = Header(None)):
    """Verifica la clave de API si está configurada."""
    if not API_KEY_SECRET:
        print("⚠ ADVERTENCIA: No se ha definido una API_KEY en el entorno")
        return
    
    if x_api_key != API_KEY_SECRET:
        raise HTTPException(status_code=401, detail="Clave de API inválida")

# Modelos de datos
class CartaAstralInput(BaseModel):
    nombre: str = Field(..., description="Nombre de la persona")
    anio: int = Field(..., ge=1900, le=2100, description="Año de nacimiento")
    mes: int = Field(..., ge=1, le=12, description="Mes de nacimiento")
    dia: int = Field(..., ge=1, le=31, description="Día de nacimiento")
    hora: int = Field(..., ge=0, le=23, description="Hora de nacimiento (formato 24h)")
    minuto: int = Field(..., ge=0, le=59, description="Minuto de nacimiento")
    ciudad: str = Field(..., description="Ciudad de nacimiento")
    lat: float = Field(..., ge=-90, le=90, description="Latitud")
    lng: float = Field(..., ge=-180, le=180, description="Longitud")

    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "María García",
                "anio": 1990,
                "mes": 5,
                "dia": 15,
                "hora": 14,
                "minuto": 30,
                "ciudad": "Buenos Aires",
                "lat": -34.6118,
                "lng": -58.3960
            }
        }

# Endpoints públicos
@app.get("/", tags=["Sistema"])
def read_root():
    """Endpoint de verificación del estado del servidor."""
    return {
        "mensaje": "🌟 Servidor de Carta Astral Expandida funcionando correctamente",
        "version": "2.0.0",
        "funcionalidades": [
            "Posiciones planetarias detalladas",
            "Casas astrológicas",
            "Aspectos entre planetas",
            "Distribución por elementos y modalidades",
            "Ángulos importantes (ASC, MC, DSC, IC)",
            "Puntos especiales (Nodos, Quirón, Lilith)"
        ]
    }

@app.get("/health", tags=["Sistema"])
def health_check():
    """Verificación de salud del sistema."""
    try:
        # Probar pyswisseph
        import swisseph as swe
        version = swe.version
        
        # Probar cálculo básico
        jd = swe.julday(2000, 1, 1, 12.0)
        
        return {
            "status": "healthy",
            "pyswisseph_version": version,
            "ephemeris_path": EPH_PATH,
            "test_julian_day": jd
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sistema no saludable: {str(e)}")

@app.get("/info", tags=["Sistema"])
def get_system_info():
    """Información detallada del sistema."""
    try:
        import swisseph as swe
        
        # Verificar archivos de efemérides
        ephe_files = []
        if os.path.exists(EPH_PATH):
            ephe_files = os.listdir(EPH_PATH)
        
        return {
            "pyswisseph_version": swe.version,
            "ephemeris_path": EPH_PATH,
            "ephemeris_files": ephe_files,
            "api_protection": "Activada" if API_KEY_SECRET else "Desactivada",
            "supported_calculations": [
                "Planetas tradicionales y modernos",
                "Nodos lunares",
                "Quirón y Lilith",
                "Casas astrológicas (sistema Placidus)",
                "Aspectos principales con orbes",
                "Distribuciones estadísticas"
            ]
        }
    except Exception as e:
        return {"error": f"Error obteniendo información: {str(e)}"}

# Endpoint principal protegido
@app.post("/carta-astral", dependencies=[Depends(get_api_key)], tags=["Carta Astral"])
def calcular_carta_astral_endpoint(data: CartaAstralInput):
    """
    Calcula una carta astral completa con todos los datos astrológicos.
    
    Incluye:
    - Posiciones planetarias en signos y casas
    - Casas astrológicas con cúspides
    - Aspectos principales entre planetas
    - Distribución por elementos y modalidades
    - Ángulos importantes del tema natal
    - Puntos especiales (Nodos, Quirón, Lilith)
    """
    try:
        resultado = realizar_calculo_astral(data)
        return {
            "success": True,
            "data": resultado,
            "mensaje": "Carta astral calculada exitosamente"
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail={
            "error": "Datos de entrada inválidos",
            "detalle": str(ve)
        })
    except Exception as e:
        print(f"ERROR en el motor de cálculo: {e}")
        raise HTTPException(status_code=500, detail={
            "error": "Error interno del servidor",
            "detalle": f"Error al calcular la carta astral: {str(e)}"
        })

# Endpoint para validar datos sin calcular
@app.post("/validar-datos", tags=["Utilidades"])
def validar_datos_entrada(data: CartaAstralInput):
    """Valida los datos de entrada sin realizar cálculos."""
    try:
        # Las validaciones de Pydantic ya se ejecutaron
        return {
            "valido": True,
            "mensaje": "Datos válidos para cálculo de carta astral",
            "datos_recibidos": {
                "nombre": data.nombre,
                "fecha": f"{data.dia:02d}/{data.mes:02d}/{data.anio}",
                "hora": f"{data.hora:02d}:{data.minuto:02d}",
                "lugar": data.ciudad,
                "coordenadas": f"{data.lat}, {data.lng}"
            }
        }
    except Exception as e:
        return {
            "valido": False,
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    # Usar puerto desde variable de entorno o 8000 por defecto
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)