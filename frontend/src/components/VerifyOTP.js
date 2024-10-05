// src/components/VerifyOTP.js

import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './VerifyOTP.css'; // Подключаем файл стилей

function VerifyOTP({ sessionId }) {
  const [otpCode, setOtpCode] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleVerifyOTP = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${process.env.REACT_APP_API_URL}/auth/verify-otp?session_id=${sessionId}&otp_code=${otpCode}`);
      const token = response.data.access_token;
      if (token) {
        localStorage.setItem('token', token);
      }
      alert('Authentication successful!');
      navigate('/course');
    } catch (error) {
      console.error(error.response?.data);
      setError('Verification failed! Please check your OTP code.');
    }
  };

  return (
    <div className="verifyotp-container">
      <h2>Verify OTP</h2>
      <form onSubmit={handleVerifyOTP} className="verifyotp-form">
        {error && <p className="error-message">{error}</p>}
        <div className="form-group">
          <label>OTP Code:</label>
          <input type="text" value={otpCode} onChange={(e) => setOtpCode(e.target.value)} required />
        </div>
        <button type="submit" className="verifyotp-button">Verify OTP</button>
      </form>
    </div>
  );
}

export default VerifyOTP;
