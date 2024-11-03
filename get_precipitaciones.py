import requests
import json
from datetime import datetime

def get_precipitaciones():
    URL = "https://www.chsegura.es/server/rest/services/VISOR_CHSIC3/VISOR_PUBLICO_ETRS89_v5_Web_Capas/MapServer/13/query?f=json&returnGeometry=true&spatialRel=esriSpatialRelIntersects&geometry=%7B%22xmin%22%3A-97839.39620500008%2C%22ymin%22%3A2406849.146643002%2C%22xmax%22%3A2602527.9390530023%2C%22ymax%22%3A5107216.481901004%2C%22spatialReference%22%3A%7B%22wkid%22%3A25830%2C%22latestWkid%22%3A25830%7D%7D&geometryType=esriGeometryEnvelope&inSR=25830&outFields=*&returnCentroid=false&returnExceededLimitFeatures=false&orderByFields=DenominacionPtoMedicion%20DESC&outSR=25830"
    
    try:
        # Obtener datos
        response = requests.get(URL)
        data = response.json()
        
        # Filtrar el pluviómetro específico
        pluviometro = next(
            (feature for feature in data['features'] 
             if feature['attributes']['DenominacionPtoMedicion'] == "Pluviómetro en MC en Cedacero, Rbla La Azohía"),
            None
        )
        
        if pluviometro:
            # Crear nombre de archivo con timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')
            filename = f'data/precipitaciones_{timestamp}.json'
            
            # Guardar datos
            with open(filename, 'w') as f:
                json.dump(pluviometro, f, indent=2)
            
            print(f'Datos guardados en {filename}')
            return True
            
        print('Pluviómetro no encontrado')
        return False
        
    except Exception as e:
        print(f'Error: {str(e)}')
        return False

if __name__ == "__main__":
    get_precipitaciones()

