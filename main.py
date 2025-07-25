from fastapi import FastAPI
from pydantic import BaseModel
import swisseph as swe
from datetime import datetime

app = FastAPI()

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

@app.post("/carta-astral")
def calcular_carta_astral(data: CartaAstralInput):
    swe.set_ephe_path(".")
    jd = swe.julday(data.anio, data.mes, data.dia, data.hora + data.minuto / 60.0)

    planetas = ["Sol", "Luna", "Mercurio", "Venus", "Marte", "Júpiter", "Saturno", "Urano", "Neptuno", "Plutón"]
    posiciones = {}

    for i in range(10):
        pos, _ = swe.calc_ut(jd, i)
        posiciones[planetas[i]] = round(pos[0], 2)

    return {
        "nombre": data.nombre,
        "fecha": f"{data.dia}/{data.mes}/{data.anio} {data.hora}:{data.minuto}",
        "posiciones": posiciones
    }
