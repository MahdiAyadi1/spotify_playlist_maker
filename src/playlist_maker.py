import logging

import requests

from adapters.local_user_persistance import LocalUserPersistance
from core.services.auth import AuthService
from core.services.spotify_playlist_service import CreatePlaylistParams, FetchTopTracksParams, SpotifyPlaylistService
from core.services.user import UserService

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('[%(asctime)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.info("Logger initialized for requests library")
class PlaylistMaker:

    def __init__(self):
        self.auth_service = AuthService()
        self.user_service = UserService(user_persistance=LocalUserPersistance())   

    def main(self):
        logger.info("Starting playlist maker")
        try:
            playlist_service = SpotifyPlaylistService(token=self.user_service.get_user_token().get("access_token"))
        except Exception as e:
            logger.error(f"Error occurred while fetching user token: {e}")
            raise e
        try:
            playlist_id = playlist_service.create_playlist(
                params=CreatePlaylistParams(
                    name="My Top Tracks",
                    description="A playlist of my top tracks",
                    public=False
                )
            )
        except requests.HTTPError as e:
            logger.error(f"Error occurred while creating playlist: {e}")
            data = self.auth_service.main_flow()
            self.user_service.write_user_token(data)
            playlist_service = SpotifyPlaylistService(token=self.user_service.get_user_token().get("access_token"))
            playlist_id = playlist_service.create_playlist(
                params=CreatePlaylistParams(
                    name="My Top Tracks",
                    description="A playlist of my top tracks",
                    public=False
                )
            )
        tracks = playlist_service.fetch_top_tracks(
            params=FetchTopTracksParams(
                time_range="long_term",
                limit=50,
                offset=0
            )
        )
        tracks_uris = playlist_service.get_tracks_uris(tracks)
        playlist_service.add_tracks_to_playlist(playlist_id=playlist_id, tracks_uris=tracks_uris)

if __name__ == "__main__":
    playlist_maker = PlaylistMaker()
    playlist_maker.main()