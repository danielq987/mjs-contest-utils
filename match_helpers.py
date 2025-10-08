from time import time
import requests
import os
import auth
import read_csv

teams, team_names = read_csv.get_teams()
if not teams: raise ValueError("No teams found in CSV.")

schedule = read_csv.get_schedule()
if not schedule: raise ValueError("No schedule found in CSV.")

#Checks whether schedule is valid (team indexes in range)
for round_games in schedule:
    for game in round_games:
        for t in game:
            if t <= 0 or t > len(team_names):
                raise ValueError(f"Invalid team index {t} in schedule.")

MJS_DANIEL_MYSTERY_TOKEN=os.getenv('MJS_SECRET')
CSV_OUTPUT_DIR=os.getenv('CSV_OUTPUT_DIR', 'output')
MJS_UID = "42474300"
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
    print(team_indexes)
    for t in team_indexes:
        #check if there is a player in that team in waiting_data
        team_name = team_names[t - 1]
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

    # Dry-run mode for CI
    if str(os.getenv("DRY_RUN", "")).lower() in ("1", "true", "yes"):
        print("[DRY_RUN] Would create game plan:", start_payload)
        return {"dry_run": True, "payload": start_payload}

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


# Starts only one match
def start_match_index(round_index,match_index):
    if match_index < 0 or match_index >= len(schedule):
        print("Match index out of range.")
        return

    round_games = schedule[round_index - 1]
    print(f"Starting match {match_index} for round {round_index}.")

    team_indexes = round_games[match_index - 1]
    print(f"Attempting to start match for teams: {[team_names[i - 1] for i in team_indexes]}")
    match(team_indexes)

# DOES NOT WORK WITH CURRENT SCHEDULE FORMAT - INDIVIDUALLY RUN MATCHES USING START_MATCH_INDEX
"""def start_scheduled_matches(schedule_index):
    if schedule_index >= len(schedule):
        print("Schedule index out of range.")
        return schedule_index

    round_games = schedule[schedule_index]
    print(f"Starting matches for round {schedule_index + 1} with {len(round_games)} games.")

    for game in round_games:
        team_indexes = game  # tuple of 4 team indexes
        print(f"Attempting to start match for teams: {[team_names[i - 1] for i in team_indexes]}")
        match(team_indexes)

    return schedule_index + 1"""

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Mahjong Soul contest matchmaking")
    sub = parser.add_subparsers(dest="cmd", required=True)

    #p_round = sub.add_parser("start-round", help="Start all matches for a schedule round (0-based index)")
    #p_round.add_argument("index", type=int)

    p_round_match = sub.add_parser("start-match-index", help="Start a single match from schedule round and match index (1-based)")
    p_round_match.add_argument("round_index", type=int, help="Round index (1-based)")
    p_round_match.add_argument("match_index", type=int, help="Match index (1-based)")

    p_match = sub.add_parser("start-match", help="Start a single match from 4 team indexes")
    p_match.add_argument("teams", nargs=4, type=int, help="Four team indexes (1-based)")

    p_wait = sub.add_parser("wait", help="Show waiting players for given team indexes")
    p_wait.add_argument("teams", nargs="+", type=int)

    args = parser.parse_args()

    #if args.cmd == "start-round":
        #start_scheduled_matches(args.index)
    if args.cmd == "start-match-index":
        start_match_index(args.round_index, args.match_index)
    elif args.cmd == "start-match":
        match(tuple(args.teams))
    elif args.cmd == "wait":
        players = get_waiting_players(tuple(args.teams))
        print({"teams": [team_names[i - 1] for i in args.teams], "players": players})