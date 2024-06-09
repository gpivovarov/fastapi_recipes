from fastapi import APIRouter
from src.users.service import user_service
from src.users.schemas import UserRegister, UserToken, User

router = APIRouter()

router.add_api_route(
    '/register',
    user_service.register,
    methods={'post'},
    response_model=UserRegister
)
router.add_api_route(
    '/login',
    user_service.login,
    methods={'post'},
    response_model=UserToken
)
router.add_api_route(
    '/profile',
    user_service.get_current,
    methods={'get'},
    response_model=User
)
