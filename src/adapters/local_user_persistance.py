import os

import yaml

from core.ports.user_persistance import UserPersistance


class LocalUserPersistance(UserPersistance):
    
    def __init__(self):
        super().__init__()
        self.user_data = None
        os.makedirs(os.path.dirname("_local/user_data.yaml"), exist_ok=True)
        

    def get_user_token(self, user_id ="default_user"):
        return yaml.load(open("_local/user_data.yaml", "r"), Loader=yaml.FullLoader)
    
    def write_user_token(self, user_data, user_id="default_user"):
        self.user_data = user_data
        yaml.dump(self.user_data, open("_local/user_data.yaml", "w"))