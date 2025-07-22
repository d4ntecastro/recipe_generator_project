import React, { useState } from 'react';
import axios from 'axios';

// Accept isAuthenticated as a prop
function RecipeGenerator({ API_BASE_URL, isAuthenticated }) {
  const [ingredients, setIngredients] = useState('');
  const [dietaryPreferences, setDietaryPreferences] = useState('');
  const [cookingTime, setCookingTime] = useState('');
  const [cuisine, setCuisine] = useState('');
  const [generatedRecipes, setGeneratedRecipes] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    // Prevent submission if not authenticated
    if (!isAuthenticated) {
      setError("Please log in to generate recipes.");
      return;
    }

    setIsLoading(true);
    setError(null);
    setGeneratedRecipes([]); // Clear previous recipes

    try {
      const response = await axios.post(`${API_BASE_URL}generate-recipe/`, {
        ingredients: ingredients.trim(),
        dietary_preferences: dietaryPreferences.trim(),
        cooking_time: cookingTime ? parseInt(cookingTime) : null,
        cuisine: cuisine.trim(),
        num_recipes: 1, // You can make this configurable later
      });
      setGeneratedRecipes(response.data);
    } catch (err) {
      console.error("Error generating recipe:", err.response ? err.response.data : err.message);
      setError(err.response ? err.response.data.error || "Failed to generate recipe." : "Network error.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ marginBottom: '40px', padding: '20px', border: '1px solid #e0e0e0', borderRadius: '10px', backgroundColor: '#fdfdfd', color: '#333' }}>
      <h2 style={{ textAlign: 'center', color: '#34495e', marginBottom: '25px' }}>Generate New Recipes with AI</h2>
      <form onSubmit={handleSubmit} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', maxWidth: '800px', margin: '0 auto' }}>
        <div style={{ gridColumn: 'span 2' }}>
          <label htmlFor="ingredients" style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', color: '#333' }}>Ingredients (comma-separated):</label>
          <input
            type="text"
            id="ingredients"
            value={ingredients}
            onChange={(e) => setIngredients(e.target.value)}
            placeholder="e.g., chicken, broccoli, rice"
            style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid #ccc', color: 'white', backgroundColor: '#333' }} /* MODIFIED */
            disabled={!isAuthenticated}
          />
        </div>
        <div>
          <label htmlFor="dietary" style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', color: '#333' }}>Dietary Preferences (comma-separated):</label>
          <input
            type="text"
            id="dietary"
            value={dietaryPreferences}
            onChange={(e) => setDietaryPreferences(e.target.value)}
            placeholder="e.g., vegetarian, gluten-free"
            style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid #ccc', color: 'white', backgroundColor: '#333' }} /* MODIFIED */
            disabled={!isAuthenticated}
          />
        </div>
        <div>
          <label htmlFor="time" style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', color: '#333' }}>Cooking Time (minutes):</label>
          <input
            type="number"
            id="time"
            value={cookingTime}
            onChange={(e) => setCookingTime(e.target.value)}
            placeholder="e.g., 30"
            style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid #ccc', color: 'white', backgroundColor: '#333' }} /* MODIFIED */
            disabled={!isAuthenticated}
          />
        </div>
        <div style={{ gridColumn: 'span 2' }}>
          <label htmlFor="cuisine" style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', color: '#333' }}>Cuisine:</label>
          <input
            type="text"
            id="cuisine"
            value={cuisine}
            onChange={(e) => setCuisine(e.target.value)}
            placeholder="e.g., Italian, Mexican"
            style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid #ccc', color: 'white', backgroundColor: '#333' }} /* MODIFIED */
            disabled={!isAuthenticated}
          />
        </div>
        <button
          type="submit"
          disabled={isLoading || !isAuthenticated}
          style={{
            gridColumn: 'span 2',
            padding: '12px 20px',
            borderRadius: '8px',
            backgroundColor: (isLoading || !isAuthenticated) ? '#95a5a6' : '#2ecc71',
            color: 'white',
            border: 'none',
            cursor: (isLoading || !isAuthenticated) ? 'not-allowed' : 'pointer',
            fontSize: '1.1em',
            fontWeight: 'bold',
            transition: 'background-color 0.3s ease'
          }}
        >
          {isLoading ? 'Generating...' : (isAuthenticated ? 'Generate Recipe' : 'Log in to Generate')}
        </button>
      </form>

      {error && <p style={{ color: 'red', textAlign: 'center', marginTop: '20px' }}>Error: {error}</p>}

      {generatedRecipes.length > 0 && (
        <div style={{ marginTop: '30px', borderTop: '1px solid #eee', paddingTop: '20px', color: '#333' }}>
          <h3 style={{ color: '#34495e', fontSize: '1.4em', marginBottom: '10px' }}>Generated Recipes:</h3>
          {generatedRecipes.map((recipe, index) => (
            <div key={recipe.id || index} style={{ border: '1px solid #dcdcdc', borderRadius: '8px', padding: '20px', marginBottom: '20px', backgroundColor: '#fcfcfc', color: '#333' }}>
              <h4 style={{ color: '#2c3e50', fontSize: '1.4em', marginBottom: '10px' }}>{recipe.title}</h4>
              <p style={{color: '#333'}}><strong>Cuisine:</strong> {recipe.cuisine}</p>
              <p style={{color: '#333'}}><strong>Cooking Time:</strong> {recipe.cooking_time_minutes} minutes</p>
              <p style={{color: '#333'}}><strong>Ingredients:</strong></p>
              <ul style={{ listStyleType: 'disc', marginLeft: '20px', color: '#333' }}>
                {recipe.ingredients && recipe.ingredients.map((ing, i) => (
                  <li key={i} style={{ color: '#333' }}>{ing.quantity} {ing.ingredient_name}</li>
                ))}
              </ul>
              <p style={{color: '#333'}}><strong>Instructions:</strong></p>
              <ol style={{ listStyleType: 'decimal', marginLeft: '20px', color: '#333' }}>
                {recipe.instructions.split('\n').filter(Boolean).map((step, i) => (
                  <li key={i} style={{ color: '#333' }}>{step.trim()}</li>
                ))}
              </ol>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default RecipeGenerator;
