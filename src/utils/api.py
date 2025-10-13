import requests
from time import time
from utils.auth import get_auth_token
from utils.helpers import get_env

def mjs_call(method, path, payload=None, params=None):
    """
    Wrapper around requests for making API calls with default headers.
    
    Args:
        method (str): HTTP method, either 'GET' or 'POST'.
        path (str): The endpoint path (e.g. '/users').
        payload (dict, optional): JSON payload for POST requests.
        queryparams (dict, optional): Query parameters for the request.
        
    Returns:
        Response: The response object from requests.
        
    Raises:
        ValueError: If the HTTP method is not supported.
    """
    API_ROOT = "https://engs.mahjongsoul.com/api/contest_gate/api/contest"

    if method not in ["GET", "POST"]:
        raise ValueError("Unsupported HTTP method. Use 'GET' or 'POST'.")
    
    token = get_env("MJS_TOKEN_CACHE") if get_env("MJS_TOKEN_CACHE") else get_auth_token()
    
    # Normalize method
    method = method.upper()
    
    # Construct full URL
    url = f"{API_ROOT.rstrip('/')}/{path.lstrip('/')}"

    # Default headers
    headers = {
        'accept': 'application/json, text/plain, */*',
        'authorization': f'Majsoul {token}',
        'origin': 'https://mahjongsoul.tournament.yo-star.com'
    }
    
    default_params = {
        "unique_id": get_env('MJS_CONTEST_ID'),  # Replace with your actual contest ID
        "season_id": get_env('MJS_SEASON_ID', 1),
    }

    all_params = {} if params == None else {**default_params, **params}
    all_payload = {} if payload == None else {**default_params, **payload}
    
    verbose = get_env('VERBOSE')
    
    if verbose:
        redacted_headers = {k: v for k, v in headers.items() if k != 'authorization'}
        print(f"Making {method} request to {url}")
        print(f"Headers: {redacted_headers}")
        print(f"Query Params: {all_params}")
        if payload:
            print(f"Payload: {payload}")

    # Make the HTTP request
    if method == "GET":
        response = requests.get(url, headers=headers, params=all_params)
    elif method == "POST":
        response = requests.post(url, headers=headers, json=all_payload, params=all_params)

    response.raise_for_status()
    return response

def mjs_get(path, params=None):
    return mjs_call("GET", path, params=params)

def mjs_post(path, payload=None, params=None):
    return mjs_call("POST", path, payload=payload, params=params)

def fetch_results_csv():
    """
    Fetches the results CSV from the API.
    Example response:
    [{
        "accounts": [
            {
                "account_id": 124543013,
                "nickname": "bartpuup",
                "remark": "",
                "seat": 0
            },
            {
                "account_id": 124646953,
                "nickname": "voxyn",
                "remark": "",
                "seat": 1
            },
            {
                "account_id": 124537122,
                "nickname": "zutomayofan7",
                "remark": "",
                "seat": 2
            },
            {
                "account_id": 124553037,
                "nickname": "TripWhiteDrags",
                "remark": "",
                "seat": 3
            }
        ],
        "end_time": 1760150274,
        "removed": 0,
        "result": {
            "players": [
                {
                    "part_point_1": 41200,
                    "seat": 3,
                    "total_point": 31200
                },
                {
                    "part_point_1": 38300,
                    "seat": 2,
                    "total_point": 18300
                },
                {
                    "part_point_1": 16500,
                    "seat": 1,
                    "total_point": -13500
                },
                {
                    "part_point_1": 4000,
                    "seat": 0,
                    "total_point": -36000
                }
            ]
        },
        "start_time": 1760148241,
        "tag": "5",
        "uuid": "251011-79b8ca31-78aa-4aa8-bfb2-038b590c5e64"
    }]
    """
    params = {
        "offset": 0,
        "limit": 1000
    }
    response = mjs_get("/fetch_contest_game_records", params=params)
    return response.json()["data"]["record_list"]

# Takes a tuple of team indexes and returns a list of player ids if all players are in the waiting room. Otherwise, returns an empty list.
def get_waiting_players():
    """
    Fetches the ready players from the API.
    
    Example response:
    [
        {
            "account_id": 120539882,
            "nickname": "danielq987",
            "remark": "",
            "team_name": "Itsumodo"
        }
    ]
    """ 
    response = mjs_get("/ready_player_list", params={})
    return response.json()["data"]

def start_match(match_id, players):
    """
    Starts a match

    match_id (str): id of the game
    players (str[]): ids of the players to start game with e.g. ["1010101010", "1010101011", "1010101012", "1010101013"]
    """
    start_payload = {
        "account_list": players,
        "ai_level": 2,
        "game_start_time": int(time()),
        "init_points": [25000, 25000, 25000, 25000],
        "remark": str(match_id),
        "shuffle_seats": False,
    }
    
    response = mjs_post("/create_game_plan", payload=start_payload)
    response.raise_for_status()
    return True