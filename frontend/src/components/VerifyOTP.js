// src/components/VerifyOTP.js

import React, { useState } from 'react';
import axios from 'axios';

function VerifyOTP({ sessionId }) {
  const [otpCode, setOtpCode] = useState('');
  const [error, setError] = useState('');

  const handleVerifyOTP = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`http://localhost:8000/auth/verify-otp?session_id=${sessionId}&otp_code=${otpCode}`);
      alert('Authentication successful!');
      // Possible: Save token or perform other actions after authentication
    } catch (error) {
      console.error(error.response?.data);
      setError('Verification failed! Please check your OTP code.');
    }
  };

  return (
    <div>
      <h2>Verify OTP</h2>
      <form onSubmit={handleVerifyOTP}>
        {error && <p style={{ color: 'red' }}>{error}</p>}
        <div>
          <label>OTP Code:</label>
          <input type="text" value={otpCode} onChange={(e) => setOtpCode(e.target.value)} required />
        </div>
        <button type="submit">Verify OTP</button>
      </form>
    </div>
  );
}

export default VerifyOTP;
