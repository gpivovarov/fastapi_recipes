from pydantic import BaseModel


class BaseError(BaseModel):
    msg: str = 'Undefined error'
    code: int = 500
