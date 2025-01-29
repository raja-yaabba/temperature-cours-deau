import matplotlib.pyplot as plt
from io import BytesIO
import base64
import pandas as pd
from matplotlib.dates import DateFormatter
from datetime import datetime
from fetch_chroniques import fetch_chroniques_for_station

def tracer_graphique(legende_x, legende_y, titre):
    plt.xlabel(legende_x)
    plt.ylabel(legende_y)
    plt.title(titre)
    image_stream = BytesIO()
    plt.savefig(image_stream, format='png')
    plt.close()
    image_base64 = base64.b64encode(image_stream.getvalue()).decode('utf-8')
    return f'data:image/png;base64,{image_base64}'

def tracer_courbe(abscisses, ordonnees, parametre, unite):
    legende_x = f"Période du {abscisses[0]} au {abscisses[-1]}"
    legende_y = f"{parametre} ({unite})"
    titre = f"{parametre} : Évolution au cours du temps"
    plt.figure(figsize=(10, 6))
    plt.plot(abscisses, ordonnees, marker='o', linestyle='-', label=f"{parametre}")
    plt.legend()
    return tracer_graphique(legende_x, legende_y, titre)

def moyennes_mensuelles_temperature_par_commune(code_commune):
    # Récupérer les données chroniques de température pour une commune spécifique
    stations = fetch_stations_for_commune(code_commune)
    if not stations:
        print(f"Aucune station trouvée pour la commune avec le code {code_commune}")
        return None

    # Collecter toutes les données chroniques de température pour chaque station
    all_chroniques_data = []
    for station in stations:
        chroniques_data = fetch_chroniques_for_station(station['code_station'])
        all_chroniques_data.extend(chroniques_data)

    # Créer un DataFrame Pandas avec les données chroniques
    df = pd.DataFrame(all_chroniques_data)

    # Adapter les noms de colonnes si nécessaire
    # Ici, nous supposons que les données contiennent une clé différente pour la date de début de mesure
    if 'Date_debut_mesure' in df.columns:
        df['date_debut_mesure'] = pd.to_datetime(df['Date_debut_mesure'], format='%Y-%m-%d')
    elif 'autre_nom_de_la_cle_date' in df.columns:
        df['date_debut_mesure'] = pd.to_datetime(df['autre_nom_de_la_cle_date'], format='%Y-%m-%d')
    else:
        print("Impossible de trouver la colonne de date de début de mesure dans les données.")
        return None

    # Calculer les moyennes mensuelles de température
    monthly_avg = df.resample('M', on='date_debut_mesure').mean()

    # Créer le graphique des moyennes mensuelles
    abscisses = monthly_avg.index.to_timestamp()
    ordonnees = monthly_avg['resultat_mesure_temp'].values
    parametre = "Température"
    unite = "°C"

    return tracer_courbe(abscisses, ordonnees, parametre, unite)

# Exemple d'utilisation pour une commune spécifique avec code_commune = '01001'
code_commune = '01001'
graphique = moyennes_mensuelles_temperature_par_commune(code_commune)
if graphique:
    print("Graphique généré avec succès!")
    print(graphique)
else:
    print("Impossible de générer le graphique.")
