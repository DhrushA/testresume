import React, { useState } from 'react';
import axios from 'axios';

const FileUploader = () => {
  const [file, setFile] = useState(null);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      alert('Please select a file first!');
      return;
    }

    try {
      const response = await axios.post('https://lnum4qu0pl.execute-api.us-east-2.amazonaws.com/dev/generate_presigned_url', {
        fileName: file.name,
        fileType: file.type,
      });

      const { uploadURL } = response.data;

      // Upload the file to S3 using the presigned URL
      await axios.put(uploadURL, file, {
        headers: {
          'Content-Type': file.type,
        },
      });

      alert('File uploaded successfully!');
    } catch (error) {
      console.error('Error uploading file:', error);
      alert('File upload failed.');
    }
  };

  return (
    <div>
      <h1>Upload Your Resume</h1>
      <input type="file" onChange={handleFileChange} />
      <button onClick={handleUpload}>Upload</button>
    </div>
  );
};

export default FileUploader;
