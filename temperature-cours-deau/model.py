import os
import sqlite3
import requests

# Liste complète des codes de départements, y compris les DOM-TOM
DEPARTEMENTS = [
    "01", "02", "03", "04", "05", "06", "07", "08", "09", "10",
    "11", "12", "13", "14", "15", "16", "17", "18", "19", "2A",
    "2B", "21", "22", "23", "24", "25", "26", "27", "28", "29",
    "30", "31", "32", "33", "34", "35", "36", "37", "38", "39",
    "40", "41", "42", "43", "44", "45", "46", "47", "48", "49",
    "50", "51", "52", "53", "54", "55", "56", "57", "58", "59",
    "60", "61", "62", "63", "64", "65", "66", "67", "68", "69",
    "70", "71", "72", "73", "74", "75", "76", "77", "78", "79",
    "80", "81", "82", "83", "84", "85", "86", "87", "88", "89",
    "90", "91", "92", "93", "94", "95", "971", "972", "973",
    "974", "976"
]

# Permet de récupérer les données des stations pour chaque département grâce à l'URL de l'API
def fetch_stations_for_departement(departement_code):
    STATIONS_URL = f"https://hubeau.eaufrance.fr/api/v1/temperature/station?code_departement={departement_code}&size=2000&exact_count=true&format=json&pretty"
    response = requests.get(STATIONS_URL)
    if response.status_code == 200:
        try:
            return response.json().get('data', [])
        except ValueError:
            print(f"Erreur de décodage JSON pour le département {departement_code}")
            return []
    else:
        print(f"Erreur {response.status_code} lors de la requête pour le département {departement_code}")
        return []

#Si la base de donnée existe déjà, cela évite de refaire la base de donnée
def database_exists(database_name):
    return os.path.exists(database_name)

# Création et insertion de la base de donnée dans les tables
def create_database_and_insert_data(database_name):
    # Se connecter à la base de données
    conn = sqlite3.connect(database_name)
    cur = conn.cursor()

# Département
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Departement (
            code_departement TEXT PRIMARY KEY,
            libelle_dep VARCHAR(50)
        );
    ''')

# Commune
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Commune (
            code_commune TEXT PRIMARY KEY,
            libelle_commune VARCHAR(500)
        );
    ''')

# Station
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Station (
            code_station TEXT PRIMARY KEY,
            libelle_station VARCHAR(500),
            latitude REAL,
            longitude REAL,
            code_commune TEXT,
            code_departement TEXT,
            FOREIGN KEY (code_commune) REFERENCES Commune (code_commune),
            FOREIGN KEY (code_departement) REFERENCES Departement (code_departement)
        );
    ''')


# Pour chaque département de la liste plus haut, on va boucler la fonction fetch pour insérer chaque données de l'API dans les tables
    for code_departement in DEPARTEMENTS:
        stations_data = fetch_stations_for_departement(code_departement)

        #   Insertion des données des départements dans la table Departement
        for station in stations_data:
            cur.execute('''INSERT OR IGNORE INTO Departement (code_departement, libelle_dep)
                           VALUES (?, ?)''',
                        (station.get('code_departement'), station.get('libelle_departement')))

        # Insertion des données des communes dans la table Commune
        for station in stations_data:
            cur.execute('''INSERT OR IGNORE INTO Commune (code_commune, libelle_commune)
                           VALUES (?, ?)''',
                        (station.get('code_commune'), station.get('libelle_commune')))

        # Insertion des données des stations dans la table Station si elles n'existent pas déjà
        for station in stations_data:
            cur.execute('''
                SELECT EXISTS(SELECT 1 FROM Station WHERE code_station = ?)
            ''', (station.get('code_station'),))
            exists = cur.fetchone()[0]
            if not exists:
                cur.execute('''INSERT INTO Station (code_station, libelle_station, latitude, longitude, code_commune, code_departement)
                               VALUES (?, ?, ?, ?, ?, ?)''',
                            (station.get('code_station'), station.get('libelle_station'), station.get('latitude'), station.get('longitude'), station.get('code_commune'), station.get('code_departement')))

    conn.commit()
    conn.close()

database_name = "temp_cours_deau.db"

# Créer la base de données et insérer les données si elle n'existe pas
if not database_exists(database_name):
    create_database_and_insert_data(database_name)

#Va récupérer les points de mesure des stations (Nom de la station, lat, longit)
def get_measurement_points():
    conn = sqlite3.connect(database_name)
    cur = conn.cursor()
    cur.execute('SELECT libelle_station, latitude, longitude FROM Station')
    points = cur.fetchall()
    conn.close()
    return points

#Va prendre toutes les données des communes triées par leur nom
def get_communes():
    conn = sqlite3.connect(database_name)
    cur = conn.cursor()
    cur.execute('SELECT code_commune, libelle_commune FROM Commune ORDER BY libelle_commune')
    communes = cur.fetchall()
    conn.close()
    return communes

#Va prendre les données des températures d'une commune choisi en joignant les tables Station et Chronique_temp
def get_data_for_commune(code_commune):
    conn = sqlite3.connect(database_name)
    cur = conn.cursor()
    cur.execute('''
        SELECT s.libelle_station, ct.Date_debut_mesure, ct.Resultat_mesure_temp, ct.Unit_mesure_temp
        FROM Station s
        JOIN Chronique_temp ct ON s.code_station = ct.code_station
        WHERE s.code_commune = ?
    ''', (code_commune,))
    data = cur.fetchall()
    conn.close()
    return data

def get_stations_by_departement(code_departement):
    conn = sqlite3.connect(database_name)
    cur = conn.cursor()
    cur.execute('SELECT code_station, libelle_station FROM Station WHERE code_departement = ?', (code_departement,))
    stations = cur.fetchall()
    conn.close()
    return stations

def get_departement_name(code_departement):
    conn = sqlite3.connect(database_name)
    cur = conn.cursor()
    cur.execute('SELECT libelle_dep FROM Departement WHERE code_departement = ?', (code_departement,))
    departement_name = cur.fetchone()
    conn.close()
    return departement_name[0] if departement_name else None

def get_commune_name(code_commune):
    conn = sqlite3.connect(database_name)
    cur = conn.cursor()
    cur.execute('SELECT libelle_commune FROM Commune WHERE code_commune = ?', (code_commune,))
    commune_name = cur.fetchone()
    conn.close()
    return commune_name[0] if commune_name else None

def get_stations_by_commune(code_commune):
    conn = sqlite3.connect(database_name)
    cur = conn.cursor()
    cur.execute('SELECT code_station, libelle_station FROM Station WHERE code_commune = ?', (code_commune,))
    stations = cur.fetchall()
    conn.close()
    return stations
