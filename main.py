from fastapi import FastAPI, Query
import swisseph as swe
from datetime import datetime

app = FastAPI()

ZODIAC_SIGNS = [
    "Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo",
    "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis"
]

SIGN_TRAITS = {
    "Aries": "valiente, impulsivo y energético",
    "Tauro": "estable, práctico y sensual",
    "Géminis": "comunicativo, versátil e ingenioso",
    "Cáncer": "emocional, protector e intuitivo",
    "Leo": "líder, creativo y generoso",
    "Virgo": "analítico, perfeccionista y servicial",
    "Libra": "diplomático, armonioso y justo",
    "Escorpio": "intenso, profundo y transformador",
    "Sagitario": "aventurero, optimista y sabio",
    "Capricornio": "disciplinado, ambicioso y realista",
    "Acuario": "innovador, independiente y humanitario",
    "Piscis": "empático, espiritual y soñador"
}

def zodiac_sign(degree):
    return ZODIAC_SIGNS[int(degree / 30) % 12]

@app.get("/")
def root():
    return {"msg": "API de Carta Astral lista ✨"}

@app.get("/carta_astral")
def calcular_carta(
    dia: int = Query(...),
    mes: int = Query(...),
    anio: int = Query(...),
    hora: int = Query(...),
    minuto: int = Query(...),
    lat: float = Query(...),
    lon: float = Query(...)
):
    swe.set_ephe_path(swe.__file__)
    jd = swe.julday(anio, mes, dia, hora + minuto / 60.0)
    resultado = {
        "fecha": f"{dia:02d}/{mes:02d}/{anio}",
        "hora_local": f"{hora:02d}:{minuto:02d}",
        "julian_day": jd,
        "coordenadas": {"lat": lat, "lon": lon},
        "planetas": {},
        "casas": {},
        "ascendente": {}
    }

    # Planetas
    planetas = {
        "Sol": swe.SUN,
        "Luna": swe.MOON,
        "Mercurio": swe.MERCURY,
        "Venus": swe.VENUS,
        "Marte": swe.MARS,
        "Júpiter": swe.JUPITER,
        "Saturno": swe.SATURN,
        "Urano": swe.URANUS,
        "Neptuno": swe.NEPTUNE,
        "Plutón": swe.PLUTO
    }

    for nombre, id_planeta in planetas.items():
        pos, _ = swe.calc_ut(jd, id_planeta)
        signo = zodiac_sign(pos[0])
        resultado["planetas"][nombre] = {
            "grados": round(pos[0], 2),
            "signo": signo,
            "interpretacion": SIGN_TRAITS[signo]
        }

    # Casas y Ascendente
    casas, ascmc = swe.houses(jd, lat, lon)
    for i, pos in enumerate(casas, start=1):
        signo = zodiac_sign(pos)
        resultado["casas"][f"Casa {i}"] = {
            "grados": round(pos, 2),
            "signo": signo
        }

    signo_asc = zodiac_sign(ascmc[0])
    resultado["ascendente"] = {
        "grados": round(ascmc[0], 2),
        "signo": signo_asc,
        "interpretacion": SIGN_TRAITS[signo_asc]
    }

    return resultado
