import React, { useState } from 'react';
import axios from 'axios';
import { useParams } from 'react-router-dom';

function UploadMaterials() {
  const { courseId } = useParams();
  const [file, setFile] = useState(null);
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      setError('Token not found');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      await axios.post(`http://localhost:8000/course/${courseId}/materials/upload?token=${token}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      alert('File uploaded successfully!');
      setFile(null); // Очищаем состояние файла после успешной загрузки
    } catch (error) {
      console.error(error.response?.data);
      setError('Failed to upload file');
    }
  };

  return (
    <div>
      <h2>Upload Materials</h2>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <input type="file" onChange={handleFileChange} />
      <button onClick={handleUpload}>Upload</button>
    </div>
  );
}

export default UploadMaterials;
