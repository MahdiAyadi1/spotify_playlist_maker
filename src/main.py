import os
import requests
import webbrowser

from dotenv import load_dotenv
from helper import stringify

load_dotenv()

client_id = os.getenv("CLIENT_ID")
BASE_URL = "https://api.spotify.com/"
redirect_uri = 'http://127.0.0.1:5000/callback'

def fetch_web_api(endpoint, token, method="GET", body=None):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    url = BASE_URL + endpoint

    response = requests.request(
        method=method,
        url=url,
        headers=headers,
        json=body
    )
    
    response.raise_for_status()
    return response.json()


def authorize():
    state = "some long string"
    scope = 'user-read-private user-read-email'
    data_to_stringify = {
        "state": state,
        "scope": scope,
        "response_type": 'code',
        "client_id": client_id,
        "redirect_uri": redirect_uri,
    }
    response = requests.request(
        method="GET",
        url='https://accounts.spotify.com/authorize?' + stringify(data_to_stringify),
    )
    webbrowser.open(response.url)

def get_top_tracks():
    data = fetch_web_api(
        "v1/me/top/tracks?time_range=long_term&limit=5",
        method="GET"
    )
    return data.get("items", [])


if __name__ == "__main__":
    authorize()
