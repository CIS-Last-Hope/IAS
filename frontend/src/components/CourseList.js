import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

function CourseList() {
  const [courses, setCourses] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchCourses = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
        setError('Token not found');
        return;
      }

      try {
        const response = await axios.get(`http://localhost:8000/course/?token=${token}`);
        setCourses(response.data);
      } catch (error) {
        console.error(error.response?.data);
        setError('Failed to fetch courses');
      }
    };

    fetchCourses();
  }, []);

  return (
    <div>
      <h2>All Courses</h2>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <button>
        <Link to="/create-course">Create Course</Link>
      </button>
      <ul>
        {courses.map(course => (
          <li key={course.id}>
            <Link to={`/course/${course.id}`}>{course.title}</Link>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default CourseList;
