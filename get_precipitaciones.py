import requests
import json
import os
from datetime import datetime

# Parámetros configurables
CADUCIDAD_DIAS = 3  # Antigüedad máxima en días
CONSULTA_MINUTOS = 15  # Frecuencia de generación en minutos
MAXIMO_ARCHIVOS = (24 * 60 // CONSULTA_MINUTOS) * CADUCIDAD_DIAS  # Archivos permitidos

URL = "https://www.chsegura.es/server/rest/services/VISOR_CHSIC3/VISOR_PUBLICO_ETRS89_v5_Web_Capas/MapServer/13/query?f=json&returnGeometry=true&spatialRel=esriSpatialRelIntersects&geometry=%7B%22xmin%22%3A-97839.39620500008%2C%22ymin%22%3A2406849.146643002%2C%22xmax%22%3A2602527.9390530023%2C%22ymax%22%3A5107216.481901004%2C%22spatialReference%22%3A%7B%22wkid%22%3A25830%2C%22latestWkid%22%3A25830%7D%7D&geometryType=esriGeometryEnvelope&inSR=25830&outFields=*&returnCentroid=false&returnExceededLimitFeatures=false&orderByFields=DenominacionPtoMedicion%20DESC&outSR=25830"

def fetch_data(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con la API: {e}")
        return None

def process_data(data, estaciones_deseadas):
    if not data or 'features' not in data:
        print("Error: Respuesta inválida.")
        return []

    return [
        feature for feature in data['features']
        if feature['attributes']['DenominacionPtoMedicion'] in estaciones_deseadas
    ]

def controlar_archivos(directorio, maximo_archivos, caducidad_dias):
    """
    Mantiene el número de archivos en el directorio por debajo de `maximo_archivos`
    y elimina los archivos más viejos que `caducidad_dias`.
    """
    archivos = [
        os.path.join(directorio, archivo) for archivo in os.listdir(directorio)
        if os.path.isfile(os.path.join(directorio, archivo))
    ]
    
    # Ordenar por fecha de modificación (antiguos primero)
    archivos.sort(key=lambda x: os.path.getmtime(x))
    
    fecha_limite = datetime.now() - timedelta(days=caducidad_dias)
    
    for archivo in archivos:
        if len(archivos) <= maximo_archivos:
            break
        
        fecha_modificacion = datetime.fromtimestamp(os.path.getmtime(archivo))
        
        if fecha_modificacion < fecha_limite or len(archivos) > maximo_archivos:
            os.remove(archivo)
            archivos.remove(archivo)
            print(f"Archivo eliminado: {archivo}")
            
def controlar_archivos_old(directorio, maximo_archivos):
    """
    Mantiene el número de archivos en el directorio por debajo de `maximo_archivos`.
    Elimina el archivo más viejo si se supera el límite.
    """
    archivos = [
        os.path.join(directorio, archivo) for archivo in os.listdir(directorio)
        if os.path.isfile(os.path.join(directorio, archivo))
    ]
    
    # Ordenar por fecha de modificación (antiguos primero)
    archivos.sort(key=lambda x: os.path.getmtime(x))
    
    if len(archivos) > maximo_archivos: Traceback (most recent call last):
  File "/home/runner/work/precipitaciones/precipitaciones/get_precipitaciones.py", line 135, in <module>
    get_precipitaciones()
  File "/home/runner/work/precipitaciones/precipitaciones/get_precipitaciones.py", line 127, in get_precipitaciones
    save_data(estaciones_procesadas)
  File "/home/runner/work/precipitaciones/precipitaciones/get_precipitaciones.py", line 81, in save_data
    controlar_archivos(output_dir, MAXIMO_ARCHIVOS)
TypeError: controlar_archivos() missing 1 required positional argument: 'caducidad_dias'
        archivo_mas_viejo = archivos[0]
        os.remove(archivo_mas_viejo)
        print(f"Archivo eliminado por superar el límite: {archivo_mas_viejo}")

def save_data(estaciones, output_dir='data'):
    # Crear el directorio si no existe
    os.makedirs(output_dir, exist_ok=True)

    # Controlar archivos antiguos
    controlar_archivos(output_dir, MAXIMO_ARCHIVOS, CADUCIDAD_DIAS)

    # Guardar el nuevo archivo
    timestamp_archivo = datetime.now().strftime('%Y%m%d_%H%M')
    filename = f'{output_dir}/precipitaciones_{timestamp_archivo}.json'
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    datos_salida = {
        "timestamp": timestamp,
        "estaciones": estaciones
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(datos_salida, f, indent=2, ensure_ascii=False)
    
    print(f'Datos guardados en {filename}')
    return filename

def get_precipitaciones():
    data = fetch_data(URL)
    if not data:
        return False
    
    estaciones_deseadas = [
        "Pluviómetro en MC en Cedacero, Rbla La Azohía",
        "Pluviómetro en MC en Los Patojos, Rbla Benipila",
    ]
    estaciones_filtradas = process_data(data, estaciones_deseadas)
    
    if estaciones_filtradas:
        estaciones_procesadas = []
        for estacion in estaciones_filtradas:
            estaciones_procesadas.append({
                "nombre": estacion['attributes']['DenominacionPtoMedicion'],
                "municipio": estacion['attributes'].get('Municipio', 'Desconocido'),
                "codigo": estacion['attributes'].get('CodVariableHidrologica', 'N/A'),
                "mediciones": {
                    "ultima_hora": estacion['attributes'].get('LluviaUltimaHora', 0),
                    "ultimas_3h": estacion['attributes'].get('LluviaUltimas3Horas', 0),
                    "ultimas_6h": estacion['attributes'].get('LluviaUltimas6Horas', 0),
                    "ultimas_12h": estacion['attributes'].get('LluviaUltimas12Horas', 0),
                    "ultimas_24h": estacion['attributes'].get('LluviaUltimas24Horas', 0),
                },
                "coordenadas": estacion.get('geometry', {})
            })
        
        save_data(estaciones_procesadas)
        print(f'Estaciones procesadas: {len(estaciones_procesadas)}')
        return True
    else:
        print('No se encontraron las estaciones buscadas.')
        return False

if __name__ == "__main__":
    get_precipitaciones()
