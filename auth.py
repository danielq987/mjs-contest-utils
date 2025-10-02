import requests

def get_auth_token(MJS_SECRET, MJS_UID):

    # Step 1: Exchange initial token for accessToken
    login_url = 'https://passport.mahjongsoul.com/user/login'
    login_payload = {
        "uid": MJS_UID,
        "token": MJS_SECRET,
        "deviceId": f"web|{MJS_UID}"
    }
    login_headers = {
        'accept': 'application/json, text/plain, */*',
        'content-type': 'application/json;charset=UTF-8',
        'origin': 'https://mahjongsoul.tournament.yo-star.com'
    }

    response1 = requests.post(login_url, headers=login_headers, json=login_payload)
    print(f"Login response status: {response1.status_code}")
    response_data = response1.json()
    response1.raise_for_status()  # Raises error if the request failed
    access_token = response_data.get('accessToken')

    if not access_token:
        raise ValueError("Failed to retrieve access token.")

    # Step 2: Exchange accessToken for auth token
    auth_url = "https://engs.mahjongsoul.com/api/contest_gate/api/login?method=oauth2"
    auth_headers = {
        'accept': 'application/json, text/plain, */*',
        'content-type': 'application/json',
        'origin': 'https://mahjongsoul.tournament.yo-star.com'
    }
    auth_payload = {
        "type": 8,
        "code": access_token,
        "uid": int(MJS_UID)
    }

    response2 = requests.post(auth_url, headers=auth_headers, json=auth_payload)
    response2.raise_for_status()
    auth_token = response2.json().get('data', {}).get('token')

    if not auth_token:
        raise ValueError("Failed to retrieve auth token.")
    
    return auth_token