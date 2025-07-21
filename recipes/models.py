from django.db import models
# For linking recipes/plans to users
from django.contrib.auth.models import User


class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class DietaryPreference(models.Model):
    # e.g., "Vegetarian", "Gluten-Free"
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes')
    title = models.CharField(max_length=255)
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient')
    instructions = models.TextField()
    cooking_time_minutes = models.IntegerField(blank=True, null=True)
    cuisine = models.CharField(max_length=100, blank=True, null=True)
    dietary_preferences = models.ManyToManyField(DietaryPreference, blank=True)
    generated_by_ai = models.BooleanField(
        default=False)  # To track if AI generated

    def __str__(self):
        return self.title


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.CharField(max_length=100)  # e.g., "2 cups", "1 large"

    class Meta:
        # An ingredient can only be listed once per recipe
        unique_together = ('recipe', 'ingredient')

    def __str__(self):
        return f"{self.quantity} {self.ingredient.name} in {self.recipe.title}"


class MealPlan(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='meal_plans')
    name = models.CharField(max_length=255, default="My Meal Plan")
    start_date = models.DateField()
    end_date = models.DateField()
    # Recipes included in this plan
    recipes = models.ManyToManyField(Recipe, blank=True)

    def __str__(self):
        return f"{self.name} for {self.user.username} ({self.start_date} to {self.end_date})"


class ShoppingListItem(models.Model):
    meal_plan = models.ForeignKey(
        MealPlan, on_delete=models.CASCADE, related_name='shopping_list_items')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.CharField(max_length=100)
    is_checked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quantity} {self.ingredient.name} for {self.meal_plan.name}"


# Create your models here.
