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
    if not (1 <= data.mes <= 12):
        raise ValueError("Mes debe estar entre 1 y 12")
    if not (1 <= data.dia <= 31):
        raise ValueError("Día debe estar entre 1 y 31")
    if not (0 <= data.hora <= 23):
        raise ValueError("Hora debe estar entre 0 y 23")
    if not (0 <= data.minuto <= 59):
        raise ValueError("Minuto debe estar entre 0 y 59")
    
    # Validación de coordenadas (es buena práctica)
    if not (-90 <= data.lat <= 90):
        raise ValueError("Latitud debe estar entre -90 y 90")
    if not (-180 <= data.lng <= 180):
        raise ValueError("Longitud debe estar entre -180 y 180")

    # Calcular el día juliano en UT. 
    # IMPORTANTE: Se asume que data.hora y data.minuto son la HORA LOCAL
    # y que el cálculo de jd_ut ya ha sido convertido a UTC si es necesario
    # antes de pasar los datos a esta función. Si data.hora y data.minuto
    # son la hora local sin conversión a UTC, el cálculo del Ascendente será incorrecto.
    # Para un cálculo preciso, asegúrate de que jd_ut represente la hora UTC.
    jd_ut = swe.julday(data.anio, data.mes, data.dia, data.hora + data.minuto / 60.0)
    
    # =================================================================================
    # ======> LA CORRECCIÓN DEFINITIVA: Usar los índices numéricos de los planetas <======
    # =================================================================================
    # Estos números son el estándar de la librería y no dependen de nombres que cambian.
    # Sol=0, Luna=1, Mercurio=2, Venus=3, Marte=4, Júpiter=5, Saturno=6, Urano=7, Neptuno=8, Plutón=9
    planetas_indices = {
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
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    
    # Calcular posiciones planetarias
    for nombre, planeta_id in planetas_indices.items():
        try:
            pos, _ = swe.calc_ut(jd_ut, planeta_id, flags)
            posiciones[nombre] = pos[0] # Guardamos el grado zodiacal completo
        except Exception as e:
            errores.append(f"Error calculando {nombre}: {str(e)}")
            posiciones[nombre] = 0.0
    
    # --- Cálculo del Ascendente ---
    try:
        # Para el cálculo del Ascendente y las casas, necesitamos la hora sidérea local (LST).
        # La función swe.houses utiliza el día juliano UT, latitud y longitud.
        # El sistema de casas 'P' (Placidus) es el más común en astrología.
        # El error "argument 4 must be a byte string of length 1, not str" 
        # indica que el identificador del sistema de casas ('P') debe ser un byte string.
        
        # Solución: Convertir 'P' a un byte string (b'P')
        hsys_byte = b'P' 

        # house_cusp: Cúspides de las casas
        # asc: Ascendente (Cúspide de la Casa 1)
        # mc: Medio Cielo (Cúspide de la Casa 10)
        # Los '_' son para ignorar otros valores que devuelve swe.houses()
        house_cusp, asc, mc, _, _, _, _, _, _ = swe.houses(jd_ut, data.lat, data.lng, hsys_byte)
        
        posiciones["Ascendente"] = asc
        posiciones["Medio_Cielo"] = mc # Opcional: puedes añadir el MC también
        
    except Exception as e:
        # Capturamos cualquier error durante el cálculo del Ascendente
        errores.append(f"Error calculando Ascendente: {str(e)}")
        posiciones["Ascendente"] = 0.0
        posiciones["Medio_Cielo"] = 0.0 # Asignamos 0 si hay error
    # --- Fin del cálculo del Ascendente ---

    # Formatear las posiciones con signos
    signos = ["Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo", 
             "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis"]
    
    posiciones_con_signos = {}
    for planeta, grados in posiciones.items():
        # Asegurarse de que los grados estén en el rango [0, 360)
        grados_normalizados = grados % 360
        if grados_normalizados < 0: # Si el resultado es negativo, lo ajustamos
            grados_normalizados += 360

        signo_index = int(grados_normalizados // 30)
        grados_en_signo = grados_normalizados % 30
        
        posiciones_con_signos[planeta] = {
            "grados_totales": round(grados, 2), # Mantenemos la precisión original
            "signo": signos[signo_index],
            "grados_en_signo": round(grados_en_signo, 2)
        }
    
    resultado = {
        "nombre": data.nombre,
        # Formato de fecha y hora, asumiendo que los datos pasados a la función son correctos
        "fecha_hora_calculo": f"{data.dia:02d}/{data.mes:02d}/{data.anio} {data.hora:02d}:{data.minuto:02d}",
        "ciudad": data.ciudad,
        "coordenadas": {"lat": data.lat, "lng": data.lng},
        "posiciones_planetarias": posiciones_con_signos,
        "dia_juliano": round(jd_ut, 2)
    }
    
    if errores:
        resultado["advertencias"] = errores
        
    return resultado

# --- END OF FILE astral_calculator.py ---

