import os
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.hash import argon2
from datetime import datetime, timedelta
from src.core.service import BaseService
from src.users.models import User
from src.users.schemas import UserCreate, UserLogin

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/login')

class UserService(BaseService):
    def create_access_token(self, data: dict):
        data.update({'expire': (datetime.now() + timedelta(minutes=int(os.environ['ACCESS_TOKEN_LIFETIME_MINUTES']))).timestamp()})
        return jwt.encode(data, os.environ['SECRET_KEY'], algorithm=os.environ['ALGORITHM'])

    def decode_access_token(self, token: str):
        data = jwt.decode(token, os.environ['SECRET_KEY'], algorithms=[os.environ['ALGORITHM']])
        if int(data['expire']) < int(datetime.now().timestamp()):
            raise HTTPException(status_code=401, detail='Token expired')
        return data

    async def register(self, data: UserCreate):
        data.password = argon2.hash(data.password)
        result = await self.create(model=User, values=data.model_dump())
        if result:
            return result
        raise HTTPException(status_code=500, detail='Unknown error on user service')

    async def login(self, data: UserLogin):
        user = await self.get_one(model=User, filter={'email': data.email})
        if not user:
            raise HTTPException(status_code=404, detail='User not found')
        if argon2.verify(data.password, user.password):
            return {'access_token': self.create_access_token(data=data.model_dump())}
        raise HTTPException(status_code=200, detail='Wrong password')

    async def get_current(self, token: str = Depends(oauth2_scheme)):
        try:
            token_data = self.decode_access_token(token)
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Access token has expired')
        except Exception as e:
            raise HTTPException(status_code=401, detail=f'Token error: {repr(e)}')

        user = await self.get_one(model=User, filter={'email': token_data['email']})
        return user


user_service = UserService()
