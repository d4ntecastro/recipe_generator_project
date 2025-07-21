from rest_framework import serializers
from .models import Ingredient, DietaryPreference, Recipe, RecipeIngredient, MealPlan, ShoppingListItem, User

# Serializer for the User model (often used for linking to recipes/plans)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

# Serializer for Ingredient


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'  # Include all fields

# Serializer for DietaryPreference


class DietaryPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DietaryPreference
        fields = '__all__'

# Serializer for RecipeIngredient (the "through" model for ManyToMany)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient_name = serializers.ReadOnlyField(
        source='ingredient.name')  # Display ingredient name
    ingredient_id = serializers.ReadOnlyField(
        source='ingredient.id')  # Display ingredient ID

    class Meta:
        model = RecipeIngredient
        fields = ['ingredient_id', 'ingredient_name', 'quantity']

# Serializer for Recipe


class RecipeSerializer(serializers.ModelSerializer):
    # Nested serializer to include user details
    user = UserSerializer(read_only=True)
    # Nested serializer to include ingredients with quantities
    ingredients = RecipeIngredientSerializer(
        source='recipeingredient_set', many=True, read_only=True)
    # Display dietary preference names
    dietary_preferences = serializers.StringRelatedField(
        many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = [
            'id', 'user', 'title', 'instructions', 'cooking_time_minutes',
            'cuisine', 'dietary_preferences', 'generated_by_ai', 'ingredients'
        ]
        # User and AI status set by backend
        read_only_fields = ['user', 'generated_by_ai']

    # Custom create method to handle nested RecipeIngredient data if needed for POST
    # For AI generation, we'll handle ingredients separately in the view.
    def create(self, validated_data):
        # If you were allowing users to manually create recipes with ingredients,
        # you'd handle the nested 'ingredients' data here.
        # For this project, AI will generate and the view will populate ingredients.
        return Recipe.objects.create(**validated_data)

# Serializer for MealPlan


class MealPlanSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    # Nested serializer to display recipes within the meal plan
    recipes = RecipeSerializer(many=True, read_only=True)

    class Meta:
        model = MealPlan
        fields = '__all__'
        read_only_fields = ['user']

# Serializer for ShoppingListItem


class ShoppingListItemSerializer(serializers.ModelSerializer):
    ingredient_name = serializers.ReadOnlyField(
        source='ingredient.name')

    class Meta:
        model = ShoppingListItem
        fields = '__all__'
