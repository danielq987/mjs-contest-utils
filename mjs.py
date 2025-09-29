import json
import csv
import requests
import json
import os

MJS_DANIEL_MYSTERY_TOKEN=os.getenv('MJS_SECRET')
CSV_OUTPUT_DIR=os.getenv('CSV_OUTPUT_DIR', 'output')
MJS_UID = "42474300"
CONTEST_ID = "31334372"
SEASON_ID = os.getenv('MJS_SEASON_ID', 1)

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
response1.raise_for_status()  # Raises error if the request failed
access_token = response1.json().get('accessToken')

if not access_token:
    raise ValueError("Failed to retrieve access token.")

# Step 2: Exchange accessToken for auth token
auth_url = 'https://engs.mahjongsoul.com/api/contest_gate/api/login?method=oauth2'
auth_payload = {
    "type": 8,
    "code": access_token,
    "uid": int(MJS_UID)
}
auth_headers = {
    'accept': 'application/json, text/plain, */*',
    'content-type': 'application/json',
    'origin': 'https://mahjongsoul.tournament.yo-star.com'
}

response2 = requests.post(auth_url, headers=auth_headers, json=auth_payload)
response2.raise_for_status()
auth_token = response2.json().get('data', {}).get('token')

if not auth_token:
    raise ValueError("Failed to retrieve auth token.")

# Step 3: Fetch contest game records
contest_url = (
    "https://engs.mahjongsoul.com/api/contest_gate/api/contest/fetch_contest_game_records"
)
params = {
    "unique_id": CONTEST_ID,  # Replace with your actual contest ID
    "season_id": SEASON_ID,
    "offset": 0,
    "limit": 1000
}
contest_headers = {
    'accept': 'application/json, text/plain, */*',
    'authorization': f'Majsoul {auth_token}',
    'origin': 'https://mahjongsoul.tournament.yo-star.com'
}

response3 = requests.get(contest_url, headers=contest_headers, params=params)
response3.raise_for_status()

# Final JSON result saved as dictionary
contest_data = response3.json()["data"]["record_list"]

os.mkdir(CSV_OUTPUT_DIR)
# Output CSV filename
csv_file = f"${CSV_OUTPUT_DIR}/results_season_{SEASON_ID}.csv"

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

