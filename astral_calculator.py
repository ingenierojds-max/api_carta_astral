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

    # Calcular el día juliano en UT
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
        # La librería sweph espera la hora en UTC + zona horaria para cálculo del ascendente
        # Si tus datos de entrada ya están en UT, puedes usarlos directamente.
        # Si los datos son locales y quieres que sean UT, deberías ajustar por zona horaria.
        # Aquí asumimos que los datos de data.hora y data.minuto son la hora LOCAL
        # Y que necesitas la hora UT para el cálculo.
        # Si el cálculo de jd_ut ya es la hora local, entonces usaremos eso.
        # Si data.hora y data.minuto son hora local, y no UT, necesitas ajustar.
        # Vamos a asumir por ahora que data.hora y data.minuto corresponden al UT para simplificar,
        # pero en una aplicación real, la zona horaria es CRUCIAL.

        # Para el Ascendente, swe.houses necesita la hora sidérea local (LST)
        # Calculamos el LST a partir del día juliano UT y la longitud.
        # La función swe.houses usa la hora UT y la latitud/longitud.
        # Sin embargo, para el Ascendente directamente, podemos usar swe.houses.
        # La documentación de sweph es un poco confusa aquí.
        # La forma más directa para el Ascendente (Cúspide Casa 1) es con swe.houses:
        # house_cusp, asc, mc, ... = swe.houses(jd_ut, lat, lng, hsys='P')
        # Donde hsys='P' es el sistema de casas Placidus, común en astrología.

        # Es importante tener en cuenta la hora universal coordinada (UTC)
        # Si 'data.hora' y 'data.minuto' son hora local, se necesita sumar el offset de la zona horaria
        # para obtener la hora UT. Asumo aquí que `jd_ut` ya está correcto para el cálculo
        # de Ascendente (es decir, que `data.hora` y `data.minuto` son la hora UT).
        # Si no es así, este cálculo fallará.

        # Si your `data.hora` and `data.minuto` are local time, you must convert to UTC first.
        # For simplicity, let's assume `jd_ut` is already correct for the calculation.

        # Si tus datos de entrada (hora, minuto) son HORA LOCAL y no UT,
        # necesitas calcular el jd_ut en UTC. La conversión puede ser compleja
        # debido a los cambios de horario de verano.
        # Para este ejemplo, ASUMIREMOS que `jd_ut` representa la hora UT
        # para el cálculo del Ascendente.

        # El parámetro `hsys` especifica el sistema de casas. 'P' es Placidus.
        # El valor retornado `asc` es la posición del Ascendente.
        house_cusp, asc, mc, _, _, _, _, _, _ = swe.houses(jd_ut, data.lat, data.lng, 'P') # 'P' para Placidus

        posiciones["Ascendente"] = asc
    except Exception as e:
        errores.append(f"Error calculando Ascendente: {str(e)}")
        posiciones["Ascendente"] = 0.0
    # --- Fin del cálculo del Ascendente ---


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
            "grados_totales": round(grados, 2), # Mantenemos la precisión original
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

# --- END OF FILE astral_calculator.py ---

