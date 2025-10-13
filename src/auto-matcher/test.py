from main import processMatches, read_matches, parse_team_csv_to_dict

def test():
    matches = read_matches()
    teams = parse_team_csv_to_dict()
    processMatches(matches, teams)

if __name__ == "__main__":
    test() 