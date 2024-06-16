// src/components/Home.js

import React from 'react';
import { Link } from 'react-router-dom';

function Home() {
  return (
    <div>
      <h1>Home Page</h1>
      <ul>
        <li><Link to="/courses">View Courses</Link></li>
        <li><Link to="/create-course">Create Course</Link></li>
      </ul>
    </div>
  );
}

export default Home;
