// src/components/Auth.js

import React from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import SignUp from './SignUp';
import SignIn from './SignIn';

function Auth() {
  return (
    <div>
      <nav>
        <ul>
          <li>
            <Link to="/sign-up">Sign Up</Link>
          </li>
          <li>
            <Link to="/sign-in">Sign In</Link>
          </li>
        </ul>
      </nav>

      <Routes>
        <Route path="/sign-up" element={<SignUp />} />
        <Route path="/sign-in" element={<SignIn />} />
      </Routes>
    </div>
  );
}

export default Auth;
