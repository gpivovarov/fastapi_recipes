import uvicorn
from fastapi import FastAPI, APIRouter
from src.users.models import User
from src.users.router import router as user_router

app = FastAPI()
router = APIRouter()
router.include_router(user_router, prefix='/users', tags=['Users'])
router.add_api_route('/', lambda: sorted({route.path for route in vars(router)['routes']}))
app.include_router(router)


if __name__ == '__main__':
    uvicorn.run(app,
                host='127.0.0.1',
                port=80)