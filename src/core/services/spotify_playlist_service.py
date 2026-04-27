import logging

from dataclasses import dataclass

import requests


logger = logging.getLogger("requests")

BASE_URL = "https://api.spotify.com/"


@dataclass
class FetchTopTracksParams:
    time_range: str
    limit: int
    offset: int

@dataclass
class CreatePlaylistParams:
    name: str
    description: str = ""
    public: bool = False
class SpotifyPlaylistService:

    def __init__(self, token):
        self.token = token

    def create_playlist(self, params: CreatePlaylistParams) -> str:
        playlist_response = requests.post(
            url=BASE_URL + "v1/me/playlists/",
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            },
            json={
                "name": params.name,
                "description": params.description,
                "public": params.public
            }
        )
        playlist_response.raise_for_status()
        return playlist_response.json()["id"]

    def fetch_top_tracks(self, params: FetchTopTracksParams) -> list:
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        response = requests.get(
            url=BASE_URL + f"v1/me/top/tracks?time_range={params.time_range}&limit={params.limit}&offset={params.offset}",
            headers=headers
        )
        response.raise_for_status()
        return response.json()["items"]

    def get_tracks_uris(self, tracks: list) -> list:
        return [track["uri"] for track in tracks]
    
    def add_tracks_to_playlist(self, playlist_id, tracks_uris):
        response = requests.post(
            url=BASE_URL + f"v1/playlists/{playlist_id}/items?uris={','.join(tracks_uris)}",
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            },
        )
        response.raise_for_status()
