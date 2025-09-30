from django.urls import path
from .views import (
    RecipeListView, RecipeDetailView, RecipeCreateView,
    RecipeUpdateView, RecipeDeleteView,
    IngredientListView, IngredientRecipeListView, RecipeSearchView,
    ingredients_cleanup_view,  # ak cleanup nepoužívaš, môžeš túto path odmazať
)

app_name = "recipes"

urlpatterns = [
    path("", RecipeListView.as_view(), name="list"),
    path("search/", RecipeSearchView.as_view(), name="search"),
    path("ingredients/", IngredientListView.as_view(), name="ingredients"),
    path("ingredients/<int:pk>/recipes/", IngredientRecipeListView.as_view(), name="ingredient_recipes"),
    path("ingredients/cleanup/", ingredients_cleanup_view, name="ingredients_cleanup"),
    path("new/", RecipeCreateView.as_view(), name="create"),
    path("<int:pk>/", RecipeDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", RecipeUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", RecipeDeleteView.as_view(), name="delete"),
]