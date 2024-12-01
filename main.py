import requests
from bs4 import BeautifulSoup
import pandas as pd
from transfermarket_utils import extract_transfermarket_table, injuried_games, get_all_players_from_team, is_stats_table
import os

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'
}

# TODO: find the way to get all the stats for all the teams
base_url = 'https://www.transfermarkt.co.uk/juventus-turin/startseite/verein/506/saison_id/2024'
pageTree = requests.get(base_url, headers=headers)
soup = BeautifulSoup(pageTree.content, 'html.parser')

hrefs = get_all_players_from_team(soup)
squad_stats = []

MIN_MINUTES_PER_SEASON = 90*2

for href in hrefs:

    player_page = os.path.join("https://www.transfermarkt.co.uk", str(href))
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
        player_stats_df = extract_transfermarket_table(tbody)
        player_stats_df['href'] = href_value

        if player_stats_df.minutes_played.sum() < MIN_MINUTES_PER_SEASON:
            continue
        squad_stats.append(player_stats_df)

    squad_stats_df = pd.concat(squad_stats)

squad_stats = squad_stats[squad_stats.matchday.map(lambda x: 'group' not in x.lower())]
serie_a_squad_stats = squad_stats[squad_stats.for_team.map(lambda x: "Juventus FC" == x)]
serie_a_squad_stats.to_csv('juve_stats.csv', index=False)

