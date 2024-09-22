// src/components/SignUp.js

import React, { useState } from 'react';
import axios from 'axios';
import './SignUp.css'; // Подключаем файл стилей

function SignUp() {
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [qrCode, setQrCode] = useState(null);
  const [error, setError] = useState('');

  const handleSignUp = async (e) => {
    e.preventDefault();
    try {
      const userData = {
        email: email,
        username: username,
        password: password
      };

      const response = await axios.post('http://51.250.6.237:8000/auth/sign-up', userData);
      const session_id = response.data.session_id;
      fetchQrCode(session_id);
      setError('');
    } catch (error) {
      console.error(error.response?.data);
      setError('Registration failed!');
    }
  };

  const fetchQrCode = async (session_id) => {
    try {
      const response = await axios.get(`http://51.250.6.237:8000/auth/qr?session_id=${session_id}`, { responseType: 'blob' });
      const qrCodeUrl = URL.createObjectURL(response.data);
      setQrCode(qrCodeUrl);
    } catch (error) {
      console.error(error.response?.data);
      setError('Failed to fetch QR code!');
    }
  };

  return (
    <div className="signup-container">
      <h2>Sign Up</h2>
      {!qrCode ? (
        <form onSubmit={handleSignUp} className="signup-form">
          <div className="form-group">
            <label>Email:</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </div>
          <div className="form-group">
            <label>Username:</label>
            <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} required />
          </div>
          <div className="form-group">
            <label>Password:</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </div>
          {error && <p className="error-message">{error}</p>}
          <button type="submit" className="signup-button">Sign Up</button>
        </form>
      ) : (
        <div>
          <h3>Scan this QR code to complete registration</h3>
          {qrCode ? <img src={qrCode} alt="QR Code" className="qr-code" /> : <p>Loading QR code...</p>}
        </div>
      )}
      <p className="signin-link">
        Already have an account? <a href="/sign-in">Sign In</a>
      </p>
    </div>
  );
}

export default SignUp;
