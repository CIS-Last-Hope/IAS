import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useParams, Link, useNavigate } from 'react-router-dom';
import './CourseList.css'; // Используем те же стили, что и в CourseList

// Компонент для отображения всплывающих ошибок
const ErrorNotification = ({ message, clearError }) => {
  useEffect(() => {
    if (message) {
      const timer = setTimeout(() => {
        clearError(); // Очищаем ошибку через 10 секунд
      }, 10000);
      return () => clearTimeout(timer); // Очищаем таймер при размонтировании
    }
  }, [message, clearError]);

  if (!message) return null;

  return (
    <div className="error-notification">
      {message}
    </div>
  );
};

function CourseDetails() {
  const { courseId } = useParams();
  const [course, setCourse] = useState(null);
  const [newTitle, setNewTitle] = useState('');
  const [newDescription, setNewDescription] = useState('');
  const [editMode, setEditMode] = useState(false);
  const [showUploadForm, setShowUploadForm] = useState(false);
  const [uploadFile, setUploadFile] = useState(null);
  const [lessonId, setLessonId] = useState(null);
  const [rating, setRating] = useState(null);
  const [error, setError] = useState(''); // Для всплывающих ошибок
  const [ratingSubmitted, setRatingSubmitted] = useState(false);
  const [recommendations, setRecommendations] = useState([]);
  const [currentUser, setCurrentUser] = useState(null);
  const [showRecommendations, setShowRecommendations] = useState(false); // Состояние для управления показом рекомендаций
  const [lessons, setLessons] = useState([]); // Список уроков
  const [selectedLesson, setSelectedLesson] = useState(null); // Содержимое выбранного урока
  const [lessonType, setLessonType] = useState(null); // Тип урока (image, text)
  const [lessonContent, setLessonContent] = useState(null); // Контент урока
  const navigate = useNavigate();

  // Сброс состояния рейтинга при изменении курса
  useEffect(() => {
    setRating(null); // Сбрасываем рейтинг при изменении курса
    setRatingSubmitted(false); // Сбрасываем состояние отправленного рейтинга
  }, [courseId]);

  // Сброс ошибки
  const clearError = () => {
    setError('');
  };

  // Fetch course details and current user on courseId change
  useEffect(() => {
    const fetchCourseDetails = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          setError('Token not found');
          return;
        }

        const response = await axios.get(`${process.env.REACT_APP_API_URL}/course/${courseId}?token=${token}`);
        setCourse(response.data);
      } catch (error) {
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

        const response = await axios.get(`${process.env.REACT_APP_API_URL}/auth/current-user?token=${token}`);
        setCurrentUser(response.data);
      } catch (error) {
        setError('Failed to fetch current user');
      }
    };

    fetchCourseDetails();
    fetchCurrentUser();
  }, [courseId]);

  // Сбрасываем состояние рекомендаций при смене курса
  useEffect(() => {
    setShowRecommendations(false);
    fetchLessons(); // Загружаем уроки при загрузке страницы курса
  }, [courseId]);

  // Получение уроков для текущего курса
  const fetchLessons = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${process.env.REACT_APP_API_URL}/course/${courseId}/lessons?token=${token}`);
      setLessons(response.data);
    } catch (error) {
      setError('Failed to fetch lessons');
    }
  };

  // Функция для получения следующего lessonId
const fetchNextLessonId = async () => {
  try {
    const token = localStorage.getItem('token');
    if (!token) {
      setError('Token not found');
      return;
    }

    const response = await axios.get(`${process.env.REACT_APP_API_URL}/course/${courseId}/lessons?token=${token}`);
    const lessons = response.data;

    // Определение следующего lessonId
    const nextLessonId = lessons.length > 0 ? Math.max(...lessons.map(lesson => lesson.lesson_id)) + 1 : 1;
    setLessonId(nextLessonId);
  } catch (error) {
    setError('Failed to fetch lessons');
  }
};

  // Просмотр конкретного урока
  const viewLesson = async (lessonId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${process.env.REACT_APP_API_URL}/course/lesson/${courseId}/${lessonId}?token=${token}`, {
        responseType: 'blob', // Получаем бинарные данные
      });

      const mimeType = response.headers['content-type'];
      if (mimeType.startsWith('image/')) {
        setLessonType('image');
        setLessonContent(URL.createObjectURL(response.data)); // Создаем URL для изображения
      } else if (mimeType.startsWith('text/plain')) {
        setLessonType('text');
        const reader = new FileReader();
        reader.onload = (e) => {
          setLessonContent(e.target.result); // Текстовый контент
        };
        reader.readAsText(response.data);
      } else {
        setError('Unsupported lesson content type');
      }

      setSelectedLesson(lessonId);
    } catch (error) {
      setError('Failed to view lesson');
    }
  };

  const closeLesson = () => {
    setSelectedLesson(null); // Сбрасываем выбранный урок
    setLessonType(null);
    setLessonContent(''); // Очищаем контент
  };

  const handleRecommendationClick = (recCourseId) => {
    setShowRecommendations(false); // Скрываем список рекомендаций при переходе на другой курс
    navigate(`/course/${recCourseId}`); // Переходим на страницу выбранного курса
  };

  const handleUploadClick = async () => {
    setShowUploadForm(true);
    await fetchNextLessonId(); // Получаем следующий lessonId при открытии формы
  };

  const handleUploadCancel = () => {
    setShowUploadForm(false);
    setUploadFile(null);
  };

  const handleFileChange = (event) => {
    setUploadFile(event.target.files[0]);
  };

  const handleFileUpload = async () => {
    if (!uploadFile || lessonId === null) {
      setError('No file selected or lessonId not set');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setError('Token not found');
        return;
      }

      const formData = new FormData();
      formData.append('file', uploadFile);

      await axios.post(
        `${process.env.REACT_APP_API_URL}/course/${courseId}/lesson/upload?lesson_id=${lessonId}&token=${token}`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
            Authorization: `Bearer ${token}`
          }
        }
      );

      setShowUploadForm(false);
      setUploadFile(null); // Очищаем файл после загрузки
    } catch (error) {
      setError('Failed to upload file');
    }
  };

  // Удаление курса
  const handleDeleteCourse = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setError('Token not found');
        return;
      }

      await axios.delete(`${process.env.REACT_APP_API_URL}/course/${courseId}?token=${token}`);
      navigate('/course');
    } catch (error) {
      setError('Failed to delete course');
    }
  };

  // Обновление курса
  const handleUpdateCourse = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setError('Token not found');
        return;
      }

      await axios.put(
        `${process.env.REACT_APP_API_URL}/course/${courseId}?token=${token}`,
        { title: newTitle, description: newDescription }
      );
      setCourse({ ...course, title: newTitle, description: newDescription });
      setEditMode(false);
    } catch (error) {
      setError('Failed to update course');
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
        `${process.env.REACT_APP_API_URL}/course/${courseId}/rate?token=${token}`,
        { rating: rating }
      );

      setRatingSubmitted(true);
    } catch (error) {
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

      const response = await axios.get(`${process.env.REACT_APP_API_URL}/course/${courseId}/recommendations?token=${token}`);
      setRecommendations(response.data);
      setShowRecommendations(true); // Показываем рекомендации после успешного получения
    } catch (error) {
      setError('Failed to fetch recommendations');
    }
  };

  if (!course || !currentUser) {
    return <div>Loading...</div>;
  }

  const isCreator = currentUser.id === course.creator_id;

  return (
    <div className="course-details-container">
      <h2>Course Details</h2>

      {/* Всплывающее сообщение об ошибке */}
      <ErrorNotification message={error} clearError={clearError} />

      <p><strong>Title:</strong> {course.title}</p>
      <p><strong>Description:</strong> {course.description}</p>

      <div className="creator-buttons">
        {isCreator && !editMode && (
          <div className="creator-buttons-group">
            <button onClick={() => setEditMode(!editMode)} className="course-button">Edit</button>
            <button onClick={handleDeleteCourse} className="course-button">Delete</button>
            <button onClick={handleUploadClick} className="course-button">Upload Materials</button>
          </div>
        )}

        {isCreator && editMode && (
          <div>
            <div>
              <label>New Title:</label>
              <input type="text" value={newTitle} onChange={(e) => setNewTitle(e.target.value)} required />
            </div>
            <div>
              <label>New Description:</label>
              <textarea value={newDescription} onChange={(e) => setNewDescription(e.target.value)} required />
            </div>
            <button onClick={handleUpdateCourse} className="course-button">Save</button>
          </div>
        )}
      </div>

      <div className="lessons-section">
        <h3>Lessons:</h3>
        <ul>
          {lessons.map((lesson) => (
            <li key={lesson.lesson_id}>
              <button onClick={() => viewLesson(lesson.lesson_id)} className="lesson-link">
                View Lesson {lesson.lesson_id}
              </button>
            </li>
          ))}
        </ul>
      </div>

      {selectedLesson && (
        <div>
          <h3>Lesson Details:</h3>
          {lessonType === 'image' &&
            <img src={lessonContent} alt="Lesson content" style={{ maxWidth: '100%', height: '200px' }} />}
          {lessonType === 'text' &&
            <textarea value={lessonContent} readOnly style={{ width: '100%', height: '200px' }} />}
          <button onClick={closeLesson} className="close-button">Close Lesson</button>
        </div>
      )}

      <div className="rating-section">
        <h3>Rate this course:</h3>
        {!ratingSubmitted ? (
          <div>
            <select value={rating} onChange={(e) => setRating(parseInt(e.target.value))}>
              <option value="">Select Rating</option>
              <option value={1}>1</option>
              <option value={2}>2</option>
              <option value={3}>3</option>
              <option value={4}>4</option>
              <option value={5}>5</option>
            </select>
            <button onClick={handleRateCourse} className="course-button">Submit Rating</button>
          </div>
        ) : (
          <p>Thank you for rating this course!</p>
        )}
      </div>

      {showUploadForm && (
        <div className="upload-form">
          <input type="file" onChange={handleFileChange} />
          <button onClick={handleFileUpload} className="course-button">Upload File</button>
          <button onClick={handleUploadCancel} className="course-button">Cancel</button>
        </div>
      )}

      <div className="other-buttons-group">
        <button onClick={handleGetRecommendations} className="course-button">Get Recommendations</button>
        <Link to="/course">
          <button className="course-button">Back to Courses</button>
        </Link>
      </div>

      {showRecommendations && recommendations.length > 0 && (
        <div>
          <h3>Recommended Courses:</h3>
          <ul>
            {recommendations.map((recCourse) => (
              <li key={recCourse.id}>
                <button onClick={() => handleRecommendationClick(recCourse.id)} className="recommendation-link">
                  {recCourse.title}
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default CourseDetails;