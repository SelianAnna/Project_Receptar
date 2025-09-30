from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .models import Recipe, Ingredient, RecipeIngredient
from .forms import RecipeForm


def cleanup_orphan_ingredients():
    """
    Zmaže ingrediencie, ktoré už nemajú žiadnu väzbu v RecipeIngredient.
    """
    Ingredient.objects.filter(recipeingredient__isnull=True).delete()


@require_POST
@user_passes_test(lambda u: u.is_superuser)
def ingredients_cleanup_view(request):
    """
    Vyčistí nepoužívané ingrediencie (len superuser, POST).
    """
    deleted, _ = Ingredient.objects.filter(recipeingredient__isnull=True).delete()
    messages.success(request, f"Zmazaných nepoužívaných ingrediencií: {deleted}")
    return redirect("recipes:ingredients")


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
        # uloženie receptu s autorom
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.save()

        # ukladanie ingrediencií z dynamických polí (meno + množstvo)
        names = self.request.POST.getlist("ingredient_name")
        amounts = self.request.POST.getlist("ingredient_amount")
        for name, amount in zip(names, amounts):
            name = (name or "").strip()
            amount = (amount or "").strip()
            if not name:
                continue
            ing, _ = Ingredient.objects.get_or_create(name=name)
            RecipeIngredient.objects.create(recipe=self.object, ingredient=ing, amount=amount)

        # po úspechu presmeruj
        return redirect(self.get_success_url())


class RecipeUpdateView(LoginRequiredMixin, UpdateView):
    model = Recipe
    form_class = RecipeForm
    template_name = "recipes/recipe_form.html"
    success_url = reverse_lazy("recipes:list")

    def get_queryset(self):
        # superuser môže upravovať všetko, ostatní len svoje
        if self.request.user.is_superuser:
            return Recipe.objects.all()
        return Recipe.objects.filter(created_by=self.request.user)

    def form_valid(self, form):
        # Uloží základné polia receptu
        self.object = form.save()

        # Prepíš ingrediencie podľa formulára:
        RecipeIngredient.objects.filter(recipe=self.object).delete()

        names = self.request.POST.getlist("ingredient_name")
        amounts = self.request.POST.getlist("ingredient_amount")
        for name, amount in zip(names, amounts):
            name = (name or "").strip()
            amount = (amount or "").strip()
            if not name:
                continue
            ing, _ = Ingredient.objects.get_or_create(name=name)
            RecipeIngredient.objects.create(recipe=self.object, ingredient=ing, amount=amount)

        # po úprave upraceme osirelé ingrediencie
        cleanup_orphan_ingredients()
        return redirect(self.get_success_url())


class RecipeDeleteView(LoginRequiredMixin, DeleteView):
    model = Recipe
    template_name = "recipes/recipe_confirm_delete.html"
    success_url = reverse_lazy("recipes:list")

    def get_queryset(self):
        # superuser môže mazať všetko, ostatní len svoje
        if self.request.user.is_superuser:
            return Recipe.objects.all()
        return Recipe.objects.filter(created_by=self.request.user)

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        cleanup_orphan_ingredients()
        return response


class IngredientListView(ListView):
    model = Ingredient
    template_name = "recipes/ingredient_list.html"
    context_object_name = "ingredients"
    paginate_by = 30

    def get_queryset(self):
        # Zobraz aj počet použitia
        return Ingredient.objects.annotate(
            recipe_count=Count("recipeingredient")
        ).order_by("name")


class IngredientRecipeListView(ListView):
    """
    Zoznam receptov, ktoré obsahujú danú ingredienciu.
    """
    model = Recipe
    template_name = "recipes/ingredient_recipes.html"
    context_object_name = "recipes"
    paginate_by = 12

    def get_queryset(self):
        self.ingredient = get_object_or_404(Ingredient, pk=self.kwargs["pk"])
        return (
            Recipe.objects.filter(recipeingredient__ingredient=self.ingredient)
            .distinct()
            .select_related("created_by")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["ingredient"] = self.ingredient
        return ctx


class RecipeSearchView(ListView):
    model = Recipe
    template_name = "recipes/recipe_search.html"
    context_object_name = "recipes"

    def get_queryset(self):
        qs = Recipe.objects.all()
        q = (self.request.GET.get("q") or "").strip()
        ingredients = (self.request.GET.get("ingredients") or "").strip()

        if q:
            qs = qs.filter(
                Q(title__icontains=q) |
                Q(description__icontains=q) |
                Q(instructions__icontains=q)
            )

        if ingredients:
            tokens = [t.strip() for t in ingredients.split(",") if t.strip()]
            for t in tokens:
                qs = qs.filter(ingredients__name__icontains=t)

        return qs.distinct()