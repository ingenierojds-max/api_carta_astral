import swisseph as swe
import math

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
        # Método 1: Capturar todos los valores que devuelve swe.houses()
        resultado_houses = swe.houses(jd_ut, data.lat, data.lng, b'P')
        
        # swe.houses() devuelve diferentes cantidades de valores según la versión
        # Típicamente: (house_cusps, ascmc) donde ascmc contiene [Asc, MC, ARMC, Vertex, ...]
        if len(resultado_houses) >= 2:
            house_cusps, ascmc = resultado_houses[0], resultado_houses[1]
            posiciones["Ascendente"] = ascmc[0]  # Ascendente
            posiciones["Medio_Cielo"] = ascmc[1]  # Medio Cielo
        else:
            # Si solo devuelve un valor, intentar extraer de ahí
            house_cusps = resultado_houses[0]
            posiciones["Ascendente"] = house_cusps[0] if len(house_cusps) > 0 else 0.0
            posiciones["Medio_Cielo"] = house_cusps[9] if len(house_cusps) > 9 else 0.0
            
    except Exception as e:
        try:
            # Método 2: Usar string normal (algunas versiones lo aceptan)
            resultado_houses = swe.houses(jd_ut, data.lat, data.lng, 'P')
            
            if len(resultado_houses) >= 2:
                house_cusps, ascmc = resultado_houses[0], resultado_houses[1]
                posiciones["Ascendente"] = ascmc[0]
                posiciones["Medio_Cielo"] = ascmc[1]
            else:
                house_cusps = resultado_houses[0]
                posiciones["Ascendente"] = house_cusps[0] if len(house_cusps) > 0 else 0.0
                posiciones["Medio_Cielo"] = house_cusps[9] if len(house_cusps) > 9 else 0.0
                
        except Exception as e2:
            try:
                # Método 3: Usar houses_ex si está disponible
                resultado_houses_ex = swe.houses_ex(jd_ut, flags, data.lat, data.lng, b'P')
                
                if len(resultado_houses_ex) >= 2:
                    house_cusps, ascmc = resultado_houses_ex[0], resultado_houses_ex[1]
                    posiciones["Ascendente"] = ascmc[0]
                    posiciones["Medio_Cielo"] = ascmc[1]
                else:
                    posiciones["Ascendente"] = 0.0
                    posiciones["Medio_Cielo"] = 0.0
                    
            except Exception as e3:
                # Método 4: Cálculo manual aproximado del Ascendente usando tiempo sidéreo
                try:
                    # Tiempo sidéreo en Greenwich
                    sidt = swe.sidtime(jd_ut)
                    # Tiempo sidéreo local (aproximado)
                    local_sidt = (sidt + data.lng / 15.0) % 24.0
                    
                    # Fórmula aproximada para el Ascendente
                    # Esta es una aproximación básica, no tan precisa como houses()
                    import math
                    lat_rad = math.radians(data.lat)
                    lst_rad = math.radians(local_sidt * 15.0)
                    
                    # Aproximación del Ascendente
                    asc_rad = math.atan2(-math.cos(lst_rad), 
                                        math.sin(lst_rad) * math.cos(lat_rad))
                    ascendente_aprox = math.degrees(asc_rad) % 360
                    
                    posiciones["Ascendente"] = ascendente_aprox
                    posiciones["Medio_Cielo"] = (local_sidt * 15.0) % 360  # MC aproximado
                    
                    errores.append("Usando cálculo aproximado del Ascendente (método manual)")
                    
                except Exception as e4:
                    # Si todo falla
                    errores.append(f"Error calculando Ascendente: {str(e)} | {str(e2)} | {str(e3)} | {str(e4)}")
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
    
    # Separar elementos especiales para una estructura más clara
    ascendente = posiciones_con_signos.pop("Ascendente", {})
    medio_cielo = posiciones_con_signos.pop("Medio_Cielo", {})
    
    resultado = {
        "nombre": data.nombre,
        "fecha_hora_calculo": f"{data.dia:02d}/{data.mes:02d}/{data.anio} {data.hora:02d}:{data.minuto:02d}",
        "ciudad": data.ciudad,
        "coordenadas": {"lat": data.lat, "lng": data.lng},
        "ascendente": ascendente,
        "medio_cielo": medio_cielo,
        "posiciones_planetarias": posiciones_con_signos,
        "dia_juliano": round(jd_ut, 2)
    }
    
    if errores:
        resultado["advertencias"] = errores
        
    return resultado
