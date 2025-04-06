import requests
import matplotlib.pyplot as plt

# Datos del terreno de Castro
latitud_fija = -42.50
longitud_min = -73.80
longitud_max = -73.50
cantidad_puntos = 50  # puedes ajustar este número

# Generar lista de longitudes
longitudes = [longitud_min + i * (longitud_max - longitud_min) / (cantidad_puntos - 1) for i in range(cantidad_puntos)]

# Preparar ubicaciones para la API
locations = [{"latitude": latitud_fija, "longitude": lon} for lon in longitudes]

# Consultar la API
api_url = "https://api.open-elevation.com/api/v1/lookup"
response = requests.post(api_url, json={"locations": locations})

# Procesar y graficar
if response.status_code == 200:
    data = response.json()
    elevaciones = [p['elevation'] for p in data['results']]
    
    # Graficar
    plt.figure(figsize=(10, 5))
    plt.plot(longitudes, elevaciones, color='green', marker='o')
    plt.title("Perfil de elevación de Castro (latitud fija)")
    plt.xlabel("Longitud (°)")
    plt.ylabel("Elevación (m)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    
    # Imprimir tabla
    print("Longitud\tElevación (m)")
    for lon, elev in zip(longitudes, elevaciones):
        print(f"{lon:.5f}\t{elev}")
else:
    print("Error al consultar la API:", response.status_code)
