"""
AuthService is responsible for handling all the authentication related logic,
such as requesting access data, requesting access and refresh tokens.
Currently support persistance for only one user.
"""

import base64
import os
import re
import socket
import webbrowser

import requests

from helper import stringify

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("SPOTIFY_API_SECRET")
BASE_URL = "https://api.spotify.com/"
redirect_uri = 'http://127.0.0.1:5000/callback'

class AuthService:
    def __init__(self):
        self.access_token = None
        self.refresh_token = None

    def request_authorization_data(self):
        pass
    
    def request_access_and_refresh_token(self):
        pass

    def refresh_access_token(self):
        pass

    def main_flow(self):
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
        access_token = response.json().get("access_token")
        refresh_token = response.json().get("refresh_token")
        return {"access_token": access_token, "refresh_token": refresh_token}
