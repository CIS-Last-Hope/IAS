// src/components/SignIn.js

import React, { useState } from 'react';
import axios from 'axios';
import VerifyOTP from './VerifyOTP';

function SignIn() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [sessionId, setSessionId] = useState('');

  const [is2FA, setIs2FA] = useState(false);

  const handleSignIn = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://localhost:8000/auth/sign-in', new URLSearchParams({
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
    <div>
      <h2>Sign In</h2>
      {!is2FA ? (
        <form onSubmit={handleSignIn}>
          <div>
            <label>Username:</label>
            <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} required />
          </div>
          <div>
            <label>Password:</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </div>
          <button type="submit">Sign In</button>
        </form>
      ) : (
        <VerifyOTP sessionId={sessionId} />
      )}
    </div>
  );
}

export default SignIn;
