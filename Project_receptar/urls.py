from django.contrib import admin
from django.urls import path, include
from recipes import views as recipe_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Home & About
    path('', recipe_views.home, name='home'),
    path('about/', recipe_views.about, name='about'),

    # Recipes app
    path('recipes/', include('recipes.urls')),

    # Login/Logout
    path('accounts/', include('django.contrib.auth.urls')),
]
