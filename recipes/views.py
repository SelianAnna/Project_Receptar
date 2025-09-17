from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Recipe, Ingredient

def home(request):
    return render(request, 'recipes/home.html')

def about(request):
    return render(request, 'recipes/about.html')

def recipe_list(request):
    query = request.GET.get('q')
    if query:
        recipes = Recipe.objects.filter(ingredients__name__icontains=query).distinct()
    else:
        recipes = Recipe.objects.all()
    return render(request, 'recipes/recipe_list.html', {'recipes': recipes})

@login_required
def add_recipe(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        ingredient_names = request.POST.get('ingredients').split(',')
        recipe = Recipe.objects.create(title=title, description=description, created_by=request.user)
        for name in ingredient_names:
            ingredient, created = Ingredient.objects.get_or_create(name=name.strip())
            recipe.ingredients.add(ingredient)
        return redirect('recipe_list')
    return render(request, 'recipes/add_recipe.html')

