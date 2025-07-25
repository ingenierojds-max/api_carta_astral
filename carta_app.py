from fastapi import FastAPI
from pydantic import BaseModel
import swisseph as swe
import os

app = FastAPI()

# --- CONFIGURACIÓN INICIAL ---
# Directorio donde nuestro script de build descargó los archivos de efemérides
EPH_PATH = "ephe"

# Le decimos a swisseph dónde encontrar esos archivos.
# Esto se hace una sola vez cuando la aplicación se inicia.
if os.path.exists(EPH_PATH):
    swe.set_ephe_path(EPH_PATH)
    print(f"Ruta de efemérides configurada en: '{EPH_PATH}'")
else:
    # Esto no debería pasar en Railway si el Build Command es correcto,
    # pero es una advertencia útil si ejecutas esto localmente sin los archivos.
    print(f"ADVERTENCIA: El directorio de efemérides '{EPH_PATH}' no fue encontrado.")
    print("La aplicación puede fallar. Ejecuta 'python download_eph.py' para descargarlos.")
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
    return {"status": "Servidor de Carta Astral funcionando correctamente"}


@app.post("/carta-astral")
def calcular_carta_astral(data: CartaAstralInput):
    # Calcula el Día Juliano (UT) a partir de los datos de entrada
    jd_ut = swe.julday(data.anio, data.mes, data.dia, data.hora + data.minuto / 60.0)
    
    planetas = {
        "Sol": swe.SOL, "Luna": swe.LUNA, "Mercurio": swe.MERCURIO,
        "Venus": swe.VENUS, "Marte": swe.MARTE, "Júpiter": swe.JUPITER,
        "Saturno": swe.SATURNO, "Urano": swe.URANO, "Neptuno": swe.NEPTUNO,
        "Plutón": swe.PLUTON
    }
    
    posiciones = {}
    
    # Flags para el cálculo: usar efemérides suizas de alta precisión
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    
    for nombre, planeta_id in planetas.items():
        # calc_ut calcula la posición del planeta para el tiempo universal dado
        pos, _ = swe.calc_ut(jd_ut, planeta_id, flags)
        # pos[0] es la longitud eclíptica en grados
        posiciones[nombre] = round(pos[0], 2)
        
    return {
        "nombre": data.nombre,
        "fecha_utc": f"{data.dia}/{data.mes}/{data.anio} {data.hora:02d}:{data.minuto:02d}",
        "ciudad": data.ciudad,
        "posiciones_planetarias_grados": posiciones
    }