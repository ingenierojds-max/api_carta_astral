import swisseph as swe
import math

def realizar_calculo_astral(data):
    """
    Motor de cálculo de la carta astral expandido.
    Incluye planetas, casas, aspectos, y datos adicionales.
    """
    
    # Validaciones básicas
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
    if not (-90 <= data.lat <= 90):
        raise ValueError("Latitud debe estar entre -90 y 90")
    if not (-180 <= data.lng <= 180):
        raise ValueError("Longitud debe estar entre -180 y 180")
    
    # Cálculo del día juliano
    jd_ut = swe.julday(data.anio, data.mes, data.dia, data.hora + data.minuto / 60.0)
    
    # Planetas principales
    planetas = {
        "Sol": 0, "Luna": 1, "Mercurio": 2, "Venus": 3, "Marte": 4,
        "Júpiter": 5, "Saturno": 6, "Urano": 7, "Neptuno": 8, "Plutón": 9
    }
    
    # Puntos adicionales
    puntos_adicionales = {
        "Nodo Norte": swe.MEAN_NODE,
        "Nodo Sur": swe.MEAN_NODE,  # Se calculará como opuesto
        "Quirón": swe.CHIRON,
        "Lilith": swe.MEAN_APOG
    }
    
    # Signos del zodíaco
    signos = ["Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo", 
             "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis"]
    
    # Elementos y modalidades
    elementos = ["Fuego", "Tierra", "Aire", "Agua"] * 3
    modalidades = ["Cardinal", "Cardinal", "Cardinal", "Fijo", "Fijo", "Fijo", 
                  "Mutable", "Mutable", "Mutable", "Cardinal", "Fijo", "Mutable"]
    
    posiciones = {}
    errores = []
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    
    # Calcular posiciones planetarias
    for nombre, planeta_id in planetas.items():
        try:
            pos, _ = swe.calc_ut(jd_ut, planeta_id, flags)
            posiciones[nombre] = pos[0]
        except Exception as e:
            errores.append(f"Error calculando {nombre}: {str(e)}")
            posiciones[nombre] = 0.0
    
    # Calcular puntos adicionales
    for nombre, punto_id in puntos_adicionales.items():
        try:
            if nombre == "Nodo Sur":
                # Nodo Sur es opuesto al Nodo Norte
                pos_norte, _ = swe.calc_ut(jd_ut, swe.MEAN_NODE, flags)
                pos_sur = (pos_norte[0] + 180) % 360
                posiciones[nombre] = pos_sur
            else:
                pos, _ = swe.calc_ut(jd_ut, punto_id, flags)
                posiciones[nombre] = pos[0]
        except Exception as e:
            errores.append(f"Error calculando {nombre}: {str(e)}")
            posiciones[nombre] = 0.0
    
    # Calcular casas astrológicas
    try:
        # Sistema Placidus (más común)
        casas = swe.houses(jd_ut, data.lat, data.lng, b'P')
        cuspides_casas = casas[0][:12]  # Primeras 12 son las casas
        ascendente = casas[1][0]  # ASC
        medio_cielo = casas[1][1]  # MC
        descendente = (ascendente + 180) % 360  # DSC
        fondo_cielo = (medio_cielo + 180) % 360  # IC
        
        # Añadir ángulos importantes
        posiciones["Ascendente"] = ascendente
        posiciones["Medio Cielo"] = medio_cielo
        posiciones["Descendente"] = descendente
        posiciones["Fondo del Cielo"] = fondo_cielo
        
    except Exception as e:
        errores.append(f"Error calculando casas: {str(e)}")
        cuspides_casas = [0] * 12
        ascendente = medio_cielo = descendente = fondo_cielo = 0
    
    # Procesar posiciones con signos y casas
    posiciones_detalladas = {}
    distribucion_signos = {signo: [] for signo in signos}
    distribucion_elementos = {"Fuego": 0, "Tierra": 0, "Aire": 0, "Agua": 0}
    distribucion_modalidades = {"Cardinal": 0, "Fijo": 0, "Mutable": 0}
    
    for planeta, grados in posiciones.items():
        signo_index = int(grados // 30)
        grados_en_signo = grados % 30
        signo = signos[signo_index]
        elemento = elementos[signo_index]
        modalidad = modalidades[signo_index]
        
        # Determinar casa
        casa = determinar_casa(grados, cuspides_casas)
        
        # Determinar retrógrado (solo para planetas)
        retrogrado = False
        if planeta in planetas:
            try:
                pos_full, _ = swe.calc_ut(jd_ut, planetas[planeta], flags)
                retrogrado = pos_full[3] < 0  # Velocidad negativa = retrógrado
            except:
                pass
        
        posiciones_detalladas[planeta] = {
            "grados_totales": round(grados, 2),
            "signo": signo,
            "grados_en_signo": round(grados_en_signo, 2),
            "casa": casa,
            "elemento": elemento,
            "modalidad": modalidad,
            "retrogrado": retrogrado
        }
        
        # Contar distribuciones (solo planetas principales para estadísticas)
        if planeta in planetas:
            distribucion_signos[signo].append(planeta)
            distribucion_elementos[elemento] += 1
            distribucion_modalidades[modalidad] += 1
    
    # Calcular aspectos principales
    aspectos = calcular_aspectos(posiciones, planetas)
    
    # Información de las casas
    casas_info = {}
    nombres_casas = [
        "Casa I - Personalidad", "Casa II - Recursos", "Casa III - Comunicación",
        "Casa IV - Hogar", "Casa V - Creatividad", "Casa VI - Salud",
        "Casa VII - Relaciones", "Casa VIII - Transformación", "Casa IX - Filosofía",
        "Casa X - Carrera", "Casa XI - Amistad", "Casa XII - Espiritualidad"
    ]
    
    for i, cuspide in enumerate(cuspides_casas):
        signo_casa = signos[int(cuspide // 30)]
        casas_info[f"Casa {i+1}"] = {
            "nombre": nombres_casas[i],
            "cuspide": round(cuspide, 2),
            "signo": signo_casa
        }
    
    # Resultado completo
    resultado = {
        "datos_personales": {
            "nombre": data.nombre,
            "fecha_nacimiento": f"{data.dia:02d}/{data.mes:02d}/{data.anio}",
            "hora_nacimiento": f"{data.hora:02d}:{data.minuto:02d}",
            "lugar_nacimiento": data.ciudad,
            "coordenadas": {"latitud": data.lat, "longitud": data.lng},
            "dia_juliano": round(jd_ut, 2)
        },
        
        "posiciones_planetarias": posiciones_detalladas,
        
        "casas_astrologicas": casas_info,
        
        "aspectos_principales": aspectos,
        
        "distribucion_signos": {
            signo: planetas for signo, planetas in distribucion_signos.items() if planetas
        },
        
        "distribucion_elementos": distribucion_elementos,
        
        "distribucion_modalidades": distribucion_modalidades,
        
        "angulos_importantes": {
            "Ascendente": {
                "grados": round(ascendente, 2),
                "signo": signos[int(ascendente // 30)]
            },
            "Medio Cielo": {
                "grados": round(medio_cielo, 2),
                "signo": signos[int(medio_cielo // 30)]
            },
            "Descendente": {
                "grados": round(descendente, 2),
                "signo": signos[int(descendente // 30)]
            },
            "Fondo del Cielo": {
                "grados": round(fondo_cielo, 2),
                "signo": signos[int(fondo_cielo // 30)]
            }
        }
    }
    
    if errores:
        resultado["advertencias"] = errores
    
    return resultado

def determinar_casa(grados_planeta, cuspides_casas):
    """Determina en qué casa está un planeta según sus grados."""
    for i in range(12):
        inicio_casa = cuspides_casas[i]
        fin_casa = cuspides_casas[(i + 1) % 12]
        
        # Manejar el cruce del 0° (Aries)
        if inicio_casa > fin_casa:
            if grados_planeta >= inicio_casa or grados_planeta < fin_casa:
                return i + 1
        else:
            if inicio_casa <= grados_planeta < fin_casa:
                return i + 1
    
    return 1  # Por defecto Casa I

def calcular_aspectos(posiciones, planetas):
    """Calcula los aspectos principales entre planetas."""
    aspectos_encontrados = []
    
    # Definir aspectos y sus orbes
    aspectos_config = {
        "Conjunción": {"grados": 0, "orbe": 8},
        "Oposición": {"grados": 180, "orbe": 8},
        "Trígono": {"grados": 120, "orbe": 6},
        "Cuadratura": {"grados": 90, "orbe": 6},
        "Sextil": {"grados": 60, "orbe": 4},
        "Quincuncio": {"grados": 150, "orbe": 3}
    }
    
    planetas_lista = list(planetas.keys())
    
    for i, planeta1 in enumerate(planetas_lista):
        for planeta2 in planetas_lista[i+1:]:
            pos1 = posiciones.get(planeta1, 0)
            pos2 = posiciones.get(planeta2, 0)
            
            # Calcular diferencia angular
            diferencia = abs(pos1 - pos2)
            if diferencia > 180:
                diferencia = 360 - diferencia
            
            # Verificar aspectos
            for aspecto, config in aspectos_config.items():
                grados_aspecto = config["grados"]
                orbe = config["orbe"]
                
                if abs(diferencia - grados_aspecto) <= orbe:
                    exactitud = abs(diferencia - grados_aspecto)
                    aspectos_encontrados.append({
                        "planeta1": planeta1,
                        "planeta2": planeta2,
                        "aspecto": aspecto,
                        "orbe_aplicado": round(exactitud, 2),
                        "exacto": exactitud < 1.0
                    })
                    break
    
    return aspectos_encontrados
