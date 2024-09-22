import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import './CourseList.css'; // Импорт стилей

function CourseList() {
  const [courses, setCourses] = useState([]);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchCourses = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
        setError('Token not found');
        return;
      }

      try {
        const response = await axios.get(`http://51.250.6.237:8000/course/?token=${token}`);
        setCourses(response.data);
      } catch (error) {
        console.error(error.response?.data);
        setError('Failed to fetch courses');
      }
    };

    fetchCourses();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/sign-in');
  };

  return (
    <div className="course-list-container">
      <div className="course-header">
        <h2>All Courses</h2>
      </div>
      {error && <p className="course-error">{error}</p>}
      <div className="course-cards">
        {courses.map(course => (
          <div key={course.id} className="course-card">
            <h3 className="course-title">{course.title}</h3>
            <p className="course-description">{course.description}</p>
            <Link to={`/course/${course.id}`} className="course-link">View Details</Link>
          </div>
        ))}
      </div>
      <div className="course-footer">
        <button onClick={handleLogout} className="course-logout-button">Logout</button>
        <Link to="/create-course" className="course-button">Create Course</Link>
      </div>
    </div>
  );
}

export default CourseList;