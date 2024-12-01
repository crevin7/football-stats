
import requests
from bs4 import BeautifulSoup
from injuries_per_team import get_injuries_and_active_players_per_team

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'
}


def get_serie_a_squads():
    base_url = 'https://www.transfermarkt.co.uk/serie-a/startseite/wettbewerb/IT1'
    pageTree = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(pageTree.content, 'html.parser')

    tables = soup.find_all('table', {"class": "items"})

    table = tables[0]
    rows = table.find_all('tr')
    squads_hyperlinks = []
    for row in rows:
        link = row.find('a')  # First <a> tag in the row
        if not link:
            continue
        title = link.get('title')
        href = link.get('href')
        if title is not None and href is not None:
            squads_hyperlinks.append((title, href))

    return squads_hyperlinks

serie_a_squads = get_serie_a_squads()

base_url = 'https://www.transfermarkt.co.uk'
"""
squad_url = 'https://www.transfermarkt.co.uk/atalanta-bergamo/startseite/verein/800/saison_id/2024'

get_injuries_and_active_players_per_team(squad_url, team_name='Atalanta BC')
"""
team_stats = {}
for squad, hlink in serie_a_squads:
    print(squad)
    squad_url = f"{base_url}{hlink}"
    print(squad_url)
    n_players, days_of_injuries = get_injuries_and_active_players_per_team(squad_url, team_name=squad)
    print()
    team_stats[squad] = {'n_players': n_players, 'days_of_injuries': days_of_injuries}

import json

with open('team_stats.json', 'w') as fp:
    json.dump(team_stats, fp)