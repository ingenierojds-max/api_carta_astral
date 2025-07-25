from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import swisseph as swe
import os

app = FastAPI()

# --- CONFIGURACIÓN INICIAL ---
# Directorio donde nuestro script de build descargó los archivos de efemérides
EPH_PATH = "ephe"

# Configurar swisseph
try:
    if os.path.exists(EPH_PATH):
        swe.set_ephe_path(EPH_PATH)
        print(f"✓ Ruta de efemérides configurada en: '{EPH_PATH}'")
        
        # Verificar archivos disponibles
        files = os.listdir(EPH_PATH)
        print(f"Archivos de efemérides encontrados: {files}")
    else:
        print(f"⚠️  Directorio '{EPH_PATH}' no encontrado. Usando cálculos internos.")
        
    # Hacer una prueba rápida de cálculo
    test_jd = swe.julday(2024, 1, 1, 12.0)
    test_pos, _ = swe.calc_ut(test_jd, swe.SOL, swe.FLG_SWIEPH)
    print(f"✓ Swiss Ephemeris funcionando correctamente. Sol en test: {test_pos[0]:.2f}°")
    
except Exception as e:
    print(f"❌ Error configurando Swiss Ephemeris: {e}")
    print("La aplicación puede tener problemas de precisión.")

# --- FIN DE CONFIGURACIÓN ---

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

# Endpoint raíz para verificar que el servidor está funcionando
@app.get("/")
def read_root():
    return {
        "status": "Servidor de Carta Astral funcionando correctamente",
        "ephemeris_path": EPH_PATH,
        "ephemeris_available": os.path.exists(EPH_PATH)
    }

@app.get("/health")
def health_check():
    """Endpoint de salud para verificar que todo funciona"""
    try:
        # Prueba rápida de cálculo
        test_jd = swe.julday(2024, 1, 1, 12.0)
        test_pos, _ = swe.calc_ut(test_jd, swe.SOL, swe.FLG_SWIEPH)
        
        return {
            "status": "healthy",
            "swisseph_working": True,
            "ephemeris_path": EPH_PATH,
            "test_calculation": f"Sol: {test_pos[0]:.2f}°"
        }
    except Exception as e:
        return {
            "status": "error",
            "swisseph_working": False,
            "error": str(e)
        }

@app.post("/carta-astral")
def calcular_carta_astral(data: CartaAstralInput):
    try:
        # Validar fechas
        if not (1900 <= data.anio <= 2100):
            raise HTTPException(status_code=400, detail="Año debe estar entre 1900 y 2100")
        if not (1 <= data.mes <= 12):
            raise HTTPException(status_code=400, detail="Mes debe estar entre 1 y 12")
        if not (1 <= data.dia <= 31):
            raise HTTPException(status_code=400, detail="Día debe estar entre 1 y 31")
        if not (0 <= data.hora <= 23):
            raise HTTPException(status_code=400, detail="Hora debe estar entre 0 y 23")
        if not (0 <= data.minuto <= 59):
            raise HTTPException(status_code=400, detail="Minuto debe estar entre 0 y 59")
        
        # Calcula el Día Juliano (UT) a partir de los datos de entrada
        jd_ut = swe.julday(data.anio, data.mes, data.dia, data.hora + data.minuto / 60.0)
        
        planetas = {
            "Sol": swe.SOL, 
            "Luna": swe.LUNA, 
            "Mercurio": swe.MERCURIO,
            "Venus": swe.VENUS, 
            "Marte": swe.MARTE, 
            "Júpiter": swe.JUPITER,
            "Saturno": swe.SATURNO, 
            "Urano": swe.URANO, 
            "Neptuno": swe.NEPTUNO,
            "Plutón": swe.PLUTON
        }
        
        posiciones = {}
        errores = []
        
        # Flags para el cálculo: usar efemérides suizas de alta precisión
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED
        
        for nombre, planeta_id in planetas.items():
            try:
                # calc_ut calcula la posición del planeta para el tiempo universal dado
                pos, _ = swe.calc_ut(jd_ut, planeta_id, flags)
                # pos[0] es la longitud eclíptica en grados
                posiciones[nombre] = round(pos[0], 2)
            except Exception as e:
                errores.append(f"Error calculando {nombre}: {str(e)}")
                # Usar valor por defecto si hay error
                posiciones[nombre] = 0.0
        
        # Calcular signos zodiacales
        signos = ["Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo", 
                 "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis"]
        
        posiciones_con_signos = {}
        for planeta, grados in posiciones.items():
            signo_index = int(grados // 30)
            grados_en_signo = grados % 30
            posiciones_con_signos[planeta] = {
                "grados_totales": grados,
                "signo": signos[signo_index],
                "grados_en_signo": round(grados_en_signo, 2)
            }
        
        resultado = {
            "nombre": data.nombre,
            "fecha_utc": f"{data.dia:02d}/{data.mes:02d}/{data.anio} {data.hora:02d}:{data.minuto:02d}",
            "ciudad": data.ciudad,
            "coordenadas": {"lat": data.lat, "lng": data.lng},
            "posiciones_planetarias": posiciones_con_signos,
            "dia_juliano": round(jd_ut, 2)
        }
        
        if errores:
            resultado["advertencias"] = errores
            
        return resultado
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculando carta astral: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
