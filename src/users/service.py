from src.core.service import BaseService
from src.users.models import User


class UserService(BaseService):
    async def register(self):
        return await self.create(model=User, values={
            'password': 'agldslgdsg',
            'email': 'agsdgsdfhfdh@asfdsg.sdgds'
        })


user_service = UserService()
