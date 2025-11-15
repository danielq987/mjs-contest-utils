import csv
import schedule
import os
from time import time, sleep
from utils.api import start_match, get_waiting_players
from utils.auth import get_auth_token

def read_matches(file_path="matches.csv"):
    """
    Reads matches from csv file and returns a dictionary of matches.

    Return example:
    {
        1: {
            match_id: "1",
            week: "1",
            team1: "1",
            team2: "2",
            team3: "3",
            team4: "4",
            timestamp: 1760140800,
            is_started: 0
        },
        ...
    }
    """
    matches = {}

    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            matches[row["match_id"]] = ({**row, "started": False})
            matches[row["match_id"]]["timestamp"] = int(row["timestamp"])

    return matches

def write_matches(matches, file_path="matches.csv"):
    """
    Writes the matches to filepath specified. Should be run if the matches file is ever updated.
    """
    fieldnames = list(matches.values())[0].keys()
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(list(matches.values()))  

    return None

def parse_team_csv_to_dict(csv_file="teams.csv"):
    """
    Read teams.csv and format as
    {
        1: {
            team_name: "Itsumodo", # Team name on sheet
            team_id: "Itsumodo", # Team ID on MJS tournament page
        },
        ...
    }
    """
    teams_dict = {}

    # Open and read the CSV file
    with open(csv_file, newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) >= 3:
                key = row[0].strip()
                team_name_sheet = row[1].strip()
                team_name = row[2].strip()
                teams_dict[key] = {"team_name_sheet": team_name_sheet, "team_name": team_name}

    # Print the resulting dictionary
    return teams_dict

def attempt_start_match(match, teams):
    """
    Attempts to start the match specified by the parameter.

    Checks if 1 player from each team is ready. Game should be startable between 30 seconds before the scheduled time and 15 minutes past the scheduled time. If not in the scheduled time, simply print the ready players for each team.

    e.g. if the game is scheduled for 9:00:00 PM, game should be startable between 8:59:30 PM and 9:15:00 PM.

    teams is a dictionary specifying all the teams.
    """
    starting_player_ids = []
    waiting_players = get_waiting_players()
    is_every_team_ready = True
    for team_key in [match["team1"], match["team2"], match["team3"], match["team4"]]:
        team_name = teams[team_key]["team_name"]
        ready_players_on_team = [player for player in waiting_players if player["team_name"] == team_name]
        if len(ready_players_on_team) != 1:
            print(f"Error: Team {team_name} has {len(ready_players_on_team)} players ready. Expected: 1")
            is_every_team_ready = False
        else:
            print(f"✅Team {team_name} has {ready_players_on_team[0]['nickname']} ready")
            starting_player_ids.append(ready_players_on_team[0]["account_id"])
    
    if len(starting_player_ids) != 4 or not is_every_team_ready:
        print(f"Error: There should be 4 players ready. Ready: {starting_player_ids}")
        return False
    
    if (time() >= match["timestamp"] - 30):
        try:
            start_match(match["match_id"], starting_player_ids)
            return True
        except Exception as e:
            print("Error starting game") 
            print(e) 
            return False

    return False 

def processMatches(matches, teams):
    """
    Given the list of all matches, find all matches which are near the current time. Then, try to start them. 

    If a match was successfully started, write the matches dictionary to a new csv file with the "is_started" field set for that match.
    """
    current_timestamp = time()
    # current_timestamp = 1760317200 
    def is_time_startable(match_timestamp):
        """
        Check whether the current time is between the start time and 15 minutes from now
        """
        return current_timestamp >= match_timestamp - 5 * 60 and current_timestamp <= match_timestamp + 15 * 60

    startable_matches = [v for k, v in matches.items() if is_time_startable(v["timestamp"]) and v["is_started"] == "0"]
    
    print(startable_matches)
    
    for match in startable_matches:
        is_successful_start = attempt_start_match(match, teams)
        if is_successful_start:
            match["is_started"] = 1
            write_matches(matches, "matches-db.csv")

def cache_auth_token():
    """
    Get the mahjong soul auth token and save it to an environment variable for caching.

    If set, every API call will no longer request a new token.
    """
    token = get_auth_token()
    if token:
        os.environ["MJS_TOKEN_CACHE"] = token
    return

def main():
    matches = read_matches()
    teams = parse_team_csv_to_dict()
    cache_auth_token()
    schedule.every(1).hours.do(cache_auth_token)
    schedule.every(20).seconds.do(processMatches, matches=matches, teams=teams)
    while True:
        schedule.run_pending()
        sleep(1)
    
if __name__ == "__main__":
    main()