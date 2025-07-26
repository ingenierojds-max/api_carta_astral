# --- START OF FILE astral_calculator.py ---

import swisseph as swe
from datetime import datetime
import pytz

# --- MAPPINGS Y DATOS ASTROLÓGICOS ---
# Estos diccionarios nos ayudarán a añadir los detalles extra

SIGNOS = ["Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo", "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis"]
ELEMENTOS = ["Fuego", "Tierra", "Aire", "Agua", "Fuego", "Tierra", "Aire", "Agua", "Fuego", "Tierra", "Aire", "Agua"]
CUALIDADES = ["Cardinal", "Fijo", "Mutable", "Cardinal", "Fijo", "Mutable", "Cardinal", "Fijo", "Mutable", "Cardinal", "Fijo", "Mutable"]
CASAS_NOMBRES = [f"{i}_house" for i in ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth", "eleventh", "twelfth"]]

# --- FUNCIONES DE AYUDA ---

def _get_sign_details(longitude):
    """Devuelve un diccionario con todos los detalles de un signo a partir de una longitud."""
    sign_num = int(longitude / 30)
    return {
        "sign": SIGNOS[sign_num],
        "sign_num": sign_num,
        "position": round(longitude % 30, 4),
        "element": ELEMENTOS[sign_num],
        "quality": CUALIDADES[sign_num],
    }

def _get_house_for_point(longitude, house_cusps):
    """Determina en qué casa se encuentra un punto."""
    for i in range(12):
        cusp_actual = house_cusps[i]
        cusp_siguiente = house_cusps[(i + 1) % 12]
        
        # Manejar el cruce de Aries (0 grados)
        if cusp_actual > cusp_siguiente:
            if longitude >= cusp_actual or longitude < cusp_siguiente:
                return i + 1
        else:
            if cusp_actual <= longitude < cusp_siguiente:
                return i + 1
    return 1 # Fallback

# --- FUNCIÓN PRINCIPAL DEL CÁLCULO ---

def realizar_calculo_astral(data):
    """
    Motor de cálculo completo de la carta astral.
    """
    
    # 1. VALIDACIÓN Y PREPARACIÓN DE FECHA/HORA
    # Usamos pytz para un manejo preciso de la zona horaria
    try:
        tz = pytz.timezone("America/Argentina/Buenos_Aires") # Puedes hacer esto dinámico si recibes tz_str
        local_dt = tz.localize(datetime(data.anio, data.mes, data.dia, data.hora, data.minuto))
        utc_dt = local_dt.astimezone(pytz.utc)
        
        jd_ut = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0)
    except Exception as e:
        raise ValueError(f"Fecha/Hora inválida: {e}")

    # 2. CALCULAR CASAS Y ASCENDENTE/MC
    # Usamos el sistema de casas Placidus (b'P')
    house_cusps_raw, ascmc = swe.houses(jd_ut, data.lat, data.lng, b'P')
    house_cusps = list(house_cusps_raw)
    
    # 3. DEFINIR PUNTOS A CALCULAR
    # Usamos los índices numéricos para compatibilidad
    puntos_a_calcular = {
        "sun": {"id": 0, "nombre": "Sun", "tipo": "Planet"},
        "moon": {"id": 1, "nombre": "Moon", "tipo": "Planet"},
        "mercury": {"id": 2, "nombre": "Mercury", "tipo": "Planet"},
        "venus": {"id": 3, "nombre": "Venus", "tipo": "Planet"},
        "mars": {"id": 4, "nombre": "Mars", "tipo": "Planet"},
        "jupiter": {"id": 5, "nombre": "Jupiter", "tipo": "Planet"},
        "saturn": {"id": 6, "nombre": "Saturn", "tipo": "Planet"},
        "uranus": {"id": 7, "nombre": "Uranus", "tipo": "Planet"},
        "neptune": {"id": 8, "nombre": "Neptune", "tipo": "Planet"},
        "pluto": {"id": 9, "nombre": "Pluto", "tipo": "Planet"},
        "chiron": {"id": 15, "nombre": "Chiron", "tipo": "Planet"},
        "mean_lilith": {"id": 11, "nombre": "Mean_Lilith", "tipo": "Planet"},
        "mean_node": {"id": 10, "nombre": "Mean_Node", "tipo": "Planet"},
        "ascendant": {"longitud": ascmc[0], "nombre": "Ascendant", "tipo": "AxialCusps"},
        "medium_coeli": {"longitud": ascmc[1], "nombre": "Medium_Coeli", "tipo": "AxialCusps"},
    }
    
    # 4. CALCULAR POSICIONES DE TODOS LOS PUNTOS
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    puntos_calculados = {}

    for key, punto_info in puntos_a_calcular.items():
        if "id" in punto_info: # Si es un cuerpo celeste
            pos, ret_flags = swe.calc_ut(jd_ut, punto_info["id"], flags)
            longitud = pos[0]
            velocidad = pos[3]
            retrogrado = velocidad < 0
        else: # Si es un punto calculado como Asc/MC
            longitud = punto_info["longitud"]
            retrogrado = False

        sign_details = _get_sign_details(longitud)
        house_num = _get_house_for_point(longitud, house_cusps)
        
        puntos_calculados[key] = {
            "name": punto_info["nombre"],
            "quality": sign_details["quality"],
            "element": sign_details["element"],
            "sign": sign_details["sign"],
            "sign_num": sign_details["sign_num"],
            "position": sign_details["position"],
            "abs_pos": round(longitud, 4),
            "point_type": punto_info["tipo"],
            "house": CASAS_NOMBRES[house_num - 1].replace("_", " ").title(),
            "retrograde": retrogrado
        }

    # 5. CONSTRUIR EL OBJETO DE DATOS FINAL
    resultado = {"data": {}}
    resultado["data"]["name"] = data.nombre
    resultado["data"]["year"] = data.anio
    resultado["data"]["month"] = data.mes
    resultado["data"]["day"] = data.dia
    resultado["data"]["hour"] = data.hora
    resultado["data"]["minute"] = data.minuto
    resultado["data"]["city"] = data.ciudad
    resultado["data"]["lng"] = data.lng
    resultado["data"]["lat"] = data.lat
    resultado["data"]["tz_str"] = "America/Argentina/Buenos_Aires"
    
    # Añadir info astrológica y de tiempo
    resultado["data"]["zodiac_type"] = "Tropic"
    resultado["data"]["houses_system_name"] = "Placidus"
    resultado["data"]["iso_formatted_local_datetime"] = local_dt.isoformat()
    resultado["data"]["iso_formatted_utc_datetime"] = utc_dt.isoformat()
    resultado["data"]["julian_day"] = round(jd_ut, 6)
    
    # Añadir todos los puntos calculados
    for key, val in puntos_calculados.items():
        resultado["data"][key] = val

    # Añadir las 12 casas
    for i in range(12):
        house_key = CASAS_NOMBRES[i]
        cusp_longitud = house_cusps[i]
        sign_details = _get_sign_details(cusp_longitud)
        resultado["data"][house_key] = {
            "name": house_key.replace("_", " ").title(),
            "quality": sign_details["quality"],
            "element": sign_details["element"],
            "sign": sign_details["sign"],
            "sign_num": sign_details["sign_num"],
            "position": sign_details["position"],
            "abs_pos": round(cusp_longitud, 4),
            "point_type": "House",
            "house": None,
            "retrograde": None
        }
    
    # Añadir listas de nombres para conveniencia
    resultado["data"]["planets_names_list"] = [p["nombre"] for k, p in puntos_calculados.items() if p["point_type"] == "Planet"]
    resultado["data"]["houses_names_list"] = [h.replace("_", " ").title() for h in CASAS_NOMBRES]

    # Devolvemos solo el objeto de datos, no la estructura externa "status" y "chart"
    # FastAPI/carta_app.py envolverá esto en un formato de respuesta adecuado.
    # El usuario pidió el contenido de la API de terceros, que es este diccionario "data".
    return resultado["data"]
