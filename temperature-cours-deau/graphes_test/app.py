from flask import Flask, render_template, request
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from io import BytesIO
import requests

app = Flask(__name__)
database_name = "temp_cours_deau.db"

@app.route('/')
def index():
    conn = sqlite3.connect(database_name)
    cur = conn.cursor()
    cur.execute('SELECT DISTINCT code_commune, libelle_commune FROM Commune ORDER BY libelle_commune')
    communes = cur.fetchall()
    conn.close()
    return render_template('index.html', communes=communes)

@app.route('/commune/<code_commune>')
def commune(code_commune):
    conn = sqlite3.connect(database_name)
    cur = conn.cursor()
    cur.execute('SELECT libelle_commune FROM Commune WHERE code_commune = ?', (code_commune,))
    commune_name = cur.fetchone()[0]
    cur.execute('SELECT code_station, libelle_station FROM Station WHERE code_commune = ?', (code_commune,))
    stations = cur.fetchall()
    conn.close()
    return render_template('commune.html', commune_name=commune_name, code_commune=code_commune, stations=stations)

@app.route('/plot/<code_station>')
def plot_temperature(code_station):
    data = fetch_chroniques_for_station(code_station)
    
    # Traitement des données pour le graphique ici
    dates = [entry['date_debut_mesure'] for entry in data]
    temperatures = [entry['resultat_mesure_temp'] for entry in data]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(dates, temperatures, marker='o', linestyle='-')
    ax.set_title('Température de l\'eau au fil du temps')
    ax.set_xlabel('Date')
    ax.set_ylabel('Température (°C)')
    ax.grid(True)

    output = BytesIO()
    FigureCanvas(fig).print_png(output)
    plt.close(fig)

    # Encodage de l'image en base64 pour l'affichage dans le template
    image_base64 = output.getvalue().encode('base64').strip()
    plot_url = 'data:image/png;base64,' + image_base64

    return render_template('plot.html', plot_url=plot_url)

# Fonction pour récupérer les chroniques de température à partir de l'API
def fetch_chroniques_for_station(code_station):
    chroniques_data = []
    CHRONIQUE_URL = f"https://hubeau.eaufrance.fr/api/v1/temperature/chronique?code_station={code_station}&size=500&sort=desc&pretty"
    page = 1
    while True:
        response = requests.get(f"{CHRONIQUE_URL}&page={page}")
        if response.status_code == 200 or response.status_code == 206:
            try:
                data = response.json().get('data', [])
                if not data:
                    break
                chroniques_data.extend(data)
                page += 1
                if page * 2000 > 20000:
                    break  # Stop if the limit is reached
            except ValueError:
                break
        else:
            break
    return chroniques_data

if __name__ == '__main__':
    app.run(debug=True)
