from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from .models import Recipe, Ingredient, RecipeIngredient
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

        return super().form_valid(form)

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
        self.object = form.save()

        # Pre zapisovanie ingrediencií pri úprave (prepíšeme podľa odoslaného formulára)
        # Najprv zmažeme existujúce väzby a vytvoríme nanovo
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

        return super().form_valid(form)

class RecipeDeleteView(LoginRequiredMixin, DeleteView):
    model = Recipe
    template_name = "recipes/recipe_confirm_delete.html"
    success_url = reverse_lazy("recipes:list")

    def get_queryset(self):
        # superuser môže mazať všetko, ostatní len svoje
        if self.request.user.is_superuser:
            return Recipe.objects.all()
        return Recipe.objects.filter(created_by=self.request.user)

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