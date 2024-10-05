// src/components/SignIn.js

import React, { useState } from 'react';
import axios from 'axios';
import VerifyOTP from './VerifyOTP';
import { Link } from 'react-router-dom';
import './SignIn.css'; // Подключаем файл стилей

function SignIn() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [sessionId, setSessionId] = useState('');
  const [is2FA, setIs2FA] = useState(false);

  const handleSignIn = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${process.env.REACT_APP_API_URL}/auth/sign-in`, new URLSearchParams({
        username,
        password
      }));
      setSessionId(response.data.session_id || '');
      setIs2FA(true);
    } catch (error) {
      console.error(error.response?.data);
      alert('Sign in failed!');
    }
  };

  return (
    <div className="signin-container">
      {!is2FA ? (
        <div className="form-container">
          <h2>Sign In</h2>
          <form onSubmit={handleSignIn} className="signin-form">
            <div className="form-group">
              <label>Username:</label>
              <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} required />
            </div>
            <div className="form-group">
              <label>Password:</label>
              <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
            </div>
            <button type="submit" className="signin-button">Sign In</button>
          </form>
          <p>Don't have an account? <Link to="/sign-up">Sign Up</Link></p>
        </div>
      ) : (
        <VerifyOTP sessionId={sessionId} />
      )}
    </div>
  );
}

export default SignIn;
