import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './AdminLogin.css'; // Подключаем новый CSS-файл

function AdminLogin() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const params = new URLSearchParams();
      params.append('username', username);
      params.append('password', password);

      const response = await axios.post(
        'http://localhost:8000/admin/sign-in/',
        params,
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          }
        }
      );

      // Сохраняем токен в localStorage
      localStorage.setItem('token', response.data.access_token);
      console.log("TOKEN: ", response.data.access_token);

      // Перенаправляем в админ-панель
      navigate('/admin-panel');
    } catch (error) {
      if (error.response && error.response.status === 422) {
        setError('Invalid login credentials');
      } else {
        setError('Failed to login. Please try again later.');
      }
    }
  };

  return (
    <div className="adminlogin-container">
      <div className="form-container">
        <h2>Admin Login</h2>
        {error && <p className="error">{error}</p>}
        <form onSubmit={handleLogin} className="adminlogin-form">
          <div className="form-group">
            <label>Username:</label>
            <input
              type="text"
              placeholder="Enter username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label>Password:</label>
            <input
              type="password"
              placeholder="Enter password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <button type="submit" className="adminlogin-button">Login</button>
        </form>
      </div>
    </div>
  );
}

export default AdminLogin;