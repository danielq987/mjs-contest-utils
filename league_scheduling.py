from itertools import combinations, permutations
import random
from collections import defaultdict, Counter
import numpy as np
import csv
import math

# Configuration
NUM_PLAYERS = 8
PLAYERS = list(range(NUM_PLAYERS))
MAX_SIMUL_GAMES = NUM_PLAYERS // 4
SIMUL_PLAYERS = MAX_SIMUL_GAMES * 4

# Rounds are sets of games played simultaneously.
# We don't need to seperate into weeks.
ROUNDS = 24

#Only for saving schedule to CSV
ROUNDS_PER_WEEK = 4

# Check if it is possible each player will play an equal number of games
# Warns if not possible
TOTAL_SPOTS = ROUNDS * SIMUL_PLAYERS
if TOTAL_SPOTS % NUM_PLAYERS != 0:
    print("Warning: Not all players can play an equal number of games.")
    games_per_player = TOTAL_SPOTS // NUM_PLAYERS
    
    # Find closest rounds that work
    # Using math/gcd: valid rounds r are multiples of L = NUM_PLAYERS / gcd(NUM_PLAYERS, SIMUL_PLAYERS)
    L = NUM_PLAYERS // math.gcd(NUM_PLAYERS, SIMUL_PLAYERS)
    rounds_lower = (ROUNDS // L) * L
    rounds_higher = ((ROUNDS + L - 1) // L) * L
    
    print(f"Current rounds: {ROUNDS}, games per player: {games_per_player}")
    print(f"Closest lower rounds: {rounds_lower} (games per player: {(rounds_lower * SIMUL_PLAYERS) // NUM_PLAYERS})")
    print(f"Closest higher rounds: {rounds_higher} (games per player: {(rounds_higher * SIMUL_PLAYERS) // NUM_PLAYERS})")

# grouping_cost = sum of all pair_counts for pairs in the group
def grouping_cost(grouping, pair_counts):
    return sum(pair_counts[(a, b)] for game in grouping for a, b in combinations(game, 2))

# seating_cost = sum of seat_counts for each player in their seat
def seating_cost(game, seat_counts):
    return sum(seat_counts[game[i]][i] for i in range(4))

def add_round(games_played: Counter, pair_counts: Counter, seat_counts: defaultdict) -> None:
    # First chooses the SIMUL_PLAYERS players with the least games_played.

    least_played = games_played.most_common()[::-1]

    maximum = least_played[SIMUL_PLAYERS-1][1]

    # Guaranteed if games played < maximum, can pick if == maximum
    guaranteed, possible = [], []
    for p, count in least_played:
        if count < maximum:
            guaranteed.append(p)
        elif count == maximum:
            possible.append(p)
    random.shuffle(possible)

    selected = guaranteed + possible[:SIMUL_PLAYERS - len(guaranteed)]
    random.shuffle(selected)

    ### I used to simulate every permutation, but that grows fast so I asked GPT and it gave this answer
    # I have no idea what's going on tbh

    # Partition selected players into groups of 4 minimizing sum of pair_counts within groups
    # Exact DP over subsets: O(2^n * n^3), fine for n=12
    n = len(selected)
    idx_of = {p: i for i, p in enumerate(selected)}
    players_by_idx = selected

    # Precompute cost of each 4-set (by indices) once per round
    def quad_cost_of_players(ps):
        # sum of 6 pair costs
        a,b,c,d = ps
        pc = pair_counts
        return (pc[(min(a,b), max(a,b))] + pc[(min(a,c), max(a,c))] + pc[(min(a,d), max(a,d))] +
                pc[(min(b,c), max(b,c))] + pc[(min(b,d), max(b,d))] + pc[(min(c,d), max(c,d))])

    quad_cost_map = {}
    for quad in combinations(range(n), 4):  # (i,a,b,c) indices, already sorted
        ps = tuple(players_by_idx[i] for i in quad)
        quad_cost_map[quad] = quad_cost_of_players(ps)

    def quad_cost(idxs):
        # idxs is a sorted 4-tuple (i,a,b,c)
        return quad_cost_map[idxs]

    from math import inf
    full_mask = (1 << n) - 1
    dp = [inf] * (1 << n)
    parent = [None] * (1 << n)  # stores (prev_mask, quad_indices_tuple)
    dp[0] = 0

    for mask in range(1 << n):
        if dp[mask] == inf:
            continue
        # pick first unused index to anchor combinations
        try:
            i = next(k for k in range(n) if not (mask >> k) & 1)
        except StopIteration:
            continue  # mask is full
        rest = [j for j in range(i + 1, n) if not (mask >> j) & 1]
        for a, b, c in combinations(rest, 3):
            quad = (i, a, b, c)
            new_mask = mask | (1 << i) | (1 << a) | (1 << b) | (1 << c)
            cost = dp[mask] + quad_cost(quad)
            if cost < dp[new_mask]:
                dp[new_mask] = cost
                parent[new_mask] = (mask, quad)

    # Reconstruct best grouping of indices, then map to player IDs
    grouping_indices = []
    cur = full_mask
    while cur and parent[cur] is not None:
        prev, quad = parent[cur]
        grouping_indices.append(tuple(players_by_idx[i] for i in quad))
        cur = prev
    best_grouping = list(reversed(grouping_indices))  # list of 3 tuples (each len 4)

    # Seat each game to balance seat usage
    for i in range(MAX_SIMUL_GAMES):
        game = best_grouping[i]
        best_seating = min(permutations(game), key=lambda g: seating_cost(g, seat_counts))
        best_grouping[i] = best_seating  # tuple of 4 players in seat order

    # Update counts
    for game in best_grouping:
        for p in game:
            games_played[p] += 1
        for a, b in combinations(game, 2):
            k = (a, b) if a < b else (b, a)
            pair_counts[k] += 1
        for seat in range(4):
            seat_counts[game[seat]][seat] += 1

    return best_grouping

def create_schedule():


    games_played = Counter({s: 0 for s in PLAYERS})
    pair_counts = Counter({(p1, p2): 0 for p1 in PLAYERS for p2 in PLAYERS if p1 < p2})
    seat_counts = defaultdict(lambda: Counter({i: 0 for i in range(4)}))  # seat_counts[player][seat] = count

    # Schedule is a list of rounds, each round contains MAX_SIMUL_GAMES lists of 4 numbers.
    # [[[1,2,3,4],[5,6,7,8]],[[1,3,5,7],[2,4,6,8]],...]
    schedule = []

    for i in range(ROUNDS):
        print(i)
        schedule.append(add_round(games_played, pair_counts, seat_counts))

    
    print("Best schedule analysis:")
    print(f"Standard deviation of matchup distribution: {np.std(list(pair_counts.values())):.4f}")
    print(f"Highest matchup count: {max(pair_counts.values())}")
    print(f"Lowest matchup count: {min(pair_counts.values())}")
    overall_seat_counts = [seat_counts[p][s] for p in PLAYERS for s in range(4)]
    print(f"Standard deviation of seat distribution (overall): {np.std(overall_seat_counts):.4f}")
    print(f"Highest seat count: {max(overall_seat_counts)}")
    print(f"Lowest seat count: {min(overall_seat_counts)}")

    return schedule

def save_schedule_to_csv(schedule, filename="schedule.csv"):
    headers = ["week", "round_in_week", "global_round", "game", "seat_0", "seat_1", "seat_2", "seat_3"]
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for r_idx, round_games in enumerate(schedule):
            week = (r_idx // ROUNDS_PER_WEEK) + 1
            round_in_week = (r_idx % ROUNDS_PER_WEEK) + 1
            global_round = r_idx + 1
            for g_idx, game in enumerate(round_games, start=1):
                seats = list(game)  # (p0, p1, p2, p3)
                writer.writerow([week, round_in_week, global_round, g_idx, *seats])
    

schedule = create_schedule()
save_schedule_to_csv(schedule)

