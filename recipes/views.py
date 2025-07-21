from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from .models import Ingredient, DietaryPreference, Recipe, RecipeIngredient, MealPlan, ShoppingListItem
from .serializers import (
    IngredientSerializer, DietaryPreferenceSerializer, RecipeSerializer,
    MealPlanSerializer, ShoppingListItemSerializer
)

# Import for Gemini API integration (will be used later)
import requests
import json
import os  # For environment variables

# --- Ingredient API Views ---


class IngredientListCreate(generics.ListCreateAPIView):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    # permission_classes = [IsAuthenticated] # Uncomment for authenticated access


class IngredientRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    # permission_classes = [IsAuthenticated] # Uncomment for authenticated access

# --- DietaryPreference API Views ---


class DietaryPreferenceListCreate(generics.ListCreateAPIView):
    queryset = DietaryPreference.objects.all()
    serializer_class = DietaryPreferenceSerializer
    # permission_classes = [IsAuthenticated]


class DietaryPreferenceRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = DietaryPreference.objects.all()
    serializer_class = DietaryPreferenceSerializer
    # permission_classes = [IsAuthenticated]

# --- Recipe API Views ---


class RecipeListCreate(generics.ListCreateAPIView):
    serializer_class = RecipeSerializer
    # Only authenticated users can list/create their recipes
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only show recipes belonging to the current authenticated user
        return Recipe.objects.filter(user=self.request.user).order_by('-id')

    def perform_create(self, serializer):
        # Automatically assign the current user to the recipe
        serializer.save(user=self.request.user)


class RecipeRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only allow users to retrieve/update/delete their own recipes
        return Recipe.objects.filter(user=self.request.user)

# --- MealPlan API Views ---


class MealPlanListCreate(generics.ListCreateAPIView):
    serializer_class = MealPlanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MealPlan.objects.filter(user=self.request.user).order_by('-start_date')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MealPlanRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MealPlanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MealPlan.objects.filter(user=self.request.user)

# --- ShoppingListItem API Views ---


class ShoppingListItemListCreate(generics.ListCreateAPIView):
    serializer_class = ShoppingListItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get items for the user's meal plans
        return ShoppingListItem.objects.filter(meal_plan__user=self.request.user)

    def perform_create(self, serializer):
        # Ensure the meal plan belongs to the current user
        meal_plan = serializer.validated_data['meal_plan']
        if meal_plan.user != self.request.user:
            raise serializers.ValidationError(
                "You can only add items to your own meal plans.")
        serializer.save()


class ShoppingListItemRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ShoppingListItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ShoppingListItem.objects.filter(meal_plan__user=self.request.user)

# --- Gemini API Integration View (for Recipe Generation) ---


