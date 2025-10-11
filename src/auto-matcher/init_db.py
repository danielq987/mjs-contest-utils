import sqlite3
import csv
import os
import sys

def initialize_db(players_csv, teams_csv, schedule_csv):
    db_name = 'tournament.db'
    
    # Remove the existing database if it exists
    if os.path.exists(db_name):
        os.remove(db_name)

    # Connect to SQLite database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Enable foreign key constraints
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Create tables
    cursor.execute("""
        CREATE TABLE players (
            mjs_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            discord_id TEXT,
            mjs_nickname TEXT
        );
    """)

    cursor.execute("""
        CREATE TABLE teams (
            team_name TEXT PRIMARY KEY,
            player1_id TEXT,
            player2_id TEXT,
            player3_id TEXT,
            player4_id TEXT,
            FOREIGN KEY (player1_id) REFERENCES players (mjs_id),
            FOREIGN KEY (player2_id) REFERENCES players (mjs_id),
            FOREIGN KEY (player3_id) REFERENCES players (mjs_id),
            FOREIGN KEY (player4_id) REFERENCES players (mjs_id)
        );
    """)

    cursor.execute("""
        CREATE TABLE schedule (
            match_id TEXT PRIMARY KEY,
            week_id TEXT NOT NULL,
            team1 TEXT,
            team2 TEXT,
            team3 TEXT,
            team4 TEXT,
            start_time TEXT,
            FOREIGN KEY (team1) REFERENCES teams (team_name),
            FOREIGN KEY (team2) REFERENCES teams (team_name),
            FOREIGN KEY (team3) REFERENCES teams (team_name),
            FOREIGN KEY (team4) REFERENCES teams (team_name)
        );
    """)

    # Insert data into players table
    with open(players_csv, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        players_data = [(row['mjs_id'], row['name'], row['discord_id'], row['mjs_nickname']) for row in reader]
        cursor.executemany("""
            INSERT INTO players (mjs_id, name, discord_id, mjs_nickname)
            VALUES (?, ?, ?, ?);
        """, players_data)

    # Insert data into teams table
    with open(teams_csv, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        teams_data = [(row['team_name'], row['player1_id'], row['player2_id'], row['player3_id'], row['player4_id']) for row in reader]
        cursor.executemany("""
            INSERT INTO teams (team_name, player1_id, player2_id, player3_id, player4_id)
            VALUES (?, ?, ?, ?, ?);
        """, teams_data)

    # Insert data into schedule table
    with open(schedule_csv, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        schedule_data = [(row['match_id'], row['week_id'], row['team1'], row['team2'], row['team3'], row['team4'], row['start_time']) for row in reader]
        cursor.executemany("""
            INSERT INTO schedule (match_id, week_id, team1, team2, team3, team4, start_time)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, schedule_data)

    # Commit changes and close connection
    conn.commit()
    conn.close()


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py players.csv teams.csv schedule.csv")
    else:
        players_csv = sys.argv[1]
        teams_csv = sys.argv[2]
        schedule_csv = sys.argv[3]
        initialize_db(players_csv, teams_csv, schedule_csv)
        print("Database 'tournament.db' initialized successfully.")