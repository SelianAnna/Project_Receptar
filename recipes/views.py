from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Recipe, Ingredient
from .forms import RecipeForm

class RecipeListView(ListView):
    model = Recipe
    template_name = "recipes/recipe_list.html"
    context_object_name = "recipes"
    paginate_by = 12

class RecipeDetailView(DetailView):
    model = Recipe
    template_name = "recipes/recipe_detail.html"
    context_object_name = "recipe"

class RecipeCreateView(LoginRequiredMixin, CreateView):
    model = Recipe
    form_class = RecipeForm
    template_name = "recipes/recipe_form.html"
    success_url = reverse_lazy("recipes:list")

    def form_valid(self, form):
        self.object = form.save(user=self.request.user)
        return super().form_valid(form)

class IngredientListView(ListView):
    model = Ingredient
    template_name = "recipes/ingredient_list.html"
    context_object_name = "ingredients"
    paginate_by = 30

class RecipeSearchView(ListView):
    model = Recipe
    template_name = "recipes/recipe_search.html"
    context_object_name = "recipes"

    def get_queryset(self):
        qs = Recipe.objects.all()
        q = self.request.GET.get("q", "").strip()
        ingredients = self.request.GET.get("ingredients", "").strip()

        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(instructions__icontains=q))

        if ingredients:
            tokens = [t.strip() for t in ingredients.split(",") if t.strip()]
            for t in tokens:
                qs = qs.filter(ingredients__name__iexact=t)

        return qs.distinct()

class RecipeUpdateView(LoginRequiredMixin, UpdateView):
    model = Recipe
    form_class = RecipeForm
    template_name = "recipes/recipe_form.html"
    success_url = reverse_lazy("recipes:list")

    def get_queryset(self):
        return Recipe.objects.filter(created_by=self.request.user)

class RecipeDeleteView(LoginRequiredMixin, DeleteView):
    model = Recipe
    template_name = "recipes/recipe_confirm_delete.html"
    success_url = reverse_lazy("recipes:list")

    def get_queryset(self):
        return Recipe.objects.filter(created_by=self.request.user)