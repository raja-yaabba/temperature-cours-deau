import folium
import sqlite3

# Connexion à la base de données SQLite
conn = sqlite3.connect('temp_cours_deau.db')
cursor = conn.cursor()

# Exemple de requête pour extraire les stations
cursor.execute("SELECT code_station, libelle_station, latitude, longitude FROM Station")
stations = cursor.fetchall()

# Fermer la connexion à la base de données
conn.close()

# Créer une carte centrée sur une position initiale (par exemple, le département du Loiret)
map_center = [48.816895156, 2.41962979]  # Coordonnées approximatives du département du Loiret
mymap = folium.Map(location=map_center, zoom_start=10)

# Ajouter des marqueurs pour chaque station
for station in stations:
    code_station = station[0]
    name = station[1]
    latitude = station[2]
    longitude = station[3]

    # Ajouter un marqueur pour la station avec un lien vers les données chroniques
    folium.Marker(
        location=[latitude, longitude],
        popup=f'<a href="/data_chroniques/{code_station}">{name}</a>',
        icon=folium.Icon(icon="info-sign")
    ).add_to(mymap)

# Sauvegarder la carte dans un fichier HTML
mymap.save("templates/carte.html")
