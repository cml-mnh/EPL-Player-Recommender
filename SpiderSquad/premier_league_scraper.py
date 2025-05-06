import requests
from bs4 import BeautifulSoup
import pandas as pd
import json

def scrape_premier_league_teams():
    # URL of the Premier League stats page
    url = "https://fbref.com/en/comps/9/Premier-League-Stats"
    
    # Send a GET request to the URL
    response = requests.get(url)
    
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the table with the specified ID
    table = soup.find('table', {'id': 'results2024-202591_overall'})
    
    if not table:
        print("Table not found")
        return
    
    # Initialize a list to store team data
    teams_data = []
    
    # Get all rows from the table body
    rows = table.find_all('tr')[1:]  # Skip header row
    
    for row in rows:
        # Extract data from each cell
        cells = row.find_all(['th', 'td'])
        
        if len(cells) >= 20:  # Ensure we have enough cells
            team_data = {
                'Rank': cells[0].text.strip(),
                'Team': cells[1].text.strip(),
                'Matches Played': cells[2].text.strip(),
                'Wins': cells[3].text.strip(),
                'Draws': cells[4].text.strip(),
                'Losses': cells[5].text.strip(),
                'Goals For': cells[6].text.strip(),
                'Goals Against': cells[7].text.strip(),
                'Goal Difference': cells[8].text.strip(),
                'Points': cells[9].text.strip(),
                'Points/Match': cells[10].text.strip(),
                'xG': cells[11].text.strip(),
                'xGA': cells[12].text.strip(),
                'xGD': cells[13].text.strip(),
                'xGD/90': cells[14].text.strip(),
                'Last 5': cells[15].text.strip(),
                'Attendance': cells[16].text.strip(),
                'Top Team Scorer': cells[17].text.strip(),
                'Goalkeeper': cells[18].text.strip(),
                'Notes': cells[19].text.strip()
            }
            teams_data.append(team_data)
    
    # Convert to DataFrame
    df = pd.DataFrame(teams_data)
    
    # Save to CSV
    df.to_csv('premier_league_teams.csv', index=False)
    
    # Save to JSON
    with open('premier_league_teams.json', 'w', encoding='utf-8') as f:
        json.dump(teams_data, f, ensure_ascii=False, indent=4)
    
    print("Data has been saved to premier_league_teams.csv and premier_league_teams.json")

if __name__ == "__main__":
    scrape_premier_league_teams()