from fastapi import APIRouter
from src.recipes.service import recipes_service
from src.recipes.schemas import RecipeCreateResponse, RecipeResponse

router = APIRouter()

router.add_api_route(
    '/add',
    recipes_service.add_recipe,
    methods={'post'},
    response_model=RecipeCreateResponse
)
router.add_api_route(
    '/list',
    recipes_service.list,
    methods={'get'},
    response_model=list[RecipeResponse]
)
router.add_api_route(
    '/list/filter',
    recipes_service.filter,
    methods={'get'},
    response_model=list[RecipeResponse]
)
router.add_api_route(
    '/{recipe_id}',
    recipes_service.get_by_id,
    methods={'get'},
    response_model=RecipeResponse
)
router.add_api_route(
    '/{recipe_id}',
    recipes_service.update_recipe,
    methods={'patch'},
    response_model=RecipeResponse
)
