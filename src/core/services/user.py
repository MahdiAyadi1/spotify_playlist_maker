
from core.ports.user_persistance import UserPersistance


class UserService:

    def __init__(self, user_persistance : UserPersistance):
        self.user_persistance = user_persistance

    def get_user_token(self, user_id="default_user"):
        return self.user_persistance.get_user_token(user_id)

    def write_user_token(self,user_data, user_id="default_user"):
        return self.user_persistance.write_user_token(user_data, user_id)
