from flask import Flask, render_template, request, redirect, url_for
import model
import data_dynamique
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/choice', methods=['GET', 'POST'])
def choice():
    if request.method == 'POST':
        choice = request.form.get('choice')
        if choice == 'departement':
            code_departement = request.form.get('departement')
            return redirect(url_for('stations', choice='departement', code=code_departement))
        elif choice == 'commune':
            code_commune = request.form.get('commune')
            return redirect(url_for('stations', choice='commune', code=code_commune))

    communes = model.get_communes()
    departements = model.DEPARTEMENTS
    return render_template('choice.html', communes=communes, departements=departements)

@app.route('/stations/<choice>/<code>', methods=['GET', 'POST'])
def stations(choice, code):
    if choice == 'departement':
        stations = model.get_stations_by_departement(code)
        name = model.get_departement_name(code)
    elif choice == 'commune':
        stations = model.get_stations_by_commune(code)
        name = model.get_commune_name(code)

    if request.method == 'POST':
        station_id = request.form['station']
        return redirect(url_for('chroniques', station_id=station_id))

    return render_template('station.html', stations=stations, choice=choice, name=name)

@app.route('/chroniques/<station_id>', methods=['GET', 'POST'])
def chroniques(station_id):
    if request.method == 'POST':
        selected_date = request.form['date']
        data = data_dynamique.fetch_chroniques_for_station_with_date(station_id, selected_date)
        return render_template('chroniques.html', station_id=station_id, data=data, selected_date=selected_date)
    else:
        data = data_dynamique.fetch_chroniques_for_station(station_id)
        return render_template('chroniques.html', station_id=station_id, data=data)

@app.route('/carte')
def carte():
    points = model.get_measurement_points()
    return render_template('carte.html', points=points)

@app.route('/station_chroniques', methods=['POST'])
def station_chroniques():
    station_id = request.form['station']
    return redirect(url_for('chroniques', station_id=station_id))

@app.route('/data_chroniques/<station_id>')
def data_chroniques(station_id):
    # URL de l'API Hubeau pour les données chroniques de température
    CHRONIQUE_URL = f"https://hubeau.eaufrance.fr/api/v1/temperature/chronique?code_station={station_id}&size=100&sort=desc&pretty"

    try:
        response = requests.get(CHRONIQUE_URL)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print(f"Erreur lors de la requête à l'API : {e}")
        data = {"data": []} 

    chroniques = [
        {"date_mesure_temp": item.get("date_mesure_temp"), "resultat": item.get("resultat")}
        for item in data.get("data", [])
    ]

    return render_template('donnee_chron_carte.html', station_id=station_id, data=chroniques)

if __name__ == '__main__':
    app.run(debug=True)
