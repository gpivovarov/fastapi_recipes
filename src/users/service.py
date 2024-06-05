from src.core.service import BaseService


class UserService(BaseService):
    def register(self):
        return self.create()


user_service = UserService()
