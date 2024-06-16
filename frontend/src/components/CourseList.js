// src/components/CourseList.js

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

function CourseList() {
  const [courses, setCourses] = useState([]);

  useEffect(() => {
    const fetchCourses = async () => {
      const response = await axios.get('/api/course');
      setCourses(response.data);
    };

    fetchCourses();
  }, []);

  return (
    <div>
      <h2>Courses</h2>
      <ul>
        {courses.map(course => (
          <li key={course.id}>
            {course.title} - {course.description}
            <ul>
              <li><Link to={`/courses/${course.id}/upload`}>Upload Materials</Link></li>
              <li><Link to={`/courses/${course.id}/update`}>Update Course</Link></li>
              <li><Link to={`/courses/${course.id}/rate`}>Rate Course</Link></li>
              <li><Link to={`/courses/${course.id}/recommendations`}>Recommended Courses</Link></li>
            </ul>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default CourseList;
