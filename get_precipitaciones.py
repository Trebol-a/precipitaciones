import requests
import json
from datetime import datetime

def get_precipitaciones():
    URL = "https://www.chsegura.es/server/rest/services/VISOR_CHSIC3/VISOR_PUBLICO_ETRS89_v5_Web_Capas/MapServer/13/query?f=json&returnGeometry=true&spatialRel=esriSpatialRelIntersects&geometry=%7B%22xmin%22%3A-97839.39620500008%2C%22ymin%22%3A2406849.146643002%2C%22xmax%22%3A2602527.9390530023%2C%22ymax%22%3A5107216.481901004%2C%22spatialReference%22%3A%7B%22wkid%22%3A25830%2C%22latestWkid%22%3A25830%7D%7D&geometryType=esriGeometryEnvelope&inSR=25830&outFields=*&returnCentroid=false&returnExceededLimitFeatures=false&orderByFields=DenominacionPtoMedicion%20DESC&outSR=25830"
    
    try:
        # Obtener datos
        response = requests.get(URL)
        data = response.json()
        
        # Lista de estaciones que queremos monitorizar
        estaciones_deseadas = [
            "Pluviómetro en MC en Cedacero, Rbla La Azohía",
            "Pluviómetro en MC en Los Patojos, Rbla Benipila",
            # Añade aquí más estaciones que quieras monitorizar
        ]
        
        # Filtrar las estaciones deseadas
        estaciones_filtradas = [
            feature for feature in data['features']
            if feature['attributes']['DenominacionPtoMedicion'] in estaciones_deseadas
        ]
        
        if estaciones_filtradas:
            # Crear estructura de datos con timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            datos_salida = {
                "timestamp": timestamp,
                "estaciones": []
            }
            
            # Procesar cada estación
            for estacion in estaciones_filtradas:
                datos_estacion = {
                    "nombre": estacion['attributes']['DenominacionPtoMedicion'],
                    "municipio": estacion['attributes']['Municipio'],
                    "codigo": estacion['attributes']['CodVariableHidrologica'],
                    "mediciones": {
                        "ultima_hora": estacion['attributes']['LluviaUltimaHora'],
                        "ultimas_3h": estacion['attributes']['LluviaUltimas3Horas'],
                        "ultimas_6h": estacion['attributes']['LluviaUltimas6Horas'],
                        "ultimas_12h": estacion['attributes']['LluviaUltimas12Horas'],
                        "ultimas_24h": estacion['attributes']['LluviaUltimas24Horas']
                    },
                    "coordenadas": estacion['geometry']
                }
                datos_salida["estaciones"].append(datos_estacion)
            
            # Guardar en archivo con timestamp en nombre
            timestamp_archivo = datetime.now().strftime('%Y%m%d_%H%M')
            filename = f'data/precipitaciones_{timestamp_archivo}.json'
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(datos_salida, f, indent=2, ensure_ascii=False)
            
            print(f'Datos guardados en {filename}')
            print(f'Estaciones procesadas: {len(estaciones_filtradas)}')
            return True
            
        else:
            print('No se encontraron las estaciones buscadas')
            return False
        
    except Exception as e:
        print(f'Error: {str(e)}')
        return False

if __name__ == "__main__":
    get_precipitaciones()