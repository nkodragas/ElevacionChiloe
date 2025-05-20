import os
import requests
import time
import geopandas as gpd
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt

# Function to get elevation from Open Elevation API
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

# Function to classify terrain type based on elevation
def clasificar_terreno(elevacion):
    if elevacion is None:
        return "Error en la elevación"
    
    if elevacion > 400:  # Montaña if elevation is greater than 400 meters
        return "Montaña"
    elif 100 <= elevacion <= 400:  # Cerro if elevation is between 100 and 400 meters
        return "Cerro"
    else:  # Planicie if elevation is less than 100 meters
        return "Planicie"

# Function to generate a list of coordinates within a shape
def generar_coordenadas_en_shape(shape, paso):
    minx, miny, maxx, maxy = shape.bounds
    coordenadas = []
    lat = miny
    while lat <= maxy:
        lon = minx
        while lon <= maxx:
            point = gpd.points_from_xy([lon], [lat])
            if shape.contains(point).any():
                coordenadas.append((lat, lon))
            lon += paso
        lat += paso
    return coordenadas

# Function to analyze selected comuna
def analizar_comuna(comuna_name, paso, area_size):
    global gdf
    comuna_shape = gdf[gdf['comuna'] == comuna_name].geometry

    if comuna_shape.empty:
        print(f"Comuna '{comuna_name}' no encontrada en el archivo GeoJSON.")
    else:
        # Generate coordinates within the comuna shape
        comuna_shape = comuna_shape.iloc[0]
        coordenadas = generar_coordenadas_en_shape(comuna_shape, paso)

        # Initialize variables to count km²
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
                km2_totales += area_size  # Each grid cell is area_size km²

                if tipo_terreno == "Montaña":
                    km2_montanas += area_size
                elif tipo_terreno == "Cerro":
                    km2_cerros += area_size
                elif tipo_terreno == "Planicie":
                    km2_planicies += area_size

            # Hacer una pequeña pausa para evitar sobrecargar la API
            time.sleep(0.1)  # Espera de 0.1 segundos entre cada solicitud (ajustable si es necesario)

        # Mostrar los resultados finales
        print("\nResultados finales:")
        print(f"Área total: {km2_totales} km²")
        print(f"Área de Montañas: {km2_montanas} km²")
        print(f"Área de Cerros: {km2_cerros} km²")
        print(f"Área de Planicies: {km2_planicies} km²")

        # Draw the shape of the comuna
        fig, ax = plt.subplots()
        gdf[gdf['comuna'] == comuna_name].plot(ax=ax, color='#474196')
        plt.title(f"Shape of {comuna_name}")
        plt.show()

# Function to generate elevation profile for selected comuna
def generar_grafico_comuna(comuna_name):
    global gdf
    comuna_shape = gdf[gdf['comuna'] == comuna_name].geometry

    if comuna_shape.empty:
        print(f"Comuna '{comuna_name}' no encontrada en el archivo GeoJSON.")
    else:
        comuna_shape = comuna_shape.iloc[0]
        minx, miny, maxx, maxy = comuna_shape.bounds
        latitud_fija = (miny + maxy) / 2
        longitud_min = minx
        longitud_max = maxx
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
            plt.plot(longitudes, elevaciones, color='#474196', marker='o')
            plt.title(f"Perfil de elevación de {comuna_name} (latitud fija)")
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

# Load GeoJSON data
geojson_path = "Comunas_de_Chiloe.geojson"
gdf = gpd.read_file(geojson_path)

# Filter only comunas from Chiloe (assuming a specific column or criteria to identify them)
chiloe_comunas = gdf[gdf['region'] == 'Chiloe']  # Adjust the filter condition based on your data
comuna_names = chiloe_comunas['comuna'].unique()

# Create the main window
root = tk.Tk()
root.title("Seleccione la Comuna")

# Create a dropdown menu
comuna_var = tk.StringVar()
comuna_dropdown = ttk.Combobox(root, textvariable=comuna_var)
comuna_dropdown['values'] = comuna_names
comuna_dropdown.grid(column=0, row=0, padx=10, pady=10)

# Create buttons to analyze the selected comuna with different grid sizes
def analizar_1km2():
    analizar_comuna(comuna_var.get(), paso=0.01, area_size=1)

def analizar_10km2():
    analizar_comuna(comuna_var.get(), paso=0.03, area_size=10)

def analizar_100km2():
    analizar_comuna(comuna_var.get(), paso=0.1, area_size=100)

button_1km2 = tk.Button(root, text="1 km²", command=analizar_1km2)
button_1km2.grid(column=0, row=1, padx=10, pady=10)

button_10km2 = tk.Button(root, text="10 km²", command=analizar_10km2)
button_10km2.grid(column=1, row=1, padx=10, pady=10)

button_100km2 = tk.Button(root, text="100 km²", command=analizar_100km2)
button_100km2.grid(column=2, row=1, padx=10, pady=10)

# Create a button to generate the elevation profile for the selected comuna
button_comuna_grafico = tk.Button(root, text="Generar Gráfico de Comuna", command=lambda: generar_grafico_comuna(comuna_var.get()))
button_comuna_grafico.grid(column=0, row=2, columnspan=3, padx=10, pady=10)

# Run the application
root.mainloop()