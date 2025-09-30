import json
import csv
from time import time
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

MJS_DANIEL_MYSTERY_TOKEN=os.getenv('MJS_SECRET')
CSV_OUTPUT_DIR=os.getenv('CSV_OUTPUT_DIR', 'output')
MJS_UID = os.getenv("MJS_UID")
CONTEST_ID = "31334372"
SEASON_ID = os.getenv('MJS_SEASON_ID', 1)
BASE_URL = "https://engs.mahjongsoul.com/api/contest_gate/api"

if not MJS_DANIEL_MYSTERY_TOKEN:
    raise ValueError("No Token Provided")

# Step 1: Exchange initial token for accessToken
login_url = 'https://passport.mahjongsoul.com/user/login'
login_payload = {
    "uid": MJS_UID,
    "token": MJS_DANIEL_MYSTERY_TOKEN,
    "deviceId": f"web|{MJS_UID}"
}
login_headers = {
    'accept': 'application/json, text/plain, */*',
    'content-type': 'application/json;charset=UTF-8',
    'origin': 'https://mahjongsoul.tournament.yo-star.com'
}

response1 = requests.post(login_url, headers=login_headers, json=login_payload)
print(f"Login response status: {response1.status_code}")
response_data = response1.json()
response1.raise_for_status()  # Raises error if the request failed
access_token = response_data.get('accessToken')

if not access_token:
    raise ValueError("Failed to retrieve access token.")

# Step 2: Exchange accessToken for auth token
auth_url = f'{BASE_URL}/login?method=oauth2'
auth_headers = {
    'accept': 'application/json, text/plain, */*',
    'content-type': 'application/json',
    'origin': 'https://mahjongsoul.tournament.yo-star.com'
}
auth_payload = {
    "type": 8,
    "code": access_token,
    "uid": int(MJS_UID)
}

response2 = requests.post(auth_url, headers=auth_headers, json=auth_payload)
response2.raise_for_status()
auth_token = response2.json().get('data', {}).get('token')

if not auth_token:
    raise ValueError("Failed to retrieve auth token.")

# Creates a dictionary of team name to a list of players

teams = {}
team_names = []

with open('teams.csv', 'r', encoding='utf-8') as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        team_name = row['Team Name']
        team_names.append(team_name)
        team = [row.get(col, '').strip() for col in ['p1', 'p2', 'p3', 'p4'] if row.get(col, '') and row.get(col, '').strip()]
        teams[team_name] = team

contest_headers = {
    'accept': 'application/json, text/plain, */*',
    'authorization': f'Majsoul {auth_token}',
    'origin': 'https://mahjongsoul.tournament.yo-star.com'
}


# Takes a tuple of team indexes and returns a list of player ids if all players are in the waiting room. Otherwise, returns an empty list.
def get_waiting_players(team_indexes):

    #fetch waiting room
    WAIT_URL = f"{BASE_URL}/contest/ready_player_list"
    params = {
        "unique_id": CONTEST_ID,  
        "season_id": SEASON_ID,
    }
    response = requests.get(WAIT_URL, headers=contest_headers, params=params)
    response.raise_for_status()
    
    waiting_data = response.json()["data"]

    players = []
    for t in team_indexes:
        #check if there is a player in that team in waiting_data
        team_name = team_names[t]
        player = [p['account_id'] for p in waiting_data if p['nickname'] in teams[team_name]]
        if len(player) > 0:
            players.append(player[0])
        else:
            print(f"No players from team {team_name} ({teams[team_name]}) are in the waiting room.")

    return players

def start_match(players):
    
    START_URL = f"{BASE_URL}/contest/create_game_plan"
    start_payload = {
        "account_list": players,
        "ai_level": 2, #idk whether to include this if no ai's present.
        "game_start_time": int(time()),
        "init_points": [25000, 25000, 25000, 25000],
        "remark": "",
        "season_id": SEASON_ID,
        "shuffle_seats": False,
        "unique_id": CONTEST_ID,
    }
    response = requests.post(START_URL, headers=contest_headers, json=start_payload)
    response.raise_for_status()
    match_data = response.json()
    print(f"Match response: {match_data}")
    return match_data

def match(team_indexes):
    players = get_waiting_players(team_indexes)

    if (len(players) < 4):
        print("Not enough players to start a match.")
        return None
    
    match_data = start_match(players)
    print(match_data)


def fetch_contest_game_records():

    contest_url = f"{BASE_URL}/contest/fetch_contest_game_records"
    params = {
        "unique_id": CONTEST_ID,  # Replace with your actual contest ID
        "season_id": SEASON_ID,
        "offset": 0,
        "limit": 1000
    }

    response3 = requests.get(contest_url, headers=contest_headers, params=params)
    response3.raise_for_status()

    # Final JSON result saved as dictionary
    contest_data = response3.json()["data"]["record_list"]

    os.makedirs(CSV_OUTPUT_DIR, exist_ok=True)
    # Output CSV filename
    csv_file = f"{CSV_OUTPUT_DIR}/results_season_{SEASON_ID}.csv"

    # Define CSV column headers
    headers = [
        "start_time", "end_time", "tag",
        "player1_nickname", "player1_part_point", "player1_total_point",
        "player2_nickname", "player2_part_point", "player2_total_point",
        "player3_nickname", "player3_part_point", "player3_total_point",
        "player4_nickname", "player4_part_point", "player4_total_point"
    ]

    with open(csv_file, mode='w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        for game in contest_data:
            row = [
                game['start_time'],
                game['end_time'],
                game['tag']
            ]

            # Create a dict of players by seat for quick lookup
            player_data = {p['seat']: p for p in game['result']['players']}
            nickname_data = {a['seat']: a['nickname'] for a in game['accounts']}

            # Append data for seats 0 through 3
            for seat in range(4):
                nickname = nickname_data.get(seat, "")
                part_point = player_data.get(seat, {}).get('part_point_1', "")
                total_point = player_data.get(seat, {}).get('total_point', "")
                row.extend([nickname, part_point, total_point])

            writer.writerow(row)

    print(f"Data exported to {csv_file}")

# EXAMPLES:

# Start a match with the first four teams
# match((0,1,2,3))

# Start a match with specific player ids (0 for AI)
# start_match([122031318,0,0,0])