from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    id: int | None = None


class UserEmailMixin:
    email: EmailStr


class UserPasswordMixin:
    password: str


class UserCreate(BaseModel, UserEmailMixin, UserPasswordMixin):
    pass


class UserLogin(UserCreate):
    pass


class UserToken(BaseModel):
    access_token: str | None = None


class User(UserRegister):
    email: EmailStr | None = None