class GenerateRecipeAPIView(APIView):
    # Only authenticated users can generate recipes
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        # Extract data from the request body (sent from React)
        ingredients_input = request.data.get(
            'ingredients', '')  # Comma-separated string
        dietary_preferences_input = request.data.get(
            'dietary_preferences', '')  # Comma-separated string
        cooking_time = request.data.get('cooking_time', '')
        cuisine = request.data.get('cuisine', '')
        # How many recipes to generate
        num_recipes = request.data.get('num_recipes', 1)

        # Construct the prompt for the Gemini API
        prompt = (
            f"Generate {num_recipes} unique recipe(s) in JSON format. "
            f"Each recipe should have 'title', 'instructions' (step-by-step), "
            f"'cooking_time_minutes' (integer), 'cuisine', and 'ingredients' (an array of objects, "
            f"each with 'name' and 'quantity').\n\n"
        )
        if ingredients_input:
            prompt += f"Use these main ingredients: {ingredients_input}.\n"
        if dietary_preferences_input:
            prompt += f"Adhere to these dietary preferences: {dietary_preferences_input}.\n"
        if cooking_time:
            prompt += f"Aim for a cooking time around {cooking_time} minutes.\n"
        if cuisine:
            prompt += f"Focus on {cuisine} cuisine.\n"
        prompt += "Ensure the JSON is valid and only contains the recipe data."

        try:
            # Get API key from environment variables for security
            api_key = os.environ.get("GEMINI_API_KEY", "")
            if not api_key:
                return Response(
                    {"error": "Gemini API key not configured on the server."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            chatHistory = []
            # Corrected: Use .append() for Python lists instead of .push()
            chatHistory.append({"role": "user", "parts": [{"text": prompt}]})

            # Define the schema for structured response (highly recommended for LLMs)
            response_schema = {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "title": {"type": "STRING"},
                        "instructions": {"type": "STRING"},
                        "cooking_time_minutes": {"type": "INTEGER"},
                        "cuisine": {"type": "STRING"},
                        "ingredients": {
                            "type": "ARRAY",
                            "items": {
                                "type": "OBJECT",
                                "properties": {
                                    "name": {"type": "STRING"},
                                    "quantity": {"type": "STRING"}
                                },
                                "propertyOrdering": ["name", "quantity"]
                            }
                        }
                    },
                    "propertyOrdering": [
                        "title", "instructions", "cooking_time_minutes", "cuisine", "ingredients"
                    ]
                }
            }

            payload = {
                "contents": chatHistory,
                "generationConfig": {
                    "responseMimeType": "application/json",
                    "responseSchema": response_schema
                }
            }

            api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

            headers = {'Content-Type': 'application/json'}
            response = requests.post(
                api_url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)

            result = response.json()

            generated_recipes_data = []
            if result.get('candidates') and result['candidates'][0].get('content') and result['candidates'][0]['content'].get('parts'):
                # The LLM response is a string that needs to be parsed as JSON
                json_string = result['candidates'][0]['content']['parts'][0]['text']
                generated_recipes_data = json.loads(json_string)

            saved_recipes = []
            for recipe_data in generated_recipes_data:
                # Create or get Ingredients and DietaryPreferences
                ingredients_list = []
                for ing_data in recipe_data.pop('ingredients', []):
                    ingredient, _ = Ingredient.objects.get_or_create(
                        name=ing_data['name'].lower())  # Normalize ingredient names
                    ingredients_list.append(
                        {'ingredient': ingredient, 'quantity': ing_data['quantity']})

                dietary_prefs_from_input = [
                    dp.strip() for dp in dietary_preferences_input.split(',') if dp.strip()]
                dietary_pref_objects = []
                for dp_name in dietary_prefs_from_input:
                    pref, _ = DietaryPreference.objects.get_or_create(
                        name=dp_name.capitalize())
                    dietary_pref_objects.append(pref)

                # Create the Recipe instance
                recipe_serializer = RecipeSerializer(data={
                    **recipe_data,
                    'user': user.id,  # Assign the user ID for creation
                    'generated_by_ai': True,
                })

                if recipe_serializer.is_valid():
                    recipe = recipe_serializer.save(
                        user=user)  # Save with the user object
                    # Add many-to-many ingredients
                    for ing_item in ingredients_list:
                        RecipeIngredient.objects.create(
                            recipe=recipe,
                            ingredient=ing_item['ingredient'],
                            quantity=ing_item['quantity']
                        )
                    # Add many-to-many dietary preferences
                    recipe.dietary_preferences.set(dietary_pref_objects)

                    saved_recipes.append(RecipeSerializer(recipe).data)
                else:
                    # For debugging
                    print(
                        f"Recipe validation error: {recipe_serializer.errors}")
                    # You might want to return an error here or log it more robustly
                    return Response(
                        {"error": "Failed to validate generated recipe data.",
                            "details": recipe_serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            return Response(saved_recipes, status=status.HTTP_201_CREATED)

        except requests.exceptions.RequestException as e:
            return Response(
                {"error": f"Error communicating with Gemini API: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except json.JSONDecodeError as e:
            return Response(
                {"error": f"Invalid JSON response from Gemini API: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
