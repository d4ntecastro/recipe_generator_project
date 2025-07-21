import React, { useState, useEffect } from 'react';
import axios from 'axios';

// Accept isAuthenticated as a prop
function RecipeList({ API_BASE_URL, isAuthenticated }) {
  const [recipes, setRecipes] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchRecipes = async () => {
      setIsLoading(true); // Set loading true before fetch
      setError(null);    // Clear previous errors
      try {
        const response = await axios.get(`${API_BASE_URL}recipes/`);
        setRecipes(response.data);
      } catch (err) {
        console.error("Error fetching recipes:", err.response ? err.response.data : err.message);
        setError("Failed to load recipes.");
      } finally {
        setIsLoading(false);
      }
    };

    // Only fetch if isAuthenticated is true
    if (isAuthenticated) {
        fetchRecipes();
    } else {
        // If not authenticated, set loading to false and clear recipes
        setIsLoading(false);
        setRecipes([]);
        setError("Please log in to view recipes."); // Inform user
    }
  }, [API_BASE_URL, isAuthenticated]); // Re-run effect when isAuthenticated changes

  if (isLoading) {
    return <p style={{ textAlign: 'center', color: '#333' }}>Loading your saved recipes...</p>; {/* Added color: '#333' */}
  }

  if (error) {
    return <p style={{ color: 'red', textAlign: 'center' }}>Error: {error}</p>;
  }

  return (
    <div style={{ padding: '20px', border: '1px solid #e0e0e0', borderRadius: '10px', backgroundColor: '#fdfdfd', color: '#333' }}> {/* Added color: '#333' */}
      <h2 style={{ textAlign: 'center', color: '#34495e', marginBottom: '25px' }}>Your Saved Recipes</h2>
      {recipes.length === 0 ? (
        <p style={{ textAlign: 'center', color: '#666' }}>No recipes saved yet. Generate some above!</p>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '25px' }}>
          {recipes.map((recipe) => (
            <div key={recipe.id} style={{ border: '1px solid #dcdcdc', borderRadius: '8px', padding: '20px', marginBottom: '20px', backgroundColor: '#fcfcfc', boxShadow: '0 2px 5px rgba(0,0,0,0.05)', color: '#333' }}> {/* Added color: '#333' */}
              <h4 style={{ color: '#2c3e50', fontSize: '1.3em', marginBottom: '10px' }}>{recipe.title}</h4>
              <p style={{ fontSize: '0.9em', color: '#333' }}><strong>Cuisine:</strong> {recipe.cuisine}</p> {/* Added color: '#333' */}
              <p style={{ fontSize: '0.9em', color: '#333' }}><strong>Time:</strong> {recipe.cooking_time_minutes} min</p> {/* Added color: '#333' */}
              <p style={{ fontSize: '0.9em', color: '#333' }}><strong>Ingredients:</strong></p> {/* Added color: '#333' */}
              <ul style={{ listStyleType: 'disc', marginLeft: '20px', fontSize: '0.9em', color: '#333' }}>
                {recipe.ingredients && recipe.ingredients.map((ing, i) => (
                  <li key={i} style={{ color: '#333' }}>{ing.quantity} {ing.ingredient_name}</li>
                ))}
              </ul>
              <p style={{ fontSize: '0.9em', color: '#333' }}><strong>Instructions:</strong> {recipe.instructions.substring(0, 100)}...</p> {/* Added color: '#333' */}
              {/* You can add a "View Full Recipe" button here */}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default RecipeList;
