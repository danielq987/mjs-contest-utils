import requests
from utils.helpers import get_env

# Not sure what exactly these represent, but needed for auth. See README for how to obtain.
MJS_SECRET=get_env('MJS_SECRET')
MJS_UID=get_env('MJS_UID')

def get_auth_token(isVerbose=False):
    # Step 1: Exchange initial token for accessToken
    headers = {
        'accept': 'application/json, text/plain, */*',
        'content-type': 'application/json',
        'origin': 'https://mahjongsoul.tournament.yo-star.com'
    }

    login_url = 'https://passport.mahjongsoul.com/user/login'
    login_payload = {
        "uid": MJS_UID,
        "token": MJS_SECRET,
        "deviceId": f"web|{MJS_UID}"
    }

    response1 = requests.post(login_url, headers=headers, json=login_payload)
    response1.raise_for_status()  # Raises error if the request failed
    response_data = response1.json()

    if isVerbose:
        print("Login Step 1 Response:")
        print(f"Status code {response1.status_code}")
        print(response_data)

    access_token = response_data.get('accessToken')

    if not access_token:
        raise ValueError("Failed to retrieve access token in Auth Step 1.")

    # Step 2: Exchange accessToken for auth token
    auth_url = "https://engs.mahjongsoul.com/api/contest_gate/api/login?method=oauth2"
    auth_payload = {
        "type": 8,
        "code": access_token,
        "uid": int(MJS_UID)
    }

    response2 = requests.post(auth_url, headers=headers, json=auth_payload)
    response2.raise_for_status()

    if isVerbose:
        print("Login Step 2 Response:")
        print(f"Status code {response2.status_code}")
        print(response2.json())

    auth_token = response2.json().get('data', {}).get('token')

    if not auth_token:
        print(response2)
        raise ValueError("Failed to retrieve auth token.")
    
    return auth_token
