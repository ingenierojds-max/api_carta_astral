# --- START OF FILE astral_calculator.py ---

import swisseph as swe

# La clase BaseModel no es necesaria aquí, pero si la usáramos para type-hinting,
# la importaríamos. Por simplicidad, asumimos que 'data' tiene los atributos correctos.

def realizar_calculo_astral(data):
    """
    Motor de cálculo de la carta astral.
    Recibe un objeto de datos y devuelve un diccionario con el resultado.
    Lanza un ValueError si los datos de entrada no son válidos.
    """
    
    # 1. Validar fechas (Esta lógica ahora vive aquí)
    if not (1900 <= data.anio <= 2100):
        raise ValueError("Año debe estar entre 1900 y 2100")
    if not (1 <= data.mes <= 12):
        raise ValueError("Mes debe estar entre 1 y 12")
    if not (1 <= data.dia <= 31):
        raise ValueError("Día debe estar entre 1 y 31")
    if not (0 <= data.hora <= 23):
        raise ValueError("Hora debe estar entre 0 y 23")
    if not (0 <= data.minuto <= 59):
        raise ValueError("Minuto debe estar entre 0 y 59")
    
    # 2. Calcula el Día Juliano (UT) a partir de los datos de entrada
    jd_ut = swe.julday(data.anio, data.mes, data.dia, data.hora + data.minuto / 60.0)
    
    planetas = {
        "Sol": swe.SOL, "Luna": swe.LUNA, "Mercurio": swe.MERCURIO,
        "Venus": swe.VENUS, "Marte": swe.MARTE, "Júpiter": swe.JUPITER,
        "Saturno": swe.SATURNO, "Urano": swe.URANO, "Neptuno": swe.NEPTUNO,
        "Plutón": swe.PLUTON
    }
    
    posiciones = {}
    errores = []
    
    # Flags para el cálculo: usar efemérides suizas de alta precisión
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    
    for nombre, planeta_id in planetas.items():
        try:
            pos, _ = swe.calc_ut(jd_ut, planeta_id, flags)
            posiciones[nombre] = round(pos[0], 2)
        except Exception as e:
            errores.append(f"Error calculando {nombre}: {str(e)}")
            posiciones[nombre] = 0.0
    
    # 3. Calcular signos zodiacales
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
    
    # 4. Construir el objeto de resultado final
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
        
    # 5. Devolver el diccionario con el resultado
    return resultado