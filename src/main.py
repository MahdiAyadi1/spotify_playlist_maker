import base64
import os
import re
import socket
import time
import requests
import webbrowser

from dotenv import load_dotenv
from helper import stringify

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("SPOTIFY_API_SECRET")
BASE_URL = "https://api.spotify.com/"
redirect_uri = 'http://127.0.0.1:5000/callback'


def fetch_top_tracks(token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    return requests.get(
        url=BASE_URL + "v1/me/top/tracks?time_range=medium_term&limit=20",
        headers=headers
    ).json()

def fetch_web_api(endpoint, token, method="GET", body=None):
    headers = {
        "Authorization": f"Bearer {token}"
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
    scope = 'user-follow-read user-follow-modify user-library-read user-library-modify user-top-read playlist-read-private playlist-modify-public playlist-modify-private'
    data_to_stringify = {
        "state": state,
        "scope": scope,
        "response_type": 'code',
        "client_id": client_id,
        "redirect_uri": redirect_uri,
    }
    auth_url = 'https://accounts.spotify.com/authorize?' + stringify(data_to_stringify)
    webbrowser.open(auth_url)

def get_top_tracks():
    data = fetch_web_api(
        "v1/me/top/tracks?time_range=long_term&limit=5",
        method="GET"
    )
    return data.get("items", [])


if __name__ == "__main__":
    authorize()
    HOST = '127.0.0.1'  # Localhost
    PORT = 5000
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))  # Bind the socket to the port
        s.listen()            # Put the socket into listening mode
        print(f"Listening on {HOST}:{PORT}...")

        conn, addr = s.accept()  # Wait for a connection
        with conn:
            print(f"Connected by {addr}")
            request_data = b""
            while True:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                request_data += chunk
                if b"\r\n\r\n" in request_data:
                    break

            http_request = request_data.decode("utf-8", errors="replace")
            response_body = "OK"
            http_response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/plain\r\n"
                f"Content-Length: {len(response_body)}\r\n"
                "Connection: close\r\n"
                "\r\n"
                + response_body
            )
            conn.sendall(http_response.encode("utf-8"))

    data = http_request

    if "error=" in data:
        raise
    code = re.search(r'code=([^&]+)', data).group(1)
    state = re.search(r'state=([^&]+)', data).group(1)
    
    response = requests.request(
        method="POST",
        url='https://accounts.spotify.com/api/token',
        data= {
            'code': code,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        },
        headers= {
            'content-type': 'application/x-www-form-urlencoded',
            'Authorization': 'Basic ' + base64.b64encode(
                f'{client_id}:{client_secret}'.encode()
            ).decode()
        }
    )
    response_decoded = response.content.decode("utf-8", errors="replace")
    
    access_token = response.json().get("access_token")
    refresh_token = response.json().get("refresh_token")

    tracks = fetch_top_tracks(access_token)
    print("Done")