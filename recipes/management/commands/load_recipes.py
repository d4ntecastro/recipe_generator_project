import csv
import json  # In case you use a JSON dataset later
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from recipes.models import Recipe, Ingredient, RecipeIngredient, DietaryPreference
import os
from django.db import transaction  # For atomic operations


class Command(BaseCommand):
    help = 'Loads recipes from a CSV file into the database.'

    def add_arguments(self, parser):
        # Add an argument to specify the CSV file path
        parser.add_argument(
            'csv_file', type=str, help='The path to the CSV file containing recipe data.')
        # Add an argument to specify the username to associate recipes with
        parser.add_argument('--user', type=str, default='admin',
                            help='Username to associate with the loaded recipes (default: admin).')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        username = options['user']

        # Find the user to associate recipes with
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(
                f'User "{username}" does not exist. Please create it first or specify an existing user.')

        self.stdout.write(self.style.SUCCESS(
            f'Starting to load recipes from {csv_file_path} for user: {user.username}'))

        if not os.path.exists(csv_file_path):
            raise CommandError(f'File "{csv_file_path}" does not exist.')

        # Use a transaction to ensure atomicity: if any part fails, rollback everything
        with transaction.atomic():
            try:
                with open(csv_file_path, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    # --- IMPORTANT: Adjusted column names based on your provided headers ---

                    for row_num, row in enumerate(reader, 1):
                        self.stdout.write(self.style.NOTICE(
                            f'Processing row {row_num}: {row.get("recipe_name", "N/A")}'))

                        # Extract data from the row, providing defaults or handling missing keys
                        # Mapping provided CSV headers to Recipe model fields
                        title = row.get(
                            'recipe_name', f'Untitled Recipe {row_num}')
                        instructions = row.get(
                            'directions', 'No instructions provided.')

                        # Try to get total_time, then cook_time, then prep_time for cooking_time_minutes
                        cooking_time_str = row.get('total_time') or row.get(
                            'cook_time') or row.get('prep_time')
                        cooking_time_minutes = None
                        if cooking_time_str:
                            try:
                                # Attempt to extract numerical part, assuming format like "30 min" or "1 hour"
                                if 'min' in cooking_time_str:
                                    cooking_time_minutes = int(
                                        cooking_time_str.split('min')[0].strip())
                                elif 'hour' in cooking_time_str:
                                    cooking_time_minutes = int(
                                        cooking_time_str.split('hour')[0].strip()) * 60
                                else:
                                    cooking_time_minutes = int(
                                        cooking_time_str.strip())
                            except ValueError:
                                cooking_time_minutes = None  # Handle non-integer or unparseable values

                        cuisine = row.get('cuisine_path', '').split(
                            '/')[-1].replace('-', ' ').title()  # Extract last part, format
                        # Using 'nutrition' for dietary preferences, adjust if needed
                        dietary_preferences_str = row.get('nutrition', '')
                        ingredients_str = row.get('ingredients', '')

                        # Create the Recipe instance
                        recipe = Recipe.objects.create(
                            user=user,
                            title=title,
                            instructions=instructions,
                            cooking_time_minutes=cooking_time_minutes,
                            cuisine=cuisine,
                            generated_by_ai=False,  # These are loaded, not AI-generated
                        )

                        # Process Ingredients
                        if ingredients_str:
                            ingredient_items = [
                                item.strip() for item in ingredients_str.split(',') if item.strip()]
                            # Keep track of ingredients already added for this recipe
                            processed_ingredient_names = set()

                            for item_str in ingredient_items:
                                parts = item_str.split(' ', 1)
                                if len(parts) > 1 and (parts[0].replace('.', '', 1).isdigit() or '/' in parts[0]):
                                    quantity = parts[0]
                                    ing_name = parts[1].strip()
                                else:
                                    quantity = "some"
                                    ing_name = item_str.strip()

                                if ing_name:
                                    normalized_ing_name = ing_name.lower()  # Normalize for uniqueness check
                                    if normalized_ing_name not in processed_ingredient_names:
                                        ingredient, created = Ingredient.objects.get_or_create(
                                            name=normalized_ing_name)
                                        RecipeIngredient.objects.create(
                                            recipe=recipe,
                                            ingredient=ingredient,
                                            quantity=quantity
                                        )
                                        processed_ingredient_names.add(
                                            normalized_ing_name)  # Add to set

                        # Process Dietary Preferences
                        if dietary_preferences_str:
                            dietary_pref_names = [
                                name.strip() for name in dietary_preferences_str.split(',') if name.strip()]
                            for dp_name in dietary_pref_names:
                                if dp_name:
                                    dietary_pref, created = DietaryPreference.objects.get_or_create(
                                        name=dp_name.capitalize())
                                    recipe.dietary_preferences.add(
                                        dietary_pref)

                self.stdout.write(self.style.SUCCESS(
                    'Successfully loaded recipes!'))

            except FileNotFoundError:
                raise CommandError(
                    f'The file "{csv_file_path}" was not found.')
            except Exception as e:
                # Rollback transaction on any error
                self.stdout.write(self.style.ERROR(
                    f'An error occurred during loading: {e}'))
                raise CommandError(f'Failed to load recipes: {e}')
