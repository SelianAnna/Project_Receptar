from django import forms
from .models import Recipe, Ingredient, RecipeIngredient

class RecipeForm(forms.ModelForm):
    ingredient_names = forms.CharField(
        help_text="Zadajte ingrediencie oddelené čiarkou (napr. cukor, múka, vajcia)",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "cukor, múka, vajcia", "class": "form-control"})
    )

    class Meta:
        model = Recipe
        fields = ["title", "description", "instructions", "image", "ingredient_names"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "instructions": forms.Textarea(attrs={"class": "form-control", "rows": 8}),
        }

    def save(self, commit=True, user=None):
        recipe = super().save(commit=False)
        if user is not None and not recipe.pk:
            recipe.created_by = user
        if commit:
            recipe.save()

        names = self.cleaned_data.get("ingredient_names", "")
        if names:
            for raw in [n.strip() for n in names.split(",") if n.strip()]:
                ing = Ingredient.objects.filter(name__iexact=raw).first()
                if not ing:
                    ing = Ingredient.objects.create(name=raw)
                RecipeIngredient.objects.get_or_create(recipe=recipe, ingredient=ing)

        return recipe