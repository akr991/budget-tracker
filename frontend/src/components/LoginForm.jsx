import { useState } from 'react';
import { api, setAuthToken } from '../api/client';

export default function LoginForm({ onAuth }) {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const validateForm = () => {
    if (!email || !password) {
      setError('Email and password are required');
      return false;
    }
    if (isRegister && !fullName) {
      setError('Full name is required');
      return false;
    }
    if (password.length < 8) {
      setError('Password must be at least 8 characters');
      return false;
    }
    return true;
  };

  const submit = async (event) => {
    event.preventDefault();
    setError('');
    setLoading(true);

    if (!validateForm()) {
      setLoading(false);
      return;
    }

    try {
      const endpoint = isRegister ? '/auth/register' : '/auth/login';
      const payload = isRegister 
        ? { email, password, full_name: fullName } 
        : { email, password };
      
      console.log(`[Auth] Submitting ${isRegister ? 'register' : 'login'}:`, { email, full_name: fullName });
      
      const response = await api.post(endpoint, payload);
      
      console.log('[Auth] Response:', response.data);
      
      if (response.data.access_token) {
        setAuthToken(response.data.access_token);
        onAuth();
      } else {
        setError('No access token received from server');
      }
    } catch (err) {
      console.error('[Auth] Error:', err);
      
      let errorMessage = 'Unable to authenticate';
      
      if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      } else if (err.response?.status === 400) {
        errorMessage = 'Invalid request. Check email format and password length (min 8 chars)';
      } else if (err.response?.status === 401) {
        errorMessage = 'Invalid email or password';
      } else if (err.message === 'Network Error') {
        errorMessage = 'Cannot connect to backend. Ensure backend is running on port 8000';
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-shell">
      <div className="auth-card">
        <h1>Cloud Budget Atlas</h1>
        <p>Track India, UAE and your global net worth in one place.</p>
        <form onSubmit={submit}>
          {isRegister && (
            <label>
              Full Name
              <input 
                value={fullName} 
                onChange={(e) => setFullName(e.target.value)} 
                disabled={loading}
                required 
              />
            </label>
          )}
          <label>
            Email
            <input 
              type="email" 
              value={email} 
              onChange={(e) => setEmail(e.target.value)} 
              disabled={loading}
              required 
            />
          </label>
          <label>
            Password
            <input 
              type="password" 
              value={password} 
              onChange={(e) => setPassword(e.target.value)} 
              disabled={loading}
              required 
              placeholder="Min 8 characters"
            />
          </label>
          {error && <p className="error-text">{error}</p>}
          <button 
            type="submit" 
            className="primary-btn"
            disabled={loading}
          >
            {loading ? 'Please wait...' : (isRegister ? 'Create Account' : 'Login')}
          </button>
        </form>
        <button 
          className="ghost-btn" 
          onClick={() => { setIsRegister(!isRegister); setError(''); }} 
          type="button"
          disabled={loading}
        >
          {isRegister ? 'Already have an account? Login' : 'New user? Register'}
        </button>
      </div>
    </div>
  );
}
