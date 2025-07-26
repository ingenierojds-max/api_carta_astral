from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import uuid
from datetime import datetime
import base64
import io
from typing import Optional, Dict, Any

# Importar tu módulo de generación de cartas astrales
from generador_carta_astral_visual import generar_carta_astral_imagen

app = FastAPI(
    title="Generador de Cartas Astrales",
    description="API para generar cartas astrales visuales",
    version="1.0.0"
)

# Configurar CORS para N8N
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear directorio para guardar imágenes si no existe
os.makedirs("static/cartas", exist_ok=True)

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Modelo para los datos de entrada
class DatosCarta(BaseModel):
    nombre: Optional[str] = "Sin nombre"
    fecha_nacimiento: Optional[str] = None
    hora_nacimiento: Optional[str] = None
    lugar_nacimiento: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None

@app.get("/")
async def home():
    return {
        'aplicacion': 'Generador de Cartas Astrales',
        'version': '1.0',
        'status': 'funcionando',
        'endpoints': {
            'generar_carta': '/carta-astral/imagen',
            'test': '/test',
            'health': '/health',
            'docs': '/docs'
        }
    }

@app.get("/health")
async def health():
    return {
        'status': 'ok',
        'timestamp': str(datetime.now()),
        'message': 'Servidor funcionando correctamente'
    }

@app.get("/test")
async def test_simple():
    return {
        'status': 'funcionando',
        'mensaje': 'La aplicación está corriendo correctamente',
        'endpoint_disponible': True,
        'timestamp': str(datetime.now())
    }

@app.get("/carta-astral/imagen")
async def info_generar_carta():
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

@app.post("/carta-astral/imagen")
async def generar_carta(datos: DatosCarta, request: Request):
    try:
        # Convertir datos del modelo Pydantic a diccionario
        datos_dict = datos.dict()
        
        # Generar la carta astral (usando tu función existente)
        imagen = generar_carta_astral_imagen(datos_dict)
        
        # Crear nombre único para la imagen
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        nombre_archivo = f"carta_astral_{timestamp}_{unique_id}.png"
        ruta_archivo = f"static/cartas/{nombre_archivo}"
        
        # Guardar la imagen en el servidor
        imagen.save(ruta_archivo)
        
        # URL completa para acceder a la imagen
        base_url = str(request.base_url).rstrip('/')
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
                'nombre': datos.nombre,
                'fecha': datos.fecha_nacimiento,
                'hora': datos.hora_nacimiento,
                'lugar': datos.lugar_nacimiento
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
        raise HTTPException(
            status_code=500,
            detail={
                'success': False,
                'error': str(e),
                'mensaje': 'Error al generar la carta astral',
                'timestamp': str(datetime.now())
            }
        )

# Endpoint para descargar imágenes
@app.get("/download/{filename}")
async def download_carta(filename: str):
    file_path = f"static/cartas/{filename}"
    if os.path.exists(file_path):
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='image/png'
        )
    else:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

# Endpoint específico para N8N (formato optimizado)
@app.post("/n8n/generar-carta")
async def generar_carta_n8n(datos: Dict[Any, Any], request: Request):
    try:
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
        
        base_url = str(request.base_url).rstrip('/')
        
        return {
            'imagen_base64': img_base64,
            'imagen_url': f"{base_url}/static/cartas/{nombre_archivo}",
            'nombre_archivo': nombre_archivo,
            'success': True
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={'error': str(e), 'success': False}
        )

# Endpoint para limpiar imágenes antiguas (opcional)
@app.post("/admin/limpiar-imagenes")
async def limpiar_imagenes():
    try:
        carpeta = 'static/cartas'
        archivos_eliminados = []
        
        if os.path.exists(carpeta):
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
        raise HTTPException(status_code=500, detail={'error': str(e)})

# Para ejecutar con uvicorn
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get('PORT', 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
