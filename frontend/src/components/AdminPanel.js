import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './AdminPanel.css'; // Импортируем стили

function AdminPanel() {
  const [courses, setCourses] = useState([]);
  const [lessons, setLessons] = useState([]); // Список уроков
  const [newCourseTitle, setNewCourseTitle] = useState('');
  const [newCourseDescription, setNewCourseDescription] = useState('');
  const [selectedCourseId, setSelectedCourseId] = useState(null); // ID выбранного курса
  const [updatedCourseTitle, setUpdatedCourseTitle] = useState(''); // Для обновления курса
  const [updatedCourseDescription, setUpdatedCourseDescription] = useState(''); // Для обновления курса
  const [file, setFile] = useState(null); // Для загрузки файла
  const [nextLessonId, setNextLessonId] = useState(null); // Для хранения следующего lessonId
  const [error, setError] = useState('');

  useEffect(() => {
    fetchCourses();
  }, []);

  const fetchCourses = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://51.250.6.237:8000/admin/admin/course/', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      setCourses(response.data);
    } catch (error) {
      setError('Failed to fetch courses');
      console.error(error);
    }
  };

  const fetchLessons = async (courseId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`http://51.250.6.237:8000/admin/admin/${courseId}/lessons/`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      setLessons(response.data);
    } catch (error) {
      setError('Failed to fetch lessons');
      console.error(error);
    }
  };

  const fetchNextLessonId = async (courseId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`http://51.250.6.237:8000/admin/admin/${courseId}/lessons`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      const lessons = response.data;
      const nextId = lessons.length > 0 ? Math.max(...lessons.map(lesson => lesson.lesson_id)) + 1 : 1;
      setNextLessonId(nextId);
    } catch (error) {
      setError('Failed to fetch next lesson ID');
      console.error(error);
    }
  };

  const handleCreateCourse = async () => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `http://51.250.6.237:8000/admin/admin/course/create`,
        { title: newCourseTitle, description: newCourseDescription },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      fetchCourses();
      setNewCourseTitle('');
      setNewCourseDescription('');
    } catch (error) {
      setError('Failed to create course');
      console.error(error);
    }
  };

  const handleDeleteCourse = async (courseTitle) => {
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`http://51.250.6.237:8000/admin/admin/course/delete/?title=${courseTitle}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
        data: { title: courseTitle },
      });
      fetchCourses();
    } catch (error) {
      setError('Failed to delete course');
      console.error(error);
    }
  };

  const handleDeleteLesson = async (courseId, lessonId) => {
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`http://51.250.6.237:8000/admin/admin/lesson/delete/?course_id=${courseId}&lesson_id=${lessonId}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      // Обновляем список уроков после удаления
      fetchLessons(selectedCourseId);
    } catch (error) {
      setError('Failed to delete lesson');
      console.error(error);
    }
  };

  const handleToggleDetails = async (courseId) => {
    if (selectedCourseId === courseId) {
      setSelectedCourseId(null);
      setLessons([]); // Очищаем список уроков при закрытии деталей курса
    } else {
      setSelectedCourseId(courseId);
      await fetchLessons(courseId); // Получаем уроки для выбранного курса
      await fetchNextLessonId(courseId); // Получаем следующий lessonId
    }
  };

  // Обновление курса
  const handleUpdateCourse = async (courseTitle) => {
    try {
      const token = localStorage.getItem('token');
      await axios.put(
        `http://51.250.6.237:8000/admin/admin/course/update/?title=${courseTitle}`,
        { title: updatedCourseTitle, description: updatedCourseDescription },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      fetchCourses(); // Обновляем список курсов после изменения
      setUpdatedCourseTitle(''); // Сбрасываем поля ввода
      setUpdatedCourseDescription('');
    } catch (error) {
      setError('Failed to update course');
      console.error(error);
    }
  };

  // Загрузка урока
  const handleUploadLesson = async (courseId) => {
    if (!file || nextLessonId === null) {
      setError('No file selected or lesson ID not fetched');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const formData = new FormData();
      formData.append('file', file);
      // formData.append('lesson_id', nextLessonId); // Передаем следующий lesson_id

      await axios.post(`http://51.250.6.237:8000/admin/admin/lesson/create/?course_id=${courseId}&lesson_id=${nextLessonId}`, formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data',
        },
      });
      setFile(null); // Очищаем выбранный файл после загрузки
      fetchLessons(courseId); // Обновляем список уроков после загрузки
    } catch (error) {
      setError('Failed to upload lesson');
      console.error(error);
    }
  };

  return (
    <div className="admin-panel-container">
      <h2 className="admin-header">Admin Panel</h2>

      {error && <p className="error-notification">{error}</p>}

      <h3>Create New Course</h3>
      <input
        type="text"
        placeholder="Course Title"
        value={newCourseTitle}
        onChange={(e) => setNewCourseTitle(e.target.value)}
      />
      <input
        type="text"
        placeholder="Course Description"
        value={newCourseDescription}
        onChange={(e) => setNewCourseDescription(e.target.value)}
      />
      <button className="admin-button" onClick={handleCreateCourse}>Create Course</button>

      <h3>Courses List</h3>
      <ul className="course-cards">
        {courses.map((course) => (
          <li key={course.id} className="course-card">
            <span className="course-title">{course.title}</span>
            <div className="course-footer">
              <button className="admin-button" onClick={() => handleToggleDetails(course.id)}>
                {selectedCourseId === course.id ? 'Hide Details' : 'View Details'}
              </button>
              <button className="admin-button delete-button" onClick={() => handleDeleteCourse(course.title)}>
                Delete
              </button>
            </div>

            {/* Показываем детали курса и уроки, если курс выбран */}
            {selectedCourseId === course.id && (
              <div className="course-details">
                <p><strong>Description:</strong> {course.description}</p>

                {/* Форма для обновления курса */}
                <h4>Update Course</h4>
                <input
                  type="text"
                  placeholder="New Course Title"
                  value={updatedCourseTitle}
                  onChange={(e) => setUpdatedCourseTitle(e.target.value)}
                />
                <input
                  type="text"
                  placeholder="New Course Description"
                  value={updatedCourseDescription}
                  onChange={(e) => setUpdatedCourseDescription(e.target.value)}
                />
                <button className="admin-button" onClick={() => handleUpdateCourse(course.title)}>Update Course</button>

                {/* Форма для загрузки уроков */}
                <h4>Upload Lesson (Next Lesson ID: {nextLessonId})</h4>
                <input type="file" onChange={(e) => setFile(e.target.files[0])} />
                <button className="admin-button" onClick={() => handleUploadLesson(course.id)}>Upload Lesson</button>

                <h4>Lessons:</h4>
                <ul className="lesson-list">
                  {lessons.map((lesson) => (
                    <li key={lesson.id} className="lesson-item">
                      <span>Lesson ID: {lesson.lesson_id}</span>
                      <button className="admin-button delete-button" onClick={() => handleDeleteLesson(course.id, lesson.lesson_id)}>
                        Delete Lesson
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default AdminPanel;