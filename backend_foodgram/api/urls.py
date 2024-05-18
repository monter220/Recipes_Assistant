from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    UsersViewSet,
    TagViewSet,
    IngredientViewSet,
    RecipeViewSet,
    DownloadCart,
)


router = DefaultRouter()
router.register('users', UsersViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')


urlpatterns = [
    path('recipes/download_shopping_cart/', DownloadCart.as_view()),
    path('', include(router.urls)),
]
