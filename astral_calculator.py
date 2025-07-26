# --- START OF FILE astral_calculator.py ---

import swisseph as swe

def realizar_calculo_astral(data):
    """
    Motor de cálculo de la carta astral.
    Recibe un objeto de datos y devuelve un diccionario con el resultado.
    Lanza un ValueError si los datos de entrada no son válidos.
    """
    
    # 1. Validar fechas
    if not (1900 <= data.anio <= 2100):
        raise ValueError("Año debe estar entre 1900 y 2100")
    # ... (el resto de las validaciones de fecha se quedan igual) ...
    if not (1 <= data.mes <= 12):
        raise ValueError("Mes debe estar entre 1 y 12")
    if not (1 <= data.dia <= 31):
        raise ValueError("Día debe estar entre 1 y 31")
    if not (0 <= data.hora <= 23):
        raise ValueError("Hora debe estar entre 0 y 23")
    if not (0 <= data.minuto <= 59):
        raise ValueError("Minuto debe estar entre 0 y 59")
    
    jd_ut = swe.julday(data.anio, data.mes, data.dia, data.hora + data.minuto / 60.0)
    
    # =================================================================================
    # ======> LA CORRECCIÓN DEFINITIVA: Usar los índices numéricos de los planetas <======
    # =================================================================================
    # Estos números son el estándar de la librería y no dependen de nombres que cambian.
    # Sol=0, Luna=1, Mercurio=2, Venus=3, Marte=4, Júpiter=5, Saturno=6, Urano=7, Neptuno=8, Plutón=9
    planetas = {
        "Sol": 0, 
        "Luna": 1, 
        "Mercurio": 2,
        "Venus": 3, 
        "Marte": 4, 
        "Júpiter": 5,
        "Saturno": 6, 
        "Urano": 7, 
        "Neptuno": 8,
        "Plutón": 9
    }
    
    posiciones = {}
    errores = []
    # La función swe.calc_ut acepta estos números directamente
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    
    for nombre, planeta_id in planetas.items():
        try:
            pos, _ = swe.calc_ut(jd_ut, planeta_id, flags)
            posiciones[nombre] = round(pos[0], 2)
        except Exception as e:
            errores.append(f"Error calculando {nombre}: {str(e)}")
            posiciones[nombre] = 0.0
    
    # El resto del código no necesita cambios
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
