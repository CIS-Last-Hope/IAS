// src/components/VerifyOTP.js

import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom'; // Импортируем useNavigate для навигации

function VerifyOTP({ sessionId }) {
  const [otpCode, setOtpCode] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate(); // Получаем функцию navigate для перехода между страницами

  const handleVerifyOTP = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`http://localhost:8000/auth/verify-otp?session_id=${sessionId}&otp_code=${otpCode}`);
      const token = response.data.access_token; // Предположим, что сервер возвращает токен после успешной аутентификации
      if (token) {
        localStorage.setItem('token', token); // Сохраняем токен в локальное хранилище
      }
      alert('Authentication successful!');
      navigate('/course'); // Используем navigate для перехода на страницу с курсами
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
