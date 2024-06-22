import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useParams, Link } from 'react-router-dom';

function CourseDetails() {
  const { courseId } = useParams();
  const [course, setCourse] = useState(null);
  const [newTitle, setNewTitle] = useState('');
  const [newDescription, setNewDescription] = useState('');
  const [editMode, setEditMode] = useState(false);
  const [showUploadForm, setShowUploadForm] = useState(false);
  const [uploadFile, setUploadFile] = useState(null);
  const [rating, setRating] = useState(null);
  const [error, setError] = useState('');
  const [ratingSubmitted, setRatingSubmitted] = useState(false);
  const [recommendations, setRecommendations] = useState([]);
  const [currentUser, setCurrentUser] = useState(null);

  useEffect(() => {
    const fetchCourseDetails = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          setError('Token not found');
          return;
        }

        const response = await axios.get(`http://localhost:8000/course/${courseId}?token=${token}`);
        setCourse(response.data);
      } catch (error) {
        console.error('Failed to fetch course details:', error);
        setError('Failed to fetch course details');
      }
    };

    const fetchCurrentUser = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          setError('Token not found');
          return;
        }

        const response = await axios.get(`http://localhost:8000/auth/current-user?token=${token}`);
        setCurrentUser(response.data);
      } catch (error) {
        console.error('Failed to fetch current user:', error);
        setError('Failed to fetch current user');
      }
    };

    fetchCourseDetails();
    fetchCurrentUser();
  }, [courseId]);

  const handleUpdateCourse = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setError('Token not found');
        return;
      }

      await axios.put(
        `http://localhost:8000/course/${courseId}?token=${token}`,
        { title: newTitle, description: newDescription }
      );
      setCourse({ ...course, title: newTitle, description: newDescription });
      setEditMode(false);
    } catch (error) {
      console.error('Failed to update course:', error);
      setError('Failed to update course');
    }
  };

  const handleDeleteCourse = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setError('Token not found');
        return;
      }

      await axios.delete(`http://localhost:8000/course/${courseId}?token=${token}`);
      setCourse(null);
    } catch (error) {
      console.error('Failed to delete course:', error);
      setError('Failed to delete course');
    }
  };

  const handleUploadClick = () => {
    setShowUploadForm(true);
  };

  const handleUploadCancel = () => {
    setShowUploadForm(false);
    setUploadFile(null);
  };

  const handleFileChange = (event) => {
    setUploadFile(event.target.files[0]);
  };

  const handleFileUpload = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token || !uploadFile) {
        setError('Token not found or no file selected');
        return;
      }

      const formData = new FormData();
      formData.append('file', uploadFile);

      await axios.post(
        `http://localhost:8000/course/${courseId}/materials/upload?token=${token}`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      );

      setShowUploadForm(false);
      setUploadFile(null);
    } catch (error) {
      console.error('Failed to upload file:', error);
      setError('Failed to upload file');
    }
  };

  const handleDownloadMaterials = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setError('Token not found');
        return;
      }

      const response = await axios.get(`http://localhost:8000/course/${courseId}/materials/download?token=${token}`, {
        responseType: 'blob'
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `course_${courseId}_materials.zip`);
      document.body.appendChild(link);
      link.click();

      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to download materials:', error);
      setError('Failed to download materials');
    }
  };

  const handleRateCourse = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token || !rating) {
        setError('Token not found or rating not selected');
        return;
      }

      await axios.post(
        `http://localhost:8000/course/${courseId}/rate?token=${token}`,
        { rating: rating }
      );

      setRatingSubmitted(true);
    } catch (error) {
      console.error('Failed to rate course:', error);
      setError('Failed to rate course');
    }
  };

  const handleGetRecommendations = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setError('Token not found');
        return;
      }

      const response = await axios.get(`http://localhost:8000/course/${courseId}/recommendations?token=${token}`);
      setRecommendations(response.data);
    } catch (error) {
      console.error('Failed to fetch recommendations:', error);
      setError('Failed to fetch recommendations');
    }
  };

  if (!course || !currentUser) {
    return <div>Loading...</div>;
  }

  const isCreator = currentUser.id === course.creator_id;

  return (
    <div>
      <h2>Course Details</h2>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <p><strong>Title:</strong> {course.title}</p>
      <p><strong>Description:</strong> {course.description}</p>

      <div>
        {isCreator && (
          <div>
            <button onClick={() => setEditMode(!editMode)}>{editMode ? 'Cancel' : 'Edit'}</button>
            <button onClick={handleDeleteCourse}>Delete</button>
            <button onClick={handleUploadClick}>Upload Materials</button>
          </div>
        )}

        {isCreator && (
          <div>
            {editMode && (
              <div>
                <div>
                  <label>New Title:</label>
                  <input type="text" value={newTitle} onChange={(e) => setNewTitle(e.target.value)} required />
                </div>
                <div>
                  <label>New Description:</label>
                  <textarea value={newDescription} onChange={(e) => setNewDescription(e.target.value)} required />
                </div>
                <button onClick={handleUpdateCourse}>Save</button>
              </div>
            )}
          </div>
        )}

        {!editMode && !ratingSubmitted && !rating && <button onClick={() => setRating('rate')}>Rate</button>}
            {!editMode && !ratingSubmitted && rating && (
              <select value={rating} onChange={(e) => setRating(e.target.value)}>
                <option value="1">1</option>
                <option value="2">2</option>
                <option value="3">3</option>
                <option value="4">4</option>
                <option value="5">5</option>
              </select>
            )}
            {!editMode && !ratingSubmitted && rating && <button onClick={handleRateCourse}>Submit Rating</button>}
            {ratingSubmitted && <button onClick={() => setRating(null)}>Rate</button>}

        <button onClick={handleDownloadMaterials}>Download Materials</button>
        <button onClick={handleGetRecommendations}>Get Recommendations</button>
        <Link to="/course"><button>Back to Courses</button></Link>
      </div>

      {recommendations.length > 0 && (
        <div>
          <h3>Recommended Courses</h3>
          <ul>
            {recommendations.map((course) => (
              <li key={course.id}>
                <p><strong>Title:</strong> {course.title}</p>
                <p><strong>Description:</strong> {course.description}</p>
              </li>
            ))}
          </ul>
        </div>
      )}

      {showUploadForm && (
        <div>
          <input type="file" onChange={handleFileChange} />
          <button onClick={handleFileUpload}>Upload File</button>
          <button onClick={handleUploadCancel}>Cancel</button>
        </div>
      )}
    </div>
  );
}

export default CourseDetails;
