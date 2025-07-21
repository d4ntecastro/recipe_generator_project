from django.urls import path
from . import views

urlpatterns = [
    # API Endpoints for Ingredients
    path('ingredients/', views.IngredientListCreate.as_view(),
         name='ingredient-list-create'),
    path('ingredients/<int:pk>/',
         views.IngredientRetrieveUpdateDestroy.as_view(), name='ingredient-detail'),

    # API Endpoints for Dietary Preferences
    path('dietary-preferences/', views.DietaryPreferenceListCreate.as_view(),
         name='dietary-preference-list-create'),
    path('dietary-preferences/<int:pk>/',
         views.DietaryPreferenceRetrieveUpdateDestroy.as_view(), name='dietary-preference-detail'),

    # API Endpoints for Recipes
    path('recipes/', views.RecipeListCreate.as_view(),
         name='recipe-list-create'),
    path('recipes/<int:pk>/',
         views.RecipeRetrieveUpdateDestroy.as_view(), name='recipe-detail'),

    # API Endpoints for Meal Plans
    path('meal-plans/', views.MealPlanListCreate.as_view(),
         name='meal-plan-list-create'),
    path('meal-plans/<int:pk>/',
         views.MealPlanRetrieveUpdateDestroy.as_view(), name='meal-plan-detail'),

    # API Endpoints for Shopping List Items
    path('shopping-list-items/', views.ShoppingListItemListCreate.as_view(),
         name='shopping-list-item-list-create'),
    path('shopping-list-items/<int:pk>/',
         views.ShoppingListItemRetrieveUpdateDestroy.as_view(), name='shopping-list-item-detail'),

    # API Endpoint for Gemini Recipe Generation
    path('generate-recipe/', views.GenerateRecipeAPIView.as_view(),
         name='generate-recipe'),
]
