import requests

from adapters.local_user_persistance import LocalUserPersistance
from core.services.auth import AuthService
from core.services.user import UserService
from main import BASE_URL

class PlaylistMaker:

    def __init__(self):
        self.auth_service = AuthService()
        self.user_service = UserService(user_persistance=LocalUserPersistance())
    
    def create_playlist(self, token):
        tracks = self.fetch_top_tracks(token)
        tracks_uris = [track["uri"] for track in tracks["items"]]
        playlist_response = requests.post(
            url=BASE_URL + "v1/me/playlists/",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json={
                "name": "My Top Tracks",
                "description": "A playlist of my top tracks",
                "public": False
            }
        )
        playlist_id = playlist_response.json()["id"]
        playlist_response = requests.post(
            url=BASE_URL + f"v1/playlists/{playlist_id}/items?uris={','.join(tracks_uris)}",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json={
                "name": "My Top Tracks",
                "description": "A playlist of my top tracks",
                "public": False
            }
        )
        return playlist_response.json()

    def fetch_top_tracks(self, token):
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        return requests.get(
            url=BASE_URL + "v1/me/top/tracks?time_range=long_term&limit=50&offset=50",
            headers=headers
        ).json()
    

    def main(self):
        self.user_service.get_user_token()
        if not self.user_service.get_user_token():
            data = self.auth_service.main_flow()
            self.user_service.write_user_token(data)

        
        if self.create_playlist(self.user_service.get_user_token().get("access_token")) == False:
            data = self.auth_service.main_flow()
            self.user_service.write_user_token(data)
            self.create_playlist(self.user_service.get_user_token().get("access_token"))
            

if __name__ == "__main__":
    playlist_maker = PlaylistMaker()
    playlist_maker.main()