import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './CreateCourse.css'; // Importing styles

function CreateCourse() {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    const token = localStorage.getItem('token');
    if (!token) {
      setError('Token not found');
      return;
    }

    try {
      const response = await axios.post(`${process.env.REACT_APP_API_URL}/course/create?token=${token}`,
        { title, description }
      );
      navigate('/course');
    } catch (error) {
      console.error(error.response?.data);
      setError('Failed to create course');
    }
  };

  const handleCancel = () => {
    navigate('/course');
  };

  return (
    <div className="create-course-container">
      <h2>Create Course</h2>
      {error && <p className="create-course-error">{error}</p>}
      <form onSubmit={handleSubmit} className="create-course-form">
        <div className="form-group">
          <label>Title:</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
            className="form-control"
          />
        </div>
        <div className="form-group">
          <label>Description:</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            required
            className="form-control"
          />
        </div>
        <div className="button-group">
          <button type="submit" className="create-course-button">Create</button>
          <button type="button" onClick={handleCancel} className="cancel-button">Cancel</button>
        </div>
      </form>
    </div>
  );
}

export default CreateCourse;
