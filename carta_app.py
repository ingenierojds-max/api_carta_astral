from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import uuid
from datetime import datetime
import base64
import io

# Importar tu módulo de generación de cartas astrales
from generador_carta_astral_visual import generar_carta_astral_imagen

app = Flask(__name__)
CORS(app)  # Permitir CORS para N8N

# Crear directorio para guardar imágenes si no existe
os.makedirs("static/cartas", exist_ok=True)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

@app.route('/', methods=['GET'])
def home():
    return {
        'aplicacion': 'Generador de Cartas Astrales',
        'version': '1.0',
        'status': 'funcionando',
        'endpoints': {
            'generar_carta': '/carta-astral/imagen',
            'test': '/test',
            'health': '/health'
        }
    }

@app.route('/health', methods=['GET'])
def health():
    return {
        'status': 'ok',
        'timestamp': str(datetime.now()),
        'message': 'Servidor funcionando correctamente'
    }

@app.route('/test', methods=['GET'])
def test_simple():
    return {
        'status': 'funcionando',
        'mensaje': 'La aplicación está corriendo correctamente',
        'endpoint_disponible': True,
        'timestamp': str(datetime.now())
    }

@app.route('/carta-astral/imagen', methods=['GET', 'POST'])
def generar_carta():
    if request.method == 'GET':
        return {
            'status': 'ok',
            'mensaje': 'Endpoint funcionando correctamente',
            'metodo_requerido': 'POST',
            'ejemplo_uso': 'Envía datos por POST para generar la carta astral',
            'formato_datos': {
                'nombre': 'Nombre de la persona',
                'fecha_nacimiento': 'YYYY-MM-DD',
                'hora_nacimiento': 'HH:MM',
                'lugar_nacimiento': 'Ciudad, País',
                'latitud': 'Latitud del lugar',
                'longitud': 'Longitud del lugar'
            }
        }
    
    try:
        # Obtener datos del request
        datos = request.json
        if not datos:
            return {'error': 'No se enviaron datos'}, 400
        
        # Generar la carta astral (usando tu función existente)
        imagen = generar_carta_astral_imagen(datos)
        
        # Crear nombre único para la imagen
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        nombre_archivo = f"carta_astral_{timestamp}_{unique_id}.png"
        ruta_archivo = f"static/cartas/{nombre_archivo}"
        
        # Guardar la imagen en el servidor
        imagen.save(ruta_archivo)
        
        # URL completa para acceder a la imagen
        base_url = request.host_url.rstrip('/')
        url_imagen = f"{base_url}/static/cartas/{nombre_archivo}"
        
        # También generar versión base64 para N8N
        img_buffer = io.BytesIO()
        imagen.save(img_buffer, format='PNG')
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        
        # Respuesta completa con toda la información
        respuesta = {
            'success': True,
            'mensaje': 'Carta astral generada exitosamente',
            'datos_procesados': {
                'nombre': datos.get('nombre', 'No especificado'),
                'fecha': datos.get('fecha_nacimiento', 'No especificada'),
                'hora': datos.get('hora_nacimiento', 'No especificada'),
                'lugar': datos.get('lugar_nacimiento', 'No especificado')
            },
            'imagen': {
                'nombre_archivo': nombre_archivo,
                'ruta_local': ruta_archivo,
                'url_completa': url_imagen,
                'url_relativa': f"/static/cartas/{nombre_archivo}",
                'formato': 'PNG',
                'timestamp': timestamp
            },
            'base64': f"data:image/png;base64,{img_base64}",
            'para_n8n': {
                'imagen_url': url_imagen,
                'imagen_base64': img_base64,
                'descarga_directa': f"{base_url}/download/{nombre_archivo}"
            }
        }
        
        return respuesta
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'mensaje': 'Error al generar la carta astral',
            'timestamp': str(datetime.now())
        }, 500

# Endpoint para servir archivos estáticos (imágenes)
@app.route('/static/cartas/<filename>')
def serve_carta_image(filename):
    try:
        return send_from_directory('static/cartas', filename)
    except FileNotFoundError:
        return {'error': 'Imagen no encontrada'}, 404

# Endpoint para descargar imágenes
@app.route('/download/<filename>')
def download_carta(filename):
    try:
        return send_from_directory('static/cartas', filename, as_attachment=True)
    except FileNotFoundError:
        return {'error': 'Archivo no encontrado'}, 404

# Endpoint específico para N8N (formato optimizado)
@app.route('/n8n/generar-carta', methods=['POST'])
def generar_carta_n8n():
    try:
        datos = request.json
        if not datos:
            return {'error': 'No se enviaron datos'}, 400
        
        # Generar imagen
        imagen = generar_carta_astral_imagen(datos)
        
        # Convertir a base64 para N8N
        img_buffer = io.BytesIO()
        imagen.save(img_buffer, format='PNG')
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        
        # Guardar también en archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"carta_n8n_{timestamp}.png"
        ruta_archivo = f"static/cartas/{nombre_archivo}"
        imagen.save(ruta_archivo)
        
        base_url = request.host_url.rstrip('/')
        
        return {
            'imagen_base64': img_base64,
            'imagen_url': f"{base_url}/static/cartas/{nombre_archivo}",
            'nombre_archivo': nombre_archivo,
            'success': True
        }
        
    except Exception as e:
        return {'error': str(e), 'success': False}, 500

# Endpoint para limpiar imágenes antiguas (opcional)
@app.route('/admin/limpiar-imagenes', methods=['POST'])
def limpiar_imagenes():
    try:
        carpeta = 'static/cartas'
        archivos_eliminados = []
        
        for archivo in os.listdir(carpeta):
            if archivo.endswith('.png'):
                ruta_completa = os.path.join(carpeta, archivo)
                # Eliminar archivos más antiguos de 24 horas (opcional)
                if os.path.getctime(ruta_completa) < (datetime.now().timestamp() - 86400):
                    os.remove(ruta_completa)
                    archivos_eliminados.append(archivo)
        
        return {
            'mensaje': f'Se eliminaron {len(archivos_eliminados)} archivos antiguos',
            'archivos_eliminados': archivos_eliminados
        }
        
    except Exception as e:
        return {'error': str(e)}, 500

if __name__ == '__main__':
    # Configuración para Railway/producción
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
