import requests
import json

try:
    print("Fetching data from http://localhost:5002/api/players...")
    response = requests.get('http://localhost:5002/api/players')
    
    if response.status_code == 200:
        data = response.json()
        players = data.get('players', [])
        print(f"Successfully fetched {len(players)} players.")
        
        # Find Virat Kohli
        kohli = next((p for p in players if 'Kohli' in p['player_name']), None)
        if kohli:
            print("\n--- LIVE API DATA FOR VIRAT KOHLI ---")
            print(f"Name: {kohli['player_name']}")
            print(f"Role: {kohli['player_role']}")  # This is what the frontend sees
            print(f"Bat Avg: {kohli['batting_avg']}")
            print(f"Bowl Econ: {kohli['bowling_economy']}")
        else:
            print("Virat Kohli not found in API response!")
            
        # Find Bumrah
        bumrah = next((p for p in players if 'Bumrah' in p['player_name']), None)
        if bumrah:
            print("\n--- LIVE API DATA FOR JASPRIT BUMRAH ---")
            print(f"Name: {bumrah['player_name']}")
            print(f"Role: {bumrah['player_role']}")
            print(f"Bat Avg: {bumrah['batting_avg']}")
            print(f"Bowl Econ: {bumrah['bowling_economy']}")
            
    else:
        print(f"Error: API returned status code {response.status_code}")

except Exception as e:
    print(f"Connection failed: {e}")
