import requests
import json
from datetime import datetime
import os

# Configuration
API_KEY = '4f5345425cd0ffb09934ed42ed3c798d'  # Replace with your actual API key
BASE_URL = 'https://api.the-odds-api.com/v4'
REGIONS = ['au', 'uk', 'us'] 
MARKETS = ['h2h']  # Get only moneyline odds (h2h)

# List of sports to analyze
SPORTS_TO_ANALYZE = [
    'basketball_nba'
]

# List of sportsbooks to consider
TARGET_BOOKMAKERS = ['888sport', 'BetMGM', 'Betway', 'DraftKings', 'FanDuel', 'LeoVegas', 'PointsBet']

# Function to calculate implied probability
def implied_probability(odds):
    """Calculates the implied probability from decimal odds."""
    try:
        return 1 / float(odds)
    except (TypeError, ValueError):
        return 0

# Function to check for arbitrage opportunities within an event and collect data
def process_event(event):
    """Processes an event and returns a dictionary with odds information."""
    all_odds = {}

    for bookmaker in event.get('bookmakers', []):
        if bookmaker['title'] in TARGET_BOOKMAKERS:
            for market in bookmaker.get('markets', []):
                if market['key'] == 'h2h':
                    for outcome in market.get('outcomes', []):
                        all_odds[f"{outcome['name']}-{bookmaker['title']}"] = outcome['price']

    if not all_odds:
        return None

    home_team_odds = {k: v for k, v in all_odds.items() if event['home_team'] in k}
    away_team_odds = {k: v for k, v in all_odds.items() if event['away_team'] in k}

    if home_team_odds and away_team_odds:
        min_home_odds = min(home_team_odds.values())
        min_home_bookmaker = min(home_team_odds, key=home_team_odds.get).split('-')[1]
        max_home_odds = max(home_team_odds.values())
        max_home_bookmaker = max(home_team_odds, key=home_team_odds.get).split('-')[1]

        min_away_odds = min(away_team_odds.values())
        min_away_bookmaker = min(away_team_odds, key=away_team_odds.get).split('-')[1]
        max_away_odds = max(away_team_odds.values())
        max_away_bookmaker = max(away_team_odds, key=away_team_odds.get).split('-')[1]

        total_implied_probability = implied_probability(min_home_odds) + implied_probability(min_away_odds)

        avg_home_odds = sum(home_team_odds.values()) / len(home_team_odds)
        avg_away_odds = sum(away_team_odds.values()) / len(away_team_odds)
        avg_home_implied = implied_probability(avg_home_odds)
        avg_away_implied = implied_probability(avg_away_odds)

        return {
            "home_team": event['home_team'],
            "away_team": event['away_team'],
            "best_home_odds": {
                "odds": min_home_odds,
                "implied_percentage": implied_probability(min_home_odds),
                "bookmaker": min_home_bookmaker
            },
            "worst_home_odds": {
                "odds": max_home_odds,
                "implied_percentage": implied_probability(max_home_odds),
                "bookmaker": max_home_bookmaker
            },
            "best_away_odds": {
                "odds": min_away_odds,
                "implied_percentage": implied_probability(min_away_odds),
                "bookmaker": min_away_bookmaker
            },
            "worst_away_odds": {
                "odds": max_away_odds,
                "implied_percentage": implied_probability(max_away_odds),
                "bookmaker": max_away_bookmaker
            },
            "average_home_odds": {
                "odds": avg_home_odds,
                "implied_percentage": avg_home_implied
            },
            "average_away_odds": {
                "odds": avg_away_odds,
                "implied_percentage": avg_away_implied
            },
            "arbitrage_opportunity": total_implied_probability < 1,
            "total_implied_probability": total_implied_probability
        }
    return None

# Save results to JSON file
def save_to_json(data, filename="odds_output.json"):
    """Saves the collected data to a JSON file."""
    output_path = os.path.join(os.getcwd(), filename)  # Save in the current working directory
    try:
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Data successfully saved to {output_path}")
    except IOError as e:
        print(f"Error saving data to {output_path}: {e}")

# Fetch the list of sports
def get_sports():
    url = f"{BASE_URL}/sports?apiKey={API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching sports: {e}")
        return None

# Fetch odds for a specific sport
def get_odds(sport_key):
    url = f"{BASE_URL}/sports/{sport_key}/odds"
    params = {
        'apiKey': API_KEY,
        'regions': ','.join(REGIONS),
        'markets': ','.join(MARKETS),
        'oddsFormat': 'decimal',
        'dateFormat': 'iso'
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json() if response.status_code == 200 else []
    except requests.exceptions.RequestException as e:
        print(f"Error fetching odds for {sport_key}: {e}")
        return []

# Main script
if __name__ == "__main__":
    print("Fetching sports...")
    sports = get_sports()
    
    if sports:
        results = []
        for sport in SPORTS_TO_ANALYZE:
            print(f"Fetching odds for sport: {sport}")
            odds = get_odds(sport)
            if odds:
                for event in odds:
                    try:
                        processed_event = process_event(event)
                        if processed_event:
                            results.append(processed_event)
                    except Exception as e:
                        print(f"Error processing event: {e}")
            else:
                print(f"No odds found for {sport}.")

        # Save results to a JSON file
        save_to_json(results)
