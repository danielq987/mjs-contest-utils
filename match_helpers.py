import json
import csv
from time import time
import requests
import os
from dotenv import load_dotenv
import auth
import read_csv

# Load environment variables from .env file
load_dotenv()

MJS_DANIEL_MYSTERY_TOKEN=os.getenv('MJS_SECRET')
CSV_OUTPUT_DIR=os.getenv('CSV_OUTPUT_DIR', 'output')
MJS_UID = os.getenv("MJS_UID")
CONTEST_ID = "31334372"
SEASON_ID = os.getenv('MJS_SEASON_ID', 1)



TOKEN = auth.get_auth_token(MJS_DANIEL_MYSTERY_TOKEN, MJS_UID)
if not TOKEN: raise ValueError("Failed to retrieve auth token.")

CONTEST_URL = "https://engs.mahjongsoul.com/api/contest_gate/api"
CONTEST_HEADERS = {
    'accept': 'application/json, text/plain, */*',
    'authorization': f'Majsoul {TOKEN}',
    'origin': 'https://mahjongsoul.tournament.yo-star.com'
}



teams, team_names = read_csv.get_teams()
if not teams: raise ValueError("No teams found in CSV.")

schedule = read_csv.get_schedule()
if not schedule: raise ValueError("No schedule found in CSV.")

# Takes a tuple of team indexes and returns a list of player ids if all players are in the waiting room. Otherwise, returns an empty list.
def get_waiting_players(team_indexes):

    #fetch waiting room
    WAIT_URL = f"{CONTEST_URL}/contest/ready_player_list"
    params = {
        "unique_id": CONTEST_ID,  
        "season_id": SEASON_ID,
    }
    response = requests.get(WAIT_URL, headers=CONTEST_HEADERS, params=params)
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
    
    START_URL = f"{CONTEST_URL}/contest/create_game_plan"
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
    response = requests.post(START_URL, headers=CONTEST_HEADERS, json=start_payload)
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

def start_scheduled_matches(schedule_index):
    if schedule_index >= len(schedule):
        print("Schedule index out of range.")
        return schedule_index

    round_games = schedule[schedule_index]
    print(f"Starting matches for round {schedule_index + 1} with {len(round_games)} games.")

    for game in round_games:
        team_indexes = game  # tuple of 4 team indexes
        print(f"Attempting to start match for teams: {[team_names[i] for i in team_indexes]}")
        match(team_indexes)

    return schedule_index + 1


start_scheduled_matches(0)