// src/components/SignUp.js

import React, { useState } from 'react';
import axios from 'axios';

function SignUp() {
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [qrCode, setQrCode] = useState(null);

  const handleSignUp = async (e) => {
    e.preventDefault();
    try {
      const userData = {
        email: email,
        username: username,
        password: password
      };

      const response = await axios.post('http://localhost:8000/auth/sign-up', userData);
      const session_id = response.data.session_id;
      fetchQrCode(session_id);
    } catch (error) {
      console.error(error.response?.data);
      alert('Registration failed!');
    }
  };

  const fetchQrCode = async (session_id) => {
    try {
      const response = await axios.get(`http://localhost:8000/auth/qr?session_id=${session_id}`, { responseType: 'blob' });
      const qrCodeUrl = URL.createObjectURL(response.data);
      setQrCode(qrCodeUrl);
    } catch (error) {
      console.error(error.response?.data);
      alert('Failed to fetch QR code!');
    }
  };

  return (
    <div>
      <h2>Sign Up</h2>
      {!qrCode ? (
        <form onSubmit={handleSignUp}>
          <div>
            <label>Email:</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </div>
          <div>
            <label>Username:</label>
            <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} required />
          </div>
          <div>
            <label>Password:</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </div>
          <button type="submit">Sign Up</button>
        </form>
      ) : (
        <div>
          <h3>Scan this QR code to complete registration</h3>
          {qrCode ? <img src={qrCode} alt="QR Code" /> : <p>Loading QR code...</p>}
        </div>
      )}
    </div>
  );
}

export default SignUp;
