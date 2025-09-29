from django.urls import path
from .views import (
    RecipeListView, RecipeDetailView, RecipeCreateView,
    IngredientListView, RecipeSearchView
)

app_name = "recipes"

urlpatterns = [
    path("", RecipeListView.as_view(), name="list"),
    path("search/", RecipeSearchView.as_view(), name="search"),
    path("ingredients/", IngredientListView.as_view(), name="ingredients"),
    path("new/", RecipeCreateView.as_view(), name="create"),
    path("<int:pk>/", RecipeDetailView.as_view(), name="detail"),
]