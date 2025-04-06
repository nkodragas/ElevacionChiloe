import requests
import time

# Función para obtener la elevación desde Open Elevation API
def obtener_elevacion(lat, lon):
    url = "https://api.open-elevation.com/api/v1/lookup"
    params = {
        "locations": f"{lat},{lon}"
    }
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        return data['results'][0]['elevation']
    else:
        print(f"Error en la solicitud para ({lat}, {lon}): {response.status_code}")
        return None

# Función para clasificar el tipo de terreno según la elevación
def clasificar_terreno(elevacion):
    if elevacion is None:
        return "Error en la elevación"
    
    if elevacion > 400:  # Montaña si la elevación es mayor a 2000 metros
        return "Montaña"
    elif 100 <= elevacion <= 400:  # Cerro si la elevación está entre 500 y 2000 metros
        return "Cerro"
    else:  # Planicie si la elevación es menor a 500 metros
        return "Planicie"

# Función para generar una lista de coordenadas dentro de un área rectangular (en cuadrículas de 1 km²)
def generar_coordenadas(lat_min, lat_max, lon_min, lon_max, paso=0.01):
    """
    Genera las coordenadas para las esquinas de las cuadrículas de 1 km² dentro de un área rectangular.
    lat_min, lat_max: límites de latitud (en grados)
    lon_min, lon_max: límites de longitud (en grados)
    paso: la distancia entre puntos en grados (0.01 ~ 1 km)
    """
    coordenadas = []
    lat = lat_min
    while lat <= lat_max:
        lon = lon_min
        while lon <= lon_max:
            coordenadas.append((lat, lon))
            lon += paso
        lat += paso
    return coordenadas

# Definir el área de interés: límites de latitud y longitud para un área rectangular de Quellón
lat_min = -43.15  # Latitud mínima de Quellón
lat_max = -43.05  # Latitud máxima de Quellón
lon_min = -73.65  # Longitud mínima de Quellón
lon_max = -73.55  # Longitud máxima de Quellón

# Generar las coordenadas en el área de Quellón (en cuadrículas de 1 km²)
coordenadas = generar_coordenadas(lat_min, lat_max, lon_min, lon_max, paso=0.01)

# Inicializar variables para contar km²
km2_totales = 0
km2_montanas = 0
km2_cerros = 0
km2_planicies = 0

# Cantidad total de coordenadas a procesar
total_coordenadas = len(coordenadas)

# Obtener la elevación y clasificar el terreno para cada cuadrícula
for i, (lat, lon) in enumerate(coordenadas):
    # Mostrar el estado de la solicitud (cada vez que se obtiene una coordenada)
    print(f"Recuperando información para la coordenada {i+1}/{total_coordenadas} ({lat}, {lon})...")

    # Obtenemos las elevaciones de las esquinas de la cuadrícula (por simplicidad, tomamos solo una coordenada de la cuadrícula)
    elevacion = obtener_elevacion(lat, lon)
    tipo_terreno = clasificar_terreno(elevacion)

    # Si la elevación se pudo obtener, contar el km²
    if elevacion is not None:
        km2_totales += 1  # Cada cuadrícula es de 1 km²

        if tipo_terreno == "Montaña":
            km2_montanas += 1
        elif tipo_terreno == "Cerro":
            km2_cerros += 1
        elif tipo_terreno == "Planicie":
            km2_planicies += 1

    # Hacer una pequeña pausa para evitar sobrecargar la API
    time.sleep(0.1)  # Espera de 0.1 segundos entre cada solicitud (ajustable si es necesario)

# Mostrar los resultados finales
print("\nResultados finales:")
print(f"Área total: {km2_totales} km²")
print(f"Área de Montañas: {km2_montanas} km²")
print(f"Área de Cerros: {km2_cerros} km²")
print(f"Área de Planicies: {km2_planicies} km²")
