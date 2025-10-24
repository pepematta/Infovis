# 🌎 Visualización de Positividad Musical por País

Este proyecto genera un **mapa interactivo** que muestra el nivel promedio de *valence* (positividad emocional) de las canciones más populares en Spotify para cada país, y permite **reproducir un fragmento de audio** representativo a través de la API pública de iTunes.

---

## 🎯 Descripción

El script `main.py` analiza una base de datos de Spotify con las canciones más escuchadas por país.  
Para cada país, calcula el promedio de **valence** dentro del *Top 50*, y selecciona la canción cuyo valor esté **más cercano al promedio** y que además tenga un **preview disponible en Apple Music**.

El resultado se visualiza en un mapa mundial interactivo, donde:
- El color indica el promedio de *valence* del país (más amarillo = más positivo).  
- Al **pasar el mouse**, se muestra la canción representativa.  
- Al **hacer clic**, se reproduce un fragmento de 30 segundos (cuando está disponible).  

---

## 🧠 Tecnologías utilizadas

- **Python 3.10+**
- **pandas** — análisis y manipulación de datos  
- **plotly.express** — visualización interactiva (choropleth map)  
- **country_converter** — estandarización de nombres de países  
- **requests** — consultas a la API pública de iTunes  

---

## ⚙️ Instalación

Para interactuar con la visualización, basta con descargar y abrir en el navegador el archivo mapa_valence_preview.html (subido). El proceso para generar dicho documento es el siguiente:

1. Clona este repositorio o copia el archivo `main.py` en una carpeta.

2. En la misma carpeta, guarda el dataset con el nombre universal_top_spotify_songs.csv, obteniéndolo del siguiente link (era muy pesado para subirlo a github):
https://www.kaggle.com/datasets/asaniczka/top-spotify-songs-in-73-countries-daily-updated

4. Instala las dependencias: pandas plotly country_converter requests re

5. Ejecuta el script: main.py

6. Se generará el archivo mapa_valence_preview.html, que debes abrir en el navegador.
