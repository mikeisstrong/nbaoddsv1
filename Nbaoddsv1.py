# importing necessary libraries
from bs4 import BeautifulSoup
import requests
import time
from datetime import datetime
import csv

def scrape_nba_odds():
    url = 'https://www.vegasinsider.com/nba/odds/las-vegas/'  # Replace with the actual URL
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    odds_table = soup.find('table', {'class': 'frodds-data-tbl'})  # Adjust based on actual HTML structure

    if not odds_table:
        print("Odds table not found")
        return

    rows = odds_table.find_all('tr')

    extracted_data = []
    for row in rows:
        columns = row.find_all('td')
        row_data = [col.text.strip() for col in columns]
        extracted_data.append(row_data)

    filename = f'nba_odds_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv'
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(extracted_data)

    print(f"Scraped data saved to {filename}")

if __name__ == "__main__":
    while True:
        print(f"Starting NBA odds scraping at {datetime.now()}")
        scrape_nba_odds()
        print(f"Completed scraping. Next scrape will occur in 4 hours.")
        time.sleep(4 * 60 * 60)
