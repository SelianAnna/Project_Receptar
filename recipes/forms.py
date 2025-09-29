from django import forms
from .models import Recipe

class RecipeForm(forms.ModelForm):
    # Polia na generovanie dynamických ingrediencií vo formulári (prázdne, JS ich dorobí)
    class Meta:
        model = Recipe
        fields = ["title", "description", "instructions", "image"]