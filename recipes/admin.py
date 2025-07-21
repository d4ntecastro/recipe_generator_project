from django.contrib import admin
from .models import Ingredient, DietaryPreference, Recipe, RecipeIngredient, MealPlan, ShoppingListItem

admin.site.register(Ingredient)
admin.site.register(DietaryPreference)
admin.site.register(Recipe)
admin.site.register(RecipeIngredient)
admin.site.register(MealPlan)
admin.site.register(ShoppingListItem)

# Register your models here.
