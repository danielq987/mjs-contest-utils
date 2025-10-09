import random
import itertools
from collections import Counter, defaultdict
import pandas as pd

random.seed(2)

# Constants
NUM_PLAYERS = 11
GAMES_PER_WEEK = 11
WEEKS = 6
GAMES_PER_PLAYER_PER_WEEK = 4
PLAYERS_PER_GAME = 4
SEATS = ["east seat", "south seat", "west seat", "north seat"]

# Player list
players = list(range(1, NUM_PLAYERS + 1))

# Track total pairings
pairings = Counter()

# Track seat usage per player
seat_counts = {player: {seat: 0 for seat in SEATS} for player in players}

# Store final matches
matches = []

match_id = 1

# Helper to get all 2-player combinations from a group
def get_pairings(group):
    return list(itertools.combinations(sorted(group), 2))

# Assign seats to 4 players in a balanced way
def assign_balanced_seats(group):
    best_perm = None
    best_score = float("inf")
    
    for perm in itertools.permutations(group):
        score = sum(seat_counts[player][seat] for player, seat in zip(perm, SEATS))
        if score < best_score:
            best_score = score
            best_perm = perm
    
    # Update seat counts
    for player, seat in zip(best_perm, SEATS):
        seat_counts[player][seat] += 1
    
    return best_perm

# Generate matches week by week
for week in range(1, WEEKS + 1):
    weekly_matches = []
    player_game_counts = Counter()
    
    attempts = 0
    while len(weekly_matches) < GAMES_PER_WEEK:
        attempts += 1
        if attempts > 10000:
            raise Exception("Stuck in loop. Possibly over-constrained.")
        
        # Eligible players (less than 4 games this week)
        eligible_players = [p for p in players if player_game_counts[p] < GAMES_PER_PLAYER_PER_WEEK]
        if len(eligible_players) < PLAYERS_PER_GAME:
            continue

        group = random.sample(eligible_players, PLAYERS_PER_GAME)
        group_pairings = get_pairings(group)
        score = sum(pairings[pair] for pair in group_pairings)

        # Try several groupings and pick best one
        best_group = group
        best_score = score
        for _ in range(20):
            candidate_group = random.sample(eligible_players, PLAYERS_PER_GAME)
            candidate_score = sum(pairings[pair] for pair in get_pairings(candidate_group))
            if candidate_score < best_score:
                best_score = candidate_score
                best_group = candidate_group

        # Assign seats in balanced way
        east, south, west, north = assign_balanced_seats(best_group)

        # Update player game counts and pairings
        for p in [east, south, west, north]:
            player_game_counts[p] += 1
        for pair in get_pairings([east, south, west, north]):
            pairings[pair] += 1

        # Save match
        weekly_matches.append({
            "match_id": match_id,
            "week": week,
            "east seat": east,
            "south seat": south,
            "west seat": west,
            "north seat": north
        })
        match_id += 1

    matches.extend(weekly_matches)

# Create DataFrame and save to CSV
df = pd.DataFrame(matches)
df.to_csv("mahjong_schedule_balanced_seats.csv", index=False)
print("Schedule saved to mahjong_schedule_balanced_seats.csv")

