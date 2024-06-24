import asyncio, pytest, os, random
from typing import AsyncGenerator
from httpx import AsyncClient
from fastapi.testclient import TestClient
from src.main import app
from tests.seeder import Seeder as SeederClass
from dotenv import load_dotenv

load_dotenv()

seeder = SeederClass()
client = TestClient(app)
user_data = seeder.AUTHOR_DATA
access_token = None
recipe_id = None


@pytest.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url=f'http://{os.getenv('SERVER_IP_ADDRESS')}:{os.getenv('SERVER_PORT')}') as ac:
        yield ac


async def test_register_user(ac: AsyncClient):
    response = await ac.post('/users/register', json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert 'id' in data
    user_data['id'] = data['id']


async def test_login_user(ac: AsyncClient):
    global access_token
    response = await ac.post('/users/login', json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert 'access_token' in data
    access_token = data['access_token']


async def test_get_user_profile(ac: AsyncClient):
    global access_token
    response = await ac.get('/users/profile', headers={
        'Authorization': f'Bearer {access_token}'
    })
    assert response.status_code == 200
    data = response.json()
    assert 'id' in data
    assert data['id'] == user_data['id']
    assert data['email'] == user_data['email']


async def test_incorrect_token_get_user_profile(ac: AsyncClient):
    response = await ac.get('/users/profile', headers={
        'Authorization': 'Bearer aaabbbccceeeeefffffggggg'
    })
    assert response.status_code == 401


async def test_add_recipe(ac: AsyncClient):
    global access_token, recipe_id
    categories = await seeder.get_categories_ids()
    ingredients = await seeder.get_ingredients_ids()
    used_ids = []
    value = 0

    payload = {
        'title': seeder.RECIPE_TITLES[random.randint(0, len(seeder.RECIPE_TITLES) - 1)],
        'description': seeder.RECIPE_DESC[random.randint(0, len(seeder.RECIPE_DESC) - 1)],
        'cooking_time': seeder.RECIPE_COOK_TIME[random.randint(0, len(seeder.RECIPE_COOK_TIME) - 1)],
        'categories': [],
        'ingredients': []
    }

    for i in range(0, random.randint(1, 3)):
        if len(categories) > 1:
            while value in used_ids:
                value = categories[random.randint(0, len(categories) - 1)]
        used_ids.append(value)
        payload['categories'].append(value)

    used_ids.clear()
    value = 0

    for i in range(0, random.randint(4, 12)):
        if len(ingredients) > 1:
            while value in used_ids:
                value = ingredients[random.randint(0, len(ingredients) - 1)]
        used_ids.append(value)
        payload['ingredients'].append(value)

    response = await ac.post(
        '/recipes/add',
        headers={
            'Authorization': f'Bearer {access_token}'
        },
        json=payload
    )
    assert response.status_code == 200
    data = response.json()
    assert 'id' in data
    recipe_id = data['id']


async def test_update_recipe(ac: AsyncClient):
    global access_token, recipe_id
    response = await ac.patch(
        f'/recipes/{recipe_id}',
        headers={
            'Authorization': f'Bearer {access_token}'
        },
        json={
            'title': f'Recipe {recipe_id} updated',
            'cooking_time': 100
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data['title'] == f'Recipe {recipe_id} updated'
    assert data['cooking_time'] == 100
