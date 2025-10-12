import csv
import schedule
from time import time, sleep
from utils.api import start_match, get_waiting_players

teams_global = []

def read_matches(file_path="matches.csv"):
    """
    Reads matches from csv file and returns an array of dictionaries.
    """
    matches = {}

    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            matches[row["match_id"]] = ({**row, "started": False})

    return matches

def write_matches(matches, file_path="matches.csv"):
    """
    
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
    print(teams_dict)
    return teams_dict

def attempt_start_match(match, teams, fail_on_error=True):
    starting_player_ids = []
    waiting_players = get_waiting_players()
    for team_key in [match["team1"], match["team2"], match["team3"], match["team4"]]:
        team_name = teams[team_key]["team_name"]
        ready_players_on_team = [player for player in waiting_players if player["team_name"] == team_name]
        if len(ready_players_on_team) != 1:
            print(f"Error: Team {team_name} has {len(ready_players_on_team)} players ready. Expected: 1")
            return False
        else:
            print(f"✅Team {team_name} has {ready_players_on_team[0]['nickname']} ready")
            starting_player_ids.append(ready_players_on_team[0]["account_id"])
    
    if len(starting_player_ids) != 4:
        print(f"Error: There should be 4 players ready. Ready: {starting_player_ids}")
        return False

    try:
        start_match(match["match_id"], starting_player_ids)
        return True
    except Exception as e:
        print("Error starting game") 
        print(e) 
        return False

def processMatches(matches, teams):
    # current_timestamp = time()
    current_timestamp = 1760317200 
    def is_time_startable(match_timestamp):
        """
        Check whether the current time is between the start time and 15 minutes from now
        """
        return current_timestamp >= match_timestamp and current_timestamp <= match_timestamp + 15 * 60

    startable_matches = [v for k, v in matches.items() if is_time_startable(int(v["timestamp"])) and v["is_started"] == "0"]
    
    print(startable_matches)
    
    for match in startable_matches:
        is_successful_start = attempt_start_match(match, teams)
        if is_successful_start:
            match["is_started"] = 1
            write_matches(matches, "matches-db.csv")

def main():
    matches = read_matches()
    global teams_global
    teams_global = parse_team_csv_to_dict()
    schedule.every(1).minutes.do(processMatches, matches=matches)
    while True:
        schedule.run_pending()
        sleep(1)
    
if __name__ == "__main__":
    main()