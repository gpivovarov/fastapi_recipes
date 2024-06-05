from fastapi import APIRouter
from src.users.service import user_service

router = APIRouter()

router.add_api_route(
    '/register',
    user_service.register,
    methods={'post'}
)
