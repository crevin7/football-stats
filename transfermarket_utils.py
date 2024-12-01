import pandas as pd
from collections import defaultdict

def extract_transfermarket_table(table_body) -> pd.DataFrame:
    table_dict = {
        "matchday": [],
        "date": [],
        "venue": [],
        "for_team": [],
        "opponent_team": [],
        "result": [],
        "minutes_played": [],
        "injury": []
    }
    for tr in table_body.find_all('tr'):
        tds = tr.find_all('td')
        # Ensure there are enough td elements (important for matching the structure)

        if len(tds) >= 9:
            table_dict["matchday"].append(tds[0].get_text(strip=True))
            table_dict["date"].append(tds[1].get_text(strip=True))
            table_dict["venue"].append(tds[2].get_text(strip=True))
            table_dict["for_team"].append(tds[3].find('a')['title'])
            table_dict["opponent_team"].append(tds[5].find('a')['title'])
            table_dict["result"].append(tds[7].get_text(strip=True))
        if len(tds) >= 13:
            table_dict["minutes_played"].append(int(tds[-1].get_text(strip=True)[:-1]))
            table_dict["injury"].append("")
        elif len(tds) == 9:
            table_dict["minutes_played"].append(None)
            table_dict["injury"].append(tds[-1].get_text(strip=True))

    return pd.DataFrame(table_dict)


def injuried_games(player_stats):
    return player_stats[player_stats.injury.map(lambda x: 'injury' in x or 'musc' in x.lower())]

def get_all_players_from_team(soup):
    all_rows = soup.find_all('tr')

    # Filter rows that also have a <td> with class="zentriert rueckennummer bg_Sturm"
    target_rows = []
    href_values = []
    for row in all_rows:

        if row.find('td', class_=['zentriert rueckennummer bg_Sturm', 'zentriert rueckennummer bg_Mittelfeld', 'zentriert rueckennummer bg_Abwehr']): # select the requested classes 
            # goalkeepers: 'zentriert rueckennummer bg_Torwart'
            target_rows.append(row)

    # Print the filtered rows
    for target_row in target_rows:
        a_tag = target_row.find('td', class_='hauptlink').find('a')

        # Extract the href attribute value
        href_values.append(a_tag['href'])
    
    return href_values
            

def is_stats_table(soup):
    expected_entries = [
        {"class": "zentriert", "text": "Matchday"},
        {"class": "zentriert", "text": "Date"},
        {"class": "zentriert", "text": "Venue"},
        {"class": "zentriert", "text": "Result"},
        {"class": "zentriert", "text": "Pos."},
        # Add additional entries based on their structure
    ]


    missing_entries = []
    for entry in expected_entries:
        if not soup.find('th', class_=entry['class'], string=entry['text']):
            missing_entries.append(entry)
    
    return not missing_entries