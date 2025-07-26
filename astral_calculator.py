import swisseph as swe
import math

def realizar_calculo_astral(data):
    """
    Motor de cálculo de la carta astral COMPLETO.
    Incluye planetas, ascendente, medio cielo y las 12 casas astrológicas.
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
    
    # Validación de coordenadas
    if not (-90 <= data.lat <= 90):
        raise ValueError("Latitud debe estar entre -90 y 90")
    if not (-180 <= data.lng <= 180):
        raise ValueError("Longitud debe estar entre -180 y 180")

    # Calcular el día juliano en UT
    jd_ut = swe.julday(data.anio, data.mes, data.dia, data.hora + data.minuto / 60.0)
    
    # Inicializar variables
    posiciones = {}
    casas = {}
    errores = []
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
    
    # --- Cálculo de Casas, Ascendente y Medio Cielo ---
    try:
        # Método 1: Capturar todos los valores que devuelve swe.houses()
        resultado_houses = swe.houses(jd_ut, data.lat, data.lng, b'P')
        
        # swe.houses() típicamente devuelve (house_cusps, ascmc)
        if len(resultado_houses) >= 2:
            house_cusps, ascmc = resultado_houses[0], resultado_houses[1]
            
            # Ascendente y Medio Cielo
            posiciones["Ascendente"] = ascmc[0]  # Ascendente
            posiciones["Medio_Cielo"] = ascmc[1]  # Medio Cielo
            
            # Las 12 casas (house_cusps[0] es casa 1, house_cusps[1] es casa 2, etc.)
            nombres_casas = [
                "Casa 1", "Casa 2", "Casa 3", "Casa 4", "Casa 5", "Casa 6",
                "Casa 7", "Casa 8", "Casa 9", "Casa 10", "Casa 11", "Casa 12"
            ]
            
            for i, nombre_casa in enumerate(nombres_casas):
                if i < len(house_cusps):
                    casas[nombre_casa] = house_cusps[i]
                else:
                    casas[nombre_casa] = 0.0
                    errores.append(f"No se pudo calcular {nombre_casa}")
            
        else:
            # Si solo devuelve un valor, intentar extraer de ahí
            house_cusps = resultado_houses[0]
            posiciones["Ascendente"] = house_cusps[0] if len(house_cusps) > 0 else 0.0
            posiciones["Medio_Cielo"] = house_cusps[9] if len(house_cusps) > 9 else 0.0
            
            # Intentar extraer las casas del array único
            nombres_casas = [
                "Casa 1", "Casa 2", "Casa 3", "Casa 4", "Casa 5", "Casa 6",
                "Casa 7", "Casa 8", "Casa 9", "Casa 10", "Casa 11", "Casa 12"
            ]
            
            for i, nombre_casa in enumerate(nombres_casas):
                if i < len(house_cusps):
                    casas[nombre_casa] = house_cusps[i]
                else:
                    casas[nombre_casa] = 0.0
                    
    except Exception as e:
        try:
            # Método 2: Usar string normal (algunas versiones lo aceptan)
            resultado_houses = swe.houses(jd_ut, data.lat, data.lng, 'P')
            
            if len(resultado_houses) >= 2:
                house_cusps, ascmc = resultado_houses[0], resultado_houses[1]
                posiciones["Ascendente"] = ascmc[0]
                posiciones["Medio_Cielo"] = ascmc[1]
                
                nombres_casas = [
                    "Casa 1", "Casa 2", "Casa 3", "Casa 4", "Casa 5", "Casa 6",
                    "Casa 7", "Casa 8", "Casa 9", "Casa 10", "Casa 11", "Casa 12"
                ]
                
                for i, nombre_casa in enumerate(nombres_casas):
                    if i < len(house_cusps):
                        casas[nombre_casa] = house_cusps[i]
                    else:
                        casas[nombre_casa] = 0.0
                        
        except Exception as e2:
            # Método 3: Cálculo manual aproximado
            try:
                # Tiempo sidéreo en Greenwich
                sidt = swe.sidtime(jd_ut)
                # Tiempo sidéreo local (aproximado)
                local_sidt = (sidt + data.lng / 15.0) % 24.0
                
                # Fórmula aproximada para el Ascendente
                lat_rad = math.radians(data.lat)
                lst_rad = math.radians(local_sidt * 15.0)
                
                # Aproximación del Ascendente
                asc_rad = math.atan2(-math.cos(lst_rad), 
                                    math.sin(lst_rad) * math.cos(lat_rad))
                ascendente_aprox = math.degrees(asc_rad) % 360
                
                posiciones["Ascendente"] = ascendente_aprox
                posiciones["Medio_Cielo"] = (local_sidt * 15.0) % 360  # MC aproximado
                
                # Casas aproximadas (método Equal House - casas de 30° cada una)
                casa_1 = ascendente_aprox
                for i in range(12):
                    casa_grados = (casa_1 + (i * 30)) % 360
                    casas[f"Casa {i+1}"] = casa_grados
                
                errores.append("Usando cálculo aproximado de casas y ascendente (método manual)")
                
            except Exception as e3:
                # Si todo falla
                errores.append(f"Error calculando casas: {str(e)} | {str(e2)} | {str(e3)}")
                posiciones["Ascendente"] = 0.0
                posiciones["Medio_Cielo"] = 0.0
                
                # Casas por defecto (todas en 0)
                for i in range(12):
                    casas[f"Casa {i+1}"] = 0.0

    # Función para determinar en qué casa está cada planeta
    def determinar_casa_planeta(grados_planeta, casas_cusps):
        """
        Determina en qué casa está un planeta basado en sus grados
        y las cúspides de las casas.
        """
        # Normalizar grados del planeta
        grados_planeta = grados_planeta % 360
        
        # Convertir diccionario de casas a lista ordenada
        cusps_list = []
        for i in range(1, 13):
            cusp = casas_cusps.get(f"Casa {i}", 0.0) % 360
            cusps_list.append(cusp)
        
        # Encontrar en qué casa cae el planeta
        for i in range(12):
            cusp_actual = cusps_list[i]
            cusp_siguiente = cusps_list[(i + 1) % 12]
            
            # Manejar el caso donde la casa cruza 0° (ej: de 350° a 10°)
            if cusp_actual <= cusp_siguiente:
                if cusp_actual <= grados_planeta < cusp_siguiente:
                    return i + 1
            else:  # Casa que cruza 0°
                if grados_planeta >= cusp_actual or grados_planeta < cusp_siguiente:
                    return i + 1
        
        return 1  # Por defecto, casa 1

    # Formatear las posiciones con signos y casas
    signos = ["Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo", 
             "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis"]
    
    posiciones_con_signos = {}
    for planeta, grados in posiciones.items():
        # Saltar Ascendente y Medio Cielo para el cálculo de casas
        if planeta in ["Ascendente", "Medio_Cielo"]:
            continue
            
        # Asegurarse de que los grados estén en el rango [0, 360)
        grados_normalizados = grados % 360
        if grados_normalizados < 0:
            grados_normalizados += 360

        signo_index = int(grados_normalizados // 30)
        grados_en_signo = grados_normalizados % 30
        
        # Determinar casa del planeta
        casa_planeta = determinar_casa_planeta(grados_normalizados, casas)
        
        posiciones_con_signos[planeta] = {
            "grados_totales": round(grados, 2),
            "signo": signos[signo_index],
            "grados_en_signo": round(grados_en_signo, 2),
            "casa": casa_planeta
        }
    
    # Formatear las casas con signos
    casas_con_signos = {}
    for casa, grados in casas.items():
        grados_normalizados = grados % 360
        if grados_normalizados < 0:
            grados_normalizados += 360

        signo_index = int(grados_normalizados // 30)
        grados_en_signo = grados_normalizados % 30
        
        casas_con_signos[casa] = {
            "grados_totales": round(grados, 2),
            "signo": signos[signo_index],
            "grados_en_signo": round(grados_en_signo, 2)
        }
    
    # Formatear Ascendente y Medio Cielo
    ascendente_formateado = {}
    medio_cielo_formateado = {}
    
    if "Ascendente" in posiciones:
        grados_asc = posiciones["Ascendente"] % 360
        if grados_asc < 0:
            grados_asc += 360
        signo_index_asc = int(grados_asc // 30)
        grados_en_signo_asc = grados_asc % 30
        
        ascendente_formateado = {
            "grados_totales": round(posiciones["Ascendente"], 2),
            "signo": signos[signo_index_asc],
            "grados_en_signo": round(grados_en_signo_asc, 2)
        }
    
    if "Medio_Cielo" in posiciones:
        grados_mc = posiciones["Medio_Cielo"] % 360
        if grados_mc < 0:
            grados_mc += 360
        signo_index_mc = int(grados_mc // 30)
        grados_en_signo_mc = grados_mc % 30
        
        medio_cielo_formateado = {
            "grados_totales": round(posiciones["Medio_Cielo"], 2),
            "signo": signos[signo_index_mc],
            "grados_en_signo": round(grados_en_signo_mc, 2)
        }
    
    # Resultado final estructurado
    resultado = {
        "nombre": data.nombre,
        "fecha_hora_calculo": f"{data.dia:02d}/{data.mes:02d}/{data.anio} {data.hora:02d}:{data.minuto:02d}",
        "ciudad": data.ciudad,
        "coordenadas": {"lat": data.lat, "lng": data.lng},
        "ascendente": ascendente_formateado,
        "medio_cielo": medio_cielo_formateado,
        "posiciones_planetarias": posiciones_con_signos,
        "casas_astrologicas": casas_con_signos,
        "dia_juliano": round(jd_ut, 2)
    }
    
    if errores:
        resultado["advertencias"] = errores
        
    return resultado
