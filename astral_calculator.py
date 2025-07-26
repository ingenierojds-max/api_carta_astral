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
    jd_ut = swe.julday(data.anio, data.mes, data.dia, data.hora + data.minuto / 60.0)
    
    # INICIALIZAR VARIABLES ANTES DE USARLAS
    posiciones = {}
    errores = []  # ← MOVIDO AQUÍ ANTES DE SER USADO
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    
    # Índices numéricos de los planetas
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
    
    # Calcular posiciones planetarias
    for nombre, planeta_id in planetas_indices.items():
        try:
            pos, _ = swe.calc_ut(jd_ut, planeta_id, flags)
            posiciones[nombre] = pos[0]
        except Exception as e:
            errores.append(f"Error calculando {nombre}: {str(e)}")
            posiciones[nombre] = 0.0
    
    # --- Cálculo del Ascendente (CORREGIDO) ---
    try:
        # Método 1: Usar directamente el byte string
        house_cusp, asc, mc = swe.houses(jd_ut, data.lat, data.lng, b'P')[:3]
        
        posiciones["Ascendente"] = asc
        posiciones["Medio_Cielo"] = mc
        
    except Exception as e:
        # Si el método 1 falla, intenta métodos alternativos
        try:
            # Método 2: Usar string encode
            hsys = 'P'.encode('ascii')
            house_cusp, asc, mc = swe.houses(jd_ut, data.lat, data.lng, hsys)[:3]
            
            posiciones["Ascendente"] = asc
            posiciones["Medio_Cielo"] = mc
            
        except Exception as e2:
            try:
                # Método 3: Usar código numérico (Placidus = P)
                # En algunas versiones, 'P' corresponde al código numérico
                house_cusp = swe.houses_ex(jd_ut, flags, data.lat, data.lng, b'P')[0]
                posiciones["Ascendente"] = house_cusp[0]  # Ascendente es la cúspide de casa 1
                posiciones["Medio_Cielo"] = house_cusp[9]  # MC es la cúspide de casa 10
                
            except Exception as e3:
                # Si todos los métodos fallan
                errores.append(f"Error calculando Ascendente: {str(e)}")
                posiciones["Ascendente"] = 0.0
                posiciones["Medio_Cielo"] = 0.0

    # Formatear las posiciones con signos
    signos = ["Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo", 
             "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis"]
    
    posiciones_con_signos = {}
    for planeta, grados in posiciones.items():
        # Asegurarse de que los grados estén en el rango [0, 360)
        grados_normalizados = grados % 360
        if grados_normalizados < 0:
            grados_normalizados += 360

        signo_index = int(grados_normalizados // 30)
        grados_en_signo = grados_normalizados % 30
        
        posiciones_con_signos[planeta] = {
            "grados_totales": round(grados, 2),
            "signo": signos[signo_index],
            "grados_en_signo": round(grados_en_signo, 2)
        }
    
    resultado = {
        "nombre": data.nombre,
        "fecha_hora_calculo": f"{data.dia:02d}/{data.mes:02d}/{data.anio} {data.hora:02d}:{data.minuto:02d}",
        "ciudad": data.ciudad,
        "coordenadas": {"lat": data.lat, "lng": data.lng},
        "posiciones_planetarias": posiciones_con_signos,
        "dia_juliano": round(jd_ut, 2)
    }
    
    if errores:
        resultado["advertencias"] = errores
        
    return resultado
