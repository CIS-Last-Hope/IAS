// src/components/RecommendedCourses.js

import React, { useState, useEffect } from 'react';
import axios from 'axios';

const RecommendedCourses = ({ courseId }) => {
  const [recommendedCourses, setRecommendedCourses] = useState([]);

  useEffect(() => {
    const fetchRecommendedCourses = async () => {
      try {
        const response = await axios.get(`/api/course/${courseId}/recommendations`);
        setRecommendedCourses(response.data);
      } catch (error) {
        console.error('Error fetching recommended courses:', error);
      }
    };
    fetchRecommendedCourses();
  }, [courseId]);

  return (
    <div>
      <h2>Recommended Courses</h2>
      <ul>
        {recommendedCourses.map(course => (
          <li key={course.id}>{course.title}</li>
        ))}
      </ul>
    </div>
  );
};

export default RecommendedCourses;
