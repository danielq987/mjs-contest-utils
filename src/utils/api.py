import requests
from utils.auth import get_auth_token
from utils.helpers import get_env

def mjs_call(method, path, payload=None, params=None, token=None, verbose=False):
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
    
    if not token:
        token = get_auth_token()
    
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
    
    default_queryparams = {
        "unique_id": get_env('MJS_CONTEST_ID'),  # Replace with your actual contest ID
        "season_id": get_env('MJS_SEASON_ID', 1),
    }
    
    params = {} if not params else {**default_queryparams, **params}
    
    if verbose:
        redacted_headers = {k: v for k, v in headers.items() if k != 'authorization'}
        print(f"Making {method} request to {url}")
        print(f"Headers: {redacted_headers}")
        print(f"Query Params: {params}")
        if payload:
            print(f"Payload: {payload}")

    # Make the HTTP request
    if method == "GET":
        response = requests.get(url, headers=headers, params=params)
    elif method == "POST":
        response = requests.post(url, headers=headers, json=payload, params=params)

    return response

def mjs_get(path, queryparams=None, token=None, verbose=False):
    return mjs_call("GET", path, params=queryparams, token=token, verbose=verbose)

def mjs_post(path, payload=None, queryparams=None, token=None, verbose=False):
    return mjs_call("POST", path, payload=payload, params=queryparams, token=token, verbose=verbose)

def fetch_results_csv(verbose=False):
    """
    Fetches the results CSV from the API.
    
    Returns:
        str: The CSV content as a string.
    """
    params = {
        "offset": 0,
        "limit": 1000
    }
    response = mjs_get("/fetch_contest_game_records", queryparams=params, verbose=verbose)
    response.raise_for_status()
    return response.json()["data"]["record_list"]
