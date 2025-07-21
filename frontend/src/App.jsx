import React, { useState, useEffect } from 'react'; // <--- CORRECTED LINE HERE
import axios from 'axios';
import RecipeGenerator from './components/RecipeGenerator';
import RecipeList from './components/RecipeList';

// Base URL for your Django API
// IMPORTANT: Change this to your deployed PythonAnywhere domain's API endpoint, using HTTPS
const API_BASE_URL = 'https://dantecastro.pythonanywhere.com/api/';

// Configure Axios for CSRF token
axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFToken';
// Important: Ensure credentials are sent with cross-origin requests
axios.defaults.withCredentials = true;

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [token, setToken] = useState(localStorage.getItem('authToken') || '');

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Token ${token}`;
      setIsAuthenticated(true);
      console.log("Axios Authorization header set:", axios.defaults.headers.common['Authorization']);
    } else {
      delete axios.defaults.headers.common['Authorization'];
      setIsAuthenticated(false);
      console.log("Axios Authorization header cleared.");
    }
  }, [token]);

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      // Your actual token from drf_create_token
      const dummyToken = '842dec06a8c2aa4a76790d99e3a8db8dea0c787a';
      setToken(dummyToken);
      localStorage.setItem('authToken', dummyToken);
      alert('Logged in with dummy token! You can now generate recipes.');
    } catch (error) {
      console.error("Login error:", error);
      alert("Login failed. Check console for details.");
    }
  };

  const handleLogout = () => {
    setToken('');
    localStorage.removeItem('authToken');
    setIsAuthenticated(false);
    alert('Logged out.');
  };

  return (
    <div style={{ fontFamily: 'Inter, sans-serif', maxWidth: '1200px', margin: '0 auto', padding: '20px', borderRadius: '12px', boxShadow: '0 4px 12px rgba(0,0,0,0.08)', backgroundColor: '#fff', color: '#333' }}>
      <h1 style={{ textAlign: 'center', color: '#2c3e50' }}>AI Recipe Generator</h1>

      {!isAuthenticated ? (
        <div style={{ textAlign: 'center', marginBottom: '30px', padding: '20px', border: '1px solid #ddd', borderRadius: '8px', backgroundColor: '#f9f9f9', color: '#333' }}>
          <h2 style={{ color: '#34495e' }}>Login to Generate Recipes</h2>
          <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '10px', maxWidth: '300px', margin: '0 auto' }}>
            <input
              type="text"
              placeholder="Username (e.g., your_admin_user)"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              style={{ padding: '10px', borderRadius: '5px', border: '1px solid #ccc', color: '#333' }}
            />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{ padding: '10px', borderRadius: '5px', border: '1px solid #ccc', color: '#333' }}
            />
            <button type="submit" style={{ padding: '10px 15px', borderRadius: '8px', backgroundColor: '#3498db', color: 'white', border: 'none', cursor: 'pointer' }}>Login (or use dummy token)</button>
          </form>
          <p style={{ marginTop: '15px', fontSize: '0.9em', color: '#666' }}>
                For development, you can manually get a token from Django admin and paste it into the `dummyToken` variable in `App.jsx` for quick testing.
                A proper login system would involve a DRF authentication endpoint.
          </p>
        </div>
      ) : (
        <div style={{color: '#333'}}>
          <div style={{ textAlign: 'right', marginBottom: '20px' }}>
            <button onClick={handleLogout} style={{ padding: '8px 15px', borderRadius: '8px', backgroundColor: '#e74c3c', color: 'white', border: 'none', cursor: 'pointer' }}>Logout</button>
          </div>
          <RecipeGenerator API_BASE_URL={API_BASE_URL} isAuthenticated={isAuthenticated} />
          <hr style={{ margin: '40px 0', borderTop: '1px solid #eee' }} />
          <RecipeList API_BASE_URL={API_BASE_URL} isAuthenticated={isAuthenticated} />
        </div>
      )}
    </div>
  );
}

export default App;
