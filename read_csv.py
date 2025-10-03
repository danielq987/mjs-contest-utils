import csv

def get_teams():
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

    return teams, team_names

def get_schedule(path: str = "schedule.csv"):
    """
    Load schedule as List[List[Tuple[seat0, seat1, seat2, seat3]]].
    Expects headers: week, round_in_week, global_round, game, seat_0..seat_3.
    Orders by global_round then game.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rounds = {}
            for row in reader:
                try:
                    gr = int(row.get("global_round") or row.get("round") or row.get("Global Round") or 0)
                    game_idx = int(row.get("game") or row.get("Game") or 0)
                except ValueError:
                    continue

                seats = []
                for k in ("seat_0", "seat_1", "seat_2", "seat_3"):
                    v = (row.get(k) or "").strip()
                    if v == "":
                        seats.append(None)
                    else:
                        try:
                            seats.append(int(v))
                        except ValueError:
                            seats.append(v)

                rounds.setdefault(gr, []).append((game_idx, tuple(seats)))

        schedule = []
        for gr in sorted(rounds):
            games_sorted = [g for _, g in sorted(rounds[gr], key=lambda x: x[0])]
            schedule.append(games_sorted)
        return schedule
    except FileNotFoundError:
        return []