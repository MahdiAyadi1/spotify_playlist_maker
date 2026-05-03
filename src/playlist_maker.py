import logging
import requests
import jwt
import time

import yaml
from adapters.local_user_persistance import LocalUserPersistance
from core.services.auth import AuthService
from core.services.spotify_playlist_service import (
    CreatePlaylistParams,
    FetchTopTracksParams,
    SpotifyPlaylistService,
)
from core.services.user import UserService

logger = logging.getLogger()


class PlaylistMaker:

    def __init__(self):
        self.auth_service = AuthService()
        self.user_service = UserService(user_persistance=LocalUserPersistance())
        with open("config/playlist_param.yaml", "r") as f:
            params = yaml.safe_load(f)
        logger.info("Fetched playlist parameters from config file")
        self.playlist_name = params.get("playlist_name") or "My Tracks"
        self.description = params.get("description") or ""
        self.public = params.get("public") or False
        self.time_range = params.get("time_range") or "long_term"
        self.limit = params.get("limit") or 20
        self.offset = params.get("offset") or 0

    def fetch_user_token(self):
        """Fetches the user token from local storage. If the token is not found, it raises an exception."""
        try:
            logger.info("Fetching user token from local storage")
            token = self.user_service.get_user_token()
            if not token:
                raise Exception("No token found")
            return token
        except Exception as e:
            logger.error(f"Error occurred while fetching user token: {e}")
            raise e

    def run_auth_flow(self):
        """Runs the authentication flow to fetch a new token and saves it to local storage."""
        try:
            logger.info("Running authentication flow to fetch new token")
            data = self.auth_service.main_flow()
            self.user_service.write_user_token(data)
            return data.get("access_token")
        except Exception as e:
            logger.error(f"Error occurred during authentication flow: {e}")
            raise e

    def check_token_validity(self, token):
        """Checks if the token is valid by parsing it and checking expiration date."""
        try:
            decoded = jwt.decode(token, options={"verify_signature": False})
            exp = decoded.get("exp")
            if exp and time.time() < exp:
                return True
            else:
                return False
        except Exception as e:
            logger.error(f"Error occurred while checking token validity: {e}")
            return False

    def refresh_token(self):
        """Refreshes the token by running the authentication flow again."""
        try:
            logger.info("Refreshing token")
            refresh_token = self.fetch_user_token().get("refresh_token")
            if not refresh_token:
                raise Exception("No refresh token found")
            data = self.auth_service.refresh_access_token(refresh_token)
            data["refresh_token"] = refresh_token
            self.user_service.write_user_token(data)
            return data.get("access_token")
        except Exception as e:
            logger.error(f"Error occurred while refreshing token: {e}")
            raise e

    def main(self):
        logger.info("Starting playlist maker")
        try:
            access_token = self.fetch_user_token().get("access_token")
        except Exception as e:
            logger.error(f"Error occurred while fetching user token: {e}")
            access_token = self.run_auth_flow()

        if not self.check_token_validity(access_token):
            logger.info("Token is invalid or expired, refreshing token")
            access_token = self.refresh_token()

        playlist_service = SpotifyPlaylistService(token=access_token)
        try:
            logger.info("Creating playlist and adding tracks")
            playlist_id = playlist_service.create_playlist(
                params=CreatePlaylistParams(
                    name=self.playlist_name,
                    description=self.description,
                    public=self.public,
                )
            )
            logger.debug(f"Playlist created successfully with id {playlist_id}")
            tracks = playlist_service.fetch_top_tracks(
                params=FetchTopTracksParams(
                    time_range=self.time_range, limit=self.limit, offset=self.offset
                )
            )
            logger.debug(
                f"Fetched top tracks for user with time range {self.time_range}, limit {self.limit} and offset {self.offset}"
            )
            tracks_uris = playlist_service.get_tracks_uris(tracks)
            playlist_service.add_tracks_to_playlist(
                playlist_id=playlist_id, tracks_uris=tracks_uris
            )
            logger.info("Playlist created and tracks added successfully")
        except requests.HTTPError as e:
            logger.error(f"Error occurred while creating playlist: {e}")
            raise e
