import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import math
from matplotlib.patches import FancyBboxPatch
import matplotlib.font_manager as fm

def generar_carta_astral_imagen(datos_carta, archivo_salida="carta_astral.png", tamaño_figura=(12, 12)):
    """
    Genera una carta astral en formato imagen con la rueda zodiacal completa.
    
    Args:
        datos_carta: Diccionario con los datos de la carta astral (del calculador completo)
        archivo_salida: Nombre del archivo de imagen a generar
        tamaño_figura: Tupla con el tamaño de la figura (ancho, alto)
    """
    
    # Configuración inicial
    fig, ax = plt.subplots(figsize=tamaño_figura, facecolor='white')
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Colores zodiacales tradicionales
    colores_signos = {
        "Aries": "#FF4500", "Tauro": "#228B22", "Géminis": "#FFD700",
        "Cáncer": "#4169E1", "Leo": "#FF8C00", "Virgo": "#8B4513",
        "Libra": "#FFB6C1", "Escorpio": "#8B0000", "Sagitario": "#9932CC",
        "Capricornio": "#2F4F4F", "Acuario": "#00CED1", "Piscis": "#20B2AA"
    }
    
    # Símbolos zodiacales (Unicode)
    simbolos_signos = {
        "Aries": "♈", "Tauro": "♉", "Géminis": "♊",
        "Cáncer": "♋", "Leo": "♌", "Virgo": "♍",
        "Libra": "♎", "Escorpio": "♏", "Sagitario": "♐",
        "Capricornio": "♑", "Acuario": "♒", "Piscis": "♓"
    }
    
    # Símbolos planetarios
    simbolos_planetas = {
        "Sol": "☉", "Luna": "☽", "Mercurio": "☿",
        "Venus": "♀", "Marte": "♂", "Júpiter": "♃",
        "Saturno": "♄", "Urano": "♅", "Neptuno": "♆", "Plutón": "♇"
    }
    
    signos_orden = ["Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo",
                   "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis"]
    
    # 1. DIBUJAR CÍRCULOS CONCÉNTRICOS
    
    # Círculo exterior (borde)
    circulo_exterior = plt.Circle((0, 0), 1.3, fill=False, color='black', linewidth=3)
    ax.add_patch(circulo_exterior)
    
    # Círculo de signos zodiacales
    circulo_signos = plt.Circle((0, 0), 1.1, fill=False, color='black', linewidth=2)
    ax.add_patch(circulo_signos)
    
    # Círculo de casas
    circulo_casas = plt.Circle((0, 0), 0.9, fill=False, color='gray', linewidth=1)
    ax.add_patch(circulo_casas)
    
    # Círculo interior (planetas)
    circulo_interior = plt.Circle((0, 0), 0.7, fill=False, color='lightgray', linewidth=1)
    ax.add_patch(circulo_interior)
    
    # 2. DIBUJAR SECTORES DE SIGNOS ZODIACALES
    
    for i, signo in enumerate(signos_orden):
        # Ángulo inicial (Aries empieza en 0°, pero en matplotlib 0° está a la derecha)
        # En astrología, Aries está en la izquierda, así que rotamos
        angulo_inicio = 90 - (i * 30)  # Empezar en 90° y ir en sentido horario
        angulo_fin = angulo_inicio - 30
        
        # Crear sector del signo
        wedge = patches.Wedge((0, 0), 1.1, angulo_fin, angulo_inicio, 
                             width=0.2, facecolor=colores_signos[signo], 
                             alpha=0.3, edgecolor='black', linewidth=1)
        ax.add_patch(wedge)
        
        # Añadir símbolo del signo
        angulo_medio = math.radians(angulo_inicio - 15)  # Centro del sector
        x_simbolo = 1.2 * math.cos(angulo_medio)
        y_simbolo = 1.2 * math.sin(angulo_medio)
        
        ax.text(x_simbolo, y_simbolo, simbolos_signos[signo], 
               fontsize=16, ha='center', va='center', 
               color=colores_signos[signo], fontweight='bold')
        
        # Añadir nombre del signo
        x_nombre = 1.0 * math.cos(angulo_medio)
        y_nombre = 1.0 * math.sin(angulo_medio)
        
        ax.text(x_nombre, y_nombre, signo[:3], 
               fontsize=10, ha='center', va='center', 
               color='black', fontweight='bold')
    
    # 3. DIBUJAR LÍNEAS DE CASAS
    
    if "casas_astrologicas" in datos_carta:
        casas = datos_carta["casas_astrologicas"]
        
        for i in range(1, 13):
            casa_nombre = f"Casa {i}"
            if casa_nombre in casas:
                grados_casa = casas[casa_nombre]["grados_totales"]
                
                # Convertir grados astrológicos a ángulo matplotlib
                # En astrología: 0° = Aries (izquierda), en matplotlib 0° = derecha
                angulo_matplotlib = 90 - grados_casa
                angulo_rad = math.radians(angulo_matplotlib)
                
                # Línea desde el centro hasta el círculo de casas
                x_fin = 0.9 * math.cos(angulo_rad)
                y_fin = 0.9 * math.sin(angulo_rad)
                
                # Línea más gruesa para casas angulares (1, 4, 7, 10)
                grosor = 2 if i in [1, 4, 7, 10] else 1
                color = 'red' if i in [1, 4, 7, 10] else 'gray'
                
                ax.plot([0, x_fin], [0, y_fin], color=color, linewidth=grosor, alpha=0.7)
                
                # Número de casa
                x_num = 0.8 * math.cos(angulo_rad)
                y_num = 0.8 * math.sin(angulo_rad)
                
                ax.text(x_num, y_num, str(i), 
                       fontsize=12, ha='center', va='center', 
                       color='black', fontweight='bold',
                       bbox=dict(boxstyle="circle,pad=0.1", facecolor='white', alpha=0.8))
    
    # 4. DIBUJAR PLANETAS
    
    if "posiciones_planetarias" in datos_carta:
        planetas = datos_carta["posiciones_planetarias"]
        
        # Agrupar planetas por proximidad para evitar superposición
        posiciones_planetas = []
        for planeta, datos in planetas.items():
            grados = datos["grados_totales"]
            posiciones_planetas.append((planeta, grados, datos))
        
        # Ordenar por grados
        posiciones_planetas.sort(key=lambda x: x[1])
        
        # Dibujar cada planeta
        for i, (planeta, grados, datos) in enumerate(posiciones_planetas):
            # Convertir a ángulo matplotlib
            angulo_matplotlib = 90 - grados
            angulo_rad = math.radians(angulo_matplotlib)
            
            # Calcular posición (con pequeño offset para evitar superposición)
            radio_planeta = 0.6
            offset_angular = 0  # Podríamos añadir lógica para separar planetas cercanos
            
            x_planeta = radio_planeta * math.cos(angulo_rad + math.radians(offset_angular))
            y_planeta = radio_planeta * math.sin(angulo_rad + math.radians(offset_angular))
            
            # Color del planeta
            colores_planetas = {
                "Sol": "#FFD700", "Luna": "#C0C0C0", "Mercurio": "#FFA500",
                "Venus": "#FF69B4", "Marte": "#FF4500", "Júpiter": "#4169E1",
                "Saturno": "#8B4513", "Urano": "#00CED1", "Neptuno": "#4682B4", "Plutón": "#8B008B"
            }
            
            color_planeta = colores_planetas.get(planeta, '#000000')
            
            # Círculo del planeta
            circulo_planeta = plt.Circle((x_planeta, y_planeta), 0.04, 
                                       facecolor=color_planeta, edgecolor='black', linewidth=1)
            ax.add_patch(circulo_planeta)
            
            # Símbolo del planeta
            simbolo = simbolos_planetas.get(planeta, planeta[:2])
            ax.text(x_planeta, y_planeta, simbolo, 
                   fontsize=12, ha='center', va='center', 
                   color='white' if planeta != 'Sol' else 'black', fontweight='bold')
            
            # Línea desde el planeta al borde (aspecto)
            x_borde = 0.88 * math.cos(angulo_rad)
            y_borde = 0.88 * math.sin(angulo_rad)
            
            ax.plot([x_planeta, x_borde], [y_planeta, y_borde], 
                   color=color_planeta, linewidth=1, alpha=0.5)
            
            # Información del planeta (grados y signo)
            info_planeta = f"{datos['signo'][:3]} {datos['grados_en_signo']:.0f}°"
            if 'casa' in datos:
                info_planeta += f" C{datos['casa']}"
            
            # Posición del texto (fuera del círculo)
            x_texto = 1.35 * math.cos(angulo_rad)
            y_texto = 1.35 * math.sin(angulo_rad)
            
            ax.text(x_texto, y_texto, f"{planeta}\n{info_planeta}", 
                   fontsize=8, ha='center', va='center', 
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
    
    # 5. MARCAR ASCENDENTE Y MEDIO CIELO
    
    if "ascendente" in datos_carta and datos_carta["ascendente"]:
        asc_grados = datos_carta["ascendente"]["grados_totales"]
        angulo_asc = math.radians(90 - asc_grados)
        
        # Línea del Ascendente (más gruesa)
        x_asc = 1.1 * math.cos(angulo_asc)
        y_asc = 1.1 * math.sin(angulo_asc)
        
        ax.plot([0, x_asc], [0, y_asc], color='red', linewidth=4, alpha=0.8)
        ax.text(x_asc * 1.1, y_asc * 1.1, 'ASC', 
               fontsize=12, ha='center', va='center', 
               color='red', fontweight='bold',
               bbox=dict(boxstyle="round,pad=0.2", facecolor='white', edgecolor='red'))
    
    if "medio_cielo" in datos_carta and datos_carta["medio_cielo"]:
        mc_grados = datos_carta["medio_cielo"]["grados_totales"]
        angulo_mc = math.radians(90 - mc_grados)
        
        # Línea del Medio Cielo
        x_mc = 1.1 * math.cos(angulo_mc)
        y_mc = 1.1 * math.sin(angulo_mc)
        
        ax.plot([0, x_mc], [0, y_mc], color='blue', linewidth=4, alpha=0.8)
        ax.text(x_mc * 1.1, y_mc * 1.1, 'MC', 
               fontsize=12, ha='center', va='center', 
               color='blue', fontweight='bold',
               bbox=dict(boxstyle="round,pad=0.2", facecolor='white', edgecolor='blue'))
    
    # 6. INFORMACIÓN GENERAL
    
    # Título
    nombre = datos_carta.get("nombre", "Carta Astral")
    fecha = datos_carta.get("fecha_hora_calculo", "")
    ciudad = datos_carta.get("ciudad", "")
    
    plt.suptitle(f"Carta Astral de {nombre}", fontsize=16, fontweight='bold', y=0.95)
    
    # Información adicional
    info_texto = f"Fecha: {fecha}\nLugar: {ciudad}"
    if "coordenadas" in datos_carta:
        lat = datos_carta["coordenadas"]["lat"]
        lng = datos_carta["coordenadas"]["lng"]
        info_texto += f"\nCoordenadas: {lat:.2f}°, {lng:.2f}°"
    
    ax.text(-1.4, -1.3, info_texto, fontsize=10, va='top', ha='left',
           bbox=dict(boxstyle="round,pad=0.5", facecolor='lightgray', alpha=0.8))
    
    # Leyenda de elementos
    elementos_texto = """
    Elementos:
    ♈♌♐ Fuego (Rojo)
    ♉♍♑ Tierra (Verde/Marrón)  
    ♊♎♒ Aire (Amarillo/Azul)
    ♋♏♓ Agua (Azul)
    """
    
    ax.text(1.4, -1.3, elementos_texto, fontsize=9, va='top', ha='right',
           bbox=dict(boxstyle="round,pad=0.5", facecolor='lightblue', alpha=0.8))
    
    # 7. GUARDAR IMAGEN
    
    plt.tight_layout()
    plt.savefig(archivo_salida, dpi=300, bbox_inches='tight', 
               facecolor='white', edgecolor='none')
    plt.show()
    
    print(f"✅ Carta astral guardada como: {archivo_salida}")
    
    return fig, ax


# FUNCIÓN DE EJEMPLO PARA PROBAR
def ejemplo_uso():
    """
    Ejemplo de cómo usar el generador con datos de prueba
    """
    
    # Datos de ejemplo (estructura del calculador completo)
    datos_ejemplo = {
        "nombre": "María García",
        "fecha_hora_calculo": "15/03/1990 14:30",
        "ciudad": "Buenos Aires, Argentina",
        "coordenadas": {"lat": -34.6037, "lng": -58.3816},
        "ascendente": {
            "grados_totales": 45.23,
            "signo": "Tauro",
            "grados_en_signo": 15.23
        },
        "medio_cielo": {
            "grados_totales": 312.45,
            "signo": "Acuario",
            "grados_en_signo": 12.45
        },
        "posiciones_planetarias": {
            "Sol": {
                "grados_totales": 354.12,
                "signo": "Piscis",
                "grados_en_signo": 24.12,
                "casa": 12
            },
            "Luna": {
                "grados_totales": 167.89,
                "signo": "Virgo",
                "grados_en_signo": 17.89,
                "casa": 5
            },
            "Venus": {
                "grados_totales": 205.67,
                "signo": "Libra",
                "grados_en_signo": 25.67,
                "casa": 7
            },
            "Marte": {
                "grados_totales": 78.34,
                "signo": "Géminis",
                "grados_en_signo": 18.34,
                "casa": 2
            }
        },
        "casas_astrologicas": {
            "Casa 1": {"grados_totales": 45.23, "signo": "Tauro", "grados_en_signo": 15.23},
            "Casa 2": {"grados_totales": 75.45, "signo": "Géminis", "grados_en_signo": 15.45},
            "Casa 3": {"grados_totales": 105.67, "signo": "Cáncer", "grados_en_signo": 15.67},
            "Casa 4": {"grados_totales": 135.89, "signo": "Leo", "grados_en_signo": 15.89},
            "Casa 5": {"grados_totales": 166.11, "signo": "Virgo", "grados_en_signo": 16.11},
            "Casa 6": {"grados_totales": 196.33, "signo": "Libra", "grados_en_signo": 16.33},
            "Casa 7": {"grados_totales": 225.23, "signo": "Escorpio", "grados_en_signo": 15.23},
            "Casa 8": {"grados_totales": 255.45, "signo": "Sagitario", "grados_en_signo": 15.45},
            "Casa 9": {"grados_totales": 285.67, "signo": "Capricornio", "grados_en_signo": 15.67},
            "Casa 10": {"grados_totales": 312.45, "signo": "Acuario", "grados_en_signo": 12.45},
            "Casa 11": {"grados_totales": 345.11, "signo": "Piscis", "grados_en_signo": 15.11},
            "Casa 12": {"grados_totales": 15.33, "signo": "Aries", "grados_en_signo": 15.33}
        }
    }
    
    # Generar la carta astral
    generar_carta_astral_imagen(datos_ejemplo, "carta_astral_ejemplo.png")


if __name__ == "__main__":
    ejemplo_uso()