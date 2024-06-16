// src/components/UploadMaterials.js

import React, { useState } from 'react';
import axios from 'axios';

const UploadMaterials = ({ courseId }) => { // Передаем courseId как параметр функции
  const [file, setFile] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('file', file);
    try {
      const response = await axios.post(`/api/course/${courseId}/materials/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      console.log('File uploaded:', response.data);
      // Очистить форму или выполнить другие действия после успешной загрузки материалов
    } catch (error) {
      console.error('Error uploading file:', error);
    }
  };

  return (
    <div>
      <h2>Upload Materials</h2>
      <form onSubmit={handleSubmit}>
        <input type="file" onChange={handleFileChange} required />
        <button type="submit">Upload File</button>
      </form>
    </div>
  );
};

export default UploadMaterials;
