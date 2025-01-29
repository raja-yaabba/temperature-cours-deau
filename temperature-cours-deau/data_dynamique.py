import requests

def fetch_chroniques_for_station_with_date(code_station, selected_date):
    chroniques_data = []
    CHRONIQUE_URL = f"https://hubeau.eaufrance.fr/api/v1/temperature/chronique?code_station={code_station}&date_fin_mesure={selected_date}&size=100&sort=desc"
    response = requests.get(CHRONIQUE_URL)
    print(response.status_code)
    if response.status_code == 200 or response.status_code==206:
        try:
            chroniques_data = response.json().get('data', [])
        except ValueError:
            pass
    else:
        print('pas bonne URL')
    return chroniques_data



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

