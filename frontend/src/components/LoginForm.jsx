import { useState } from 'react';
import { api, setAuthToken } from '../api/client';

export default function LoginForm({ onAuth }) {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');

  const submit = async (event) => {
    event.preventDefault();
    setError('');

    try {
      const endpoint = isRegister ? '/auth/register' : '/auth/login';
      const payload = isRegister ? { email, password, full_name: fullName } : { email, password };
      const response = await api.post(endpoint, payload);
      setAuthToken(response.data.access_token);
      onAuth();
    } catch (err) {
      setError(err.response?.data?.detail || 'Unable to authenticate');
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
              <input value={fullName} onChange={(e) => setFullName(e.target.value)} required />
            </label>
          )}
          <label>
            Email
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </label>
          <label>
            Password
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </label>
          {error && <p className="error-text">{error}</p>}
          <button type="submit" className="primary-btn">{isRegister ? 'Create Account' : 'Login'}</button>
        </form>
        <button className="ghost-btn" onClick={() => setIsRegister(!isRegister)} type="button">
          {isRegister ? 'Already have an account? Login' : 'New user? Register'}
        </button>
      </div>
    </div>
  );
}
