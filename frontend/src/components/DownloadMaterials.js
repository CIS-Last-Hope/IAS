import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams } from 'react-router-dom';

function DownloadMaterials() {
  const { courseId } = useParams();
  const [error, setError] = useState('');

  const handleDownload = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      setError('Token not found');
      return;
    }

    try {
      const response = await axios.get(`http://localhost:8000/course/${courseId}/materials/download?token=${token}`, {
        responseType: 'blob', // Указываем тип ответа как blob (для скачивания файла)
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `course_${courseId}_materials.zip`);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
    } catch (error) {
      console.error(error.response?.data);
      setError('Failed to download materials');
    }
  };

  return (
    <div>
      <h2>Download Materials</h2>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <button onClick={handleDownload}>Download</button>
    </div>
  );
}

export default DownloadMaterials;
