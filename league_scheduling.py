from itertools import combinations, permutations
import random
from collections import defaultdict, Counter
import numpy as np

random.seed(5)

# Configuration
NUM_PLAYERS = 10
WEEKS = 6
GAMES_PER_PLAYER_PER_WEEK = 4
PLAYERS = list(range(NUM_PLAYERS))
TOTAL_GAMES = NUM_PLAYERS * GAMES_PER_PLAYER_PER_WEEK * WEEKS // 4  # total number of 4-player games

# Week-wise structure
GAMES_PER_WEEK = TOTAL_GAMES // WEEKS  # 10 games per week
ROUNDS_PER_WEEK = GAMES_PER_WEEK // 2  # 2 games per round, 5 rounds

# Seat labels
SEATS = ['East', 'South', 'West', 'North']


def generate_all_possible_groups(players):
    """Generate all possible 4-player combinations."""
    return list(combinations(players, 4))


def assign_seats(game):
    """Assign seats randomly to players in a game."""
    return list(zip(SEATS, random.sample(game, 4)))


def schedule_week(valid_groups, players):
    """
    Schedule one week of Mahjong games while ensuring:
    - Each player plays exactly 4 games.
    - No player plays in two games in the same round (i.e., within the same time slot).
    """
    for _ in range(1000):  # Retry limit
        weekly_games = []
        player_game_count = Counter()
        rounds = [[] for _ in range(ROUNDS_PER_WEEK)]

        # Random shuffle for fairness
        groups = valid_groups[:]
        random.shuffle(groups)

        for group in groups:
            if any(player_game_count[p] >= GAMES_PER_PLAYER_PER_WEEK for p in group):
                continue

            # Try to place the group in a round
            for round_games in rounds:
                if len(round_games) < 2 and all(p not in sum(round_games, ()) for p in group):
                    round_games.append(group)
                    for p in group:
                        player_game_count[p] += 1
                    break

            if sum(len(r) for r in rounds) == GAMES_PER_WEEK:
                # Success
                return rounds

    return None  # Failed to find valid schedule


def schedule_all_weeks():
    all_groups = generate_all_possible_groups(PLAYERS)
    schedule = []

    for week in range(WEEKS):
        weekly_schedule = schedule_week(all_groups, PLAYERS)
        if weekly_schedule is None:
            print(f"Failed to schedule week {week + 1}")
            return None
        schedule.append(weekly_schedule)

    return schedule


def analyze_schedule(schedule):
    matchup_counter = defaultdict(int)
    seat_counter = Counter()

    for week in schedule:
        for round_games in week:
            for game in round_games:
                seated_game = assign_seats(game)
                players = [p for seat, p in seated_game]

                # Count matchups
                for p1, p2 in combinations(players, 2):
                    key = tuple(sorted((p1, p2)))
                    matchup_counter[key] += 1

                # Count seat distribution
                for seat, player in seated_game:
                    seat_counter[(player, seat)] += 1

    return matchup_counter, seat_counter


# Run the scheduler
schedule = schedule_all_weeks()

# If successful, analyze it
if schedule:
    matchup_counter, seat_counter = analyze_schedule(schedule)

    # print(seat_counter)
    for key, value in sorted(matchup_counter.items(), key=lambda item: item[1], reverse=True):
        print(f"{key}: {value}")

    for week in schedule:
        for pairing in week:
            for game in pairing:
                l_game = list(game)
                random.shuffle(l_game)
                print(','.join(str(team) for team in l_game))
else:
    print("failed")
    seat_counter = {}
    
