# --- Sección corregida para el cálculo del Ascendente ---

# OPCIÓN 1: Solución rápida - Reemplaza esta sección en tu código:
try:
    # Método 1: Usar directamente el byte string
    house_cusp, asc, mc = swe.houses(jd_ut, data.lat, data.lng, b'P')[:3]
    
    posiciones["Ascendente"] = asc
    posiciones["Medio_Cielo"] = mc
    
except Exception as e:
    # Si el método 1 falla, intenta el método alternativo
    try:
        # Método 2: Usar el código numérico del sistema de casas
        # 'P' = Placidus = código 80 en algunas versiones de pyepheus
        house_cusp, asc, mc = swe.houses(jd_ut, data.lat, data.lng, 80)[:3]
        
        posiciones["Ascendente"] = asc
        posiciones["Medio_Cielo"] = mc
        
    except Exception as e2:
        # Si ambos métodos fallan, usa el método con string encode
        try:
            # Método 3: Convertir explícitamente el string a bytes
            hsys = 'P'.encode('ascii')
            house_cusp, asc, mc = swe.houses(jd_ut, data.lat, data.lng, hsys)[:3]
            
            posiciones["Ascendente"] = asc
            posiciones["Medio_Cielo"] = mc
            
        except Exception as e3:
            # Si nada funciona, registrar todos los errores
            errores.append(f"Error calculando Ascendente (método 1): {str(e)}")
            errores.append(f"Error calculando Ascendente (método 2): {str(e2)}")
            errores.append(f"Error calculando Ascendente (método 3): {str(e3)}")
            posiciones["Ascendente"] = 0.0
            posiciones["Medio_Cielo"] = 0.0

# OPCIÓN 2: Verificación previa de la función houses
# Si sigues teniendo problemas, prueba esta verificación antes del cálculo:

def verificar_swiss_ephemeris():
    """Función para verificar que Swiss Ephemeris esté funcionando correctamente"""
    try:
        # Prueba básica con fecha conocida
        test_jd = swe.julday(2023, 1, 1, 12.0)
        test_houses = swe.houses(test_jd, 0.0, 0.0, b'P')
        print("Swiss Ephemeris funcionando correctamente")
        return True
    except Exception as e:
        print(f"Error en Swiss Ephemeris: {e}")
        return False

# OPCIÓN 3: Función alternativa usando sidereal time si houses() no funciona
def calcular_ascendente_alternativo(jd_ut, lat, lng):
    """Método alternativo para calcular el ascendente usando tiempo sidéreo"""
    try:
        # Calcular tiempo sidéreo local
        sid_time = swe.sidtime(jd_ut)
        
        # Aquí necesitarías implementar las fórmulas trigonométricas
        # para calcular el ascendente manualmente
        # Este es un método más complejo pero más confiable
        
        return 0.0  # Placeholder - requiere implementación completa
    except Exception as e:
        return 0.0

