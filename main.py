import requests
from bs4 import BeautifulSoup
import pandas as pd

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'
}

# Initialize empty lists to store player names and values
all_player_names = []
all_player_values = []

base_url = "https://www.transfermarkt.co.uk/premier-league/marktwerte/wettbewerb/GB1/pos//detailpos/0/altersklasse/alle/plus/1"
base_url = "https://www.transfermarkt.co.uk/dusan-vlahovic/leistungsdatendetails/spieler/357498/wettbewerb/IT1/saison/2024"
pageTree = requests.get(base_url, headers=headers)
soup = BeautifulSoup(pageTree.content, 'html.parser')

tables = soup.find_all('table')
print(len(tables))

# Find the table body
tbody = tables[2]

# Loop through each row in the body
for tr in tbody.find_all('tr'):
    tds = tr.find_all('td')
    
    # Ensure there are enough td elements (important for matching the structure)
    if len(tds) >= 13:
        matchday = tds[0].get_text(strip=True)
        date = tds[1].get_text(strip=True)
        venue = tds[2].get_text(strip=True)
        for_team = tds[3].get_text(strip=True)
        opponent_team = tds[5].get_text(strip=True)
        result = tds[6].get_text(strip=True)
        minutes_played = tds[-1].get_text(strip=True)

        print(f"Matchday: {matchday}, Date: {date}, Venue: {venue}, For Team: {for_team}, Opponent: {opponent_team}, Result: {result}, Minutes Played: {minutes_played}")
