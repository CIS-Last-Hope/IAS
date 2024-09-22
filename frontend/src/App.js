import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Auth from './components/Auth';
import CourseList from './components/CourseList';
import CourseDetails from './components/CourseDetails';
import CreateCourse from './components/CreateCourse';
import AdminPanel from './components/AdminPanel.js';
import AdminLogin from './components/AdminLogin.js';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/admin" element={<AdminLogin />}  />
        <Route path="/admin/sign-in" element={<AdminLogin />}  />
        <Route path="/admin-panel" element={<AdminPanel />} />
        <Route path="/*" element={<Auth />} />
        <Route path="/" element={<Navigate to="/sign-in" />} />
        <Route path="/course" element={<CourseList />} />
        <Route path="/course/:courseId" element={<CourseDetails />} />
        <Route path="/create-course" element={<CreateCourse />} />
        {/* Add other routes as needed */}
      </Routes>
    </Router>
  );
}

export default App;
