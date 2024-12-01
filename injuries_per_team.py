# a script to get the number of injuries per for_team

import requests
from bs4 import BeautifulSoup
import pandas as pd
from transfermarket_utils import extract_transfermarket_table, injuried_games, get_all_players_from_team, is_stats_table

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'
}

base_url = 'https://www.transfermarkt.co.uk/juventus-turin/startseite/verein/506/saison_id/2024'
MIN_MINUTES_PER_SEASON = 90*1

def get_stast_page_table(player_page):
    pageTree = requests.get(player_page, headers=headers)
    soup = BeautifulSoup(pageTree.content, 'html.parser')

    a_tags = soup.find_all('a', class_='content-link')

    for a_tag in a_tags:
        # Extract the href attribute value
        href_value = a_tag['href']
        # Check if 'leistungsdaten' is in the href
        if 'leistungsdaten' in href_value:
            return href_value
    
    return 

def get_injuries_and_active_players_per_team(base_url, team_name, min_mins_per_season = MIN_MINUTES_PER_SEASON):

    pageTree = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(pageTree.content, 'html.parser')

    hrefs = get_all_players_from_team(soup)
    squad_stats = []
    for href in hrefs:

        player_page = f"https://www.transfermarkt.co.uk{href}"
        
        href_value = get_stast_page_table(player_page)

        player_stats_page = f"https://www.transfermarkt.co.uk{href_value}"
        pageTree = requests.get(player_stats_page, headers=headers)
        soup = BeautifulSoup(pageTree.content, 'html.parser')

        tables = soup.find_all('table')
        for tbody in tables:
            if not is_stats_table(tbody):
                continue
            player_stats_df = extract_transfermarket_table(tbody)
            player_stats_df['href'] = href_value
            
            # only serie_a data
            player_stats_df = player_stats_df[player_stats_df.matchday.map(lambda x: 'group' not in x.lower())] 
            if len(player_stats_df) == 0:
                continue
            player_stats_df = player_stats_df[player_stats_df.for_team.map(lambda x: team_name == x)]
            if len(player_stats_df) == 0:
                continue
            try:
                if player_stats_df.minutes_played.sum() < min_mins_per_season:
                    continue
            except:
                print(player_stats_df)
                continue
            squad_stats.append(player_stats_df)

    squad_stats_df = pd.concat(squad_stats)

    #squad_stats_df = squad_stats_df[squad_stats_df.matchday.map(lambda x: 'group' not in x.lower())]
    #serie_a_squad_stats = squad_stats_df[squad_stats_df.for_team.map(lambda x: "Juventus FC" == x)]
    #serie_a_squad_stats.to_csv('juve_stats.csv', index=False)

    serie_a_squad_stats = squad_stats_df

    n_players = serie_a_squad_stats.href.nunique()
    days_of_injuries = len(injuried_games(squad_stats_df))
    print("n players", n_players)
    print("n days of muscular injuries", days_of_injuries)
    print('proportion day injuries/ n players', days_of_injuries/n_players)
    return n_players, days_of_injuries

