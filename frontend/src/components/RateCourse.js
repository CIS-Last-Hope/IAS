// src/components/RateCourse.js

import React, { useState } from 'react';
import axios from 'axios';

const RateCourse = ({ courseId }) => {
  const [rating, setRating] = useState(0);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`/api/course/${courseId}/rate`, { rating });
      console.log('Rating added successfully');
      // Очистить форму или выполнить другие действия после успешной оценки курса
    } catch (error) {
      console.error('Error adding rating:', error);
    }
  };

  return (
    <div>
      <h2>Rate Course</h2>
      <form onSubmit={handleSubmit}>
        <label>Rating (1-5):</label>
        <input type="number" min="1" max="5" value={rating} onChange={(e) => setRating(e.target.value)} required />
        <button type="submit">Rate</button>
      </form>
    </div>
  );
};

export default RateCourse;
