import requests
from bs4 import BeautifulSoup
import pandas as pd
from transfermarket_utils import extract_transfermarket_table, injuried_games, get_all_players_from_team, is_stats_table
import os

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'
}

# Initialize empty lists to store player names and values
all_player_names = []
all_player_values = []

base_url = "https://www.transfermarkt.co.uk/premier-league/marktwerte/wettbewerb/GB1/pos//detailpos/0/altersklasse/alle/plus/1"
# TODO: find the way to get all the stats for each player
#base_url = "https://www.transfermarkt.co.uk/dusan-vlahovic/leistungsdatendetails/spieler/357498/wettbewerb/IT1/saison/2024"
base_url = 'https://www.transfermarkt.co.uk/juventus-turin/startseite/verein/506/saison_id/2024'
pageTree = requests.get(base_url, headers=headers)
soup = BeautifulSoup(pageTree.content, 'html.parser')

hrefs = get_all_players_from_team(soup)
detected_tables = []
for href in hrefs:

    player_page = os.path.join("https://www.transfermarkt.co.uk", str(href))
    #https://www.transfermarkt.co.uk/bremer/leistungsdatendetails/spieler/516716/wettbewerb/IT1/saison/2024
    player_page = f"https://www.transfermarkt.co.uk{href}"
    pageTree = requests.get(player_page, headers=headers)
    soup = BeautifulSoup(pageTree.content, 'html.parser')

    a_tags = soup.find_all('a', class_='content-link')

    for a_tag in a_tags:
        # Extract the href attribute value
        href_value = a_tag['href']
        # Check if 'leistungsdaten' is in the href
        if 'leistungsdaten' in href_value:
            print(href_value)
            break
    
    player_page = f"https://www.transfermarkt.co.uk{href_value}"
    pageTree = requests.get(player_page, headers=headers)
    soup = BeautifulSoup(pageTree.content, 'html.parser')

    tables = soup.find_all('table')
    for tbody in tables:
        if not is_stats_table(tbody):
            continue
        detected_table = extract_transfermarket_table(tbody)
        detected_table['href'] = href_value
        detected_tables.append(detected_table)

    squad_stats = pd.concat(detected_tables)
    squad_stats = squad_stats[squad_stats.matchday.map(lambda x: 'group' not in x.lower())]
    serie_a_squad_stats = squad_stats[squad_stats.for_team.map(lambda x: "Juventus FC" == x)]
    serie_a_squad_stats.to_csv('juve_stats.csv', index=False)