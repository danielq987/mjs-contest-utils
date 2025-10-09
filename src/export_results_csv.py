import csv
import os
from utils.api import fetch_results_csv
from utils.helpers import get_env, is_running_in_github_actions

def export_results_csv():
    # Writes results to a CSV file. Used by GitHub Action.
    contest_data = fetch_results_csv(verbose=is_running_in_github_actions())
    
    csv_output_dir = get_env('CSV_OUTPUT_DIR', 'output')
    mjs_season_id = get_env('MJS_SEASON_ID', 1)

    if not os.path.exists(csv_output_dir):
        os.mkdir(csv_output_dir)

    # Output CSV filename
    csv_file = f"{csv_output_dir}/results_season_{mjs_season_id}.csv"

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

if __name__ == "__main__":
    export_results_csv()