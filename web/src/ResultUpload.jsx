import React, { useState } from "react";
import { Form, Button } from "react-bootstrap";

const ResultUpload = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState("");
  const [selectedProgram, setSelectedProgram] = useState("");

  const programOptions = [
    "Foundation in Computing",
    "Diploma in Computer Science",
    "Diploma in Information Technology",
    "Bachelor of Software Engineering (Honours)",
    "Bachelor of Computer Science (Honours) in Data Science",
    "Bachelor of Computer Science (Honours) in Interactive Software Technology",
    "Bachelor of Information Technology (Honours) in Software Systems Development",
    "Bachelor of Information Technology (Honours) in Information Security",
    "Master of Information Technology",
    "Master of Computer Science",
    "Doctor of Philosophy (Information Technology)",
    "Doctor of Philosophy in Computer Science",
  ];

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleProgramChange = (event) => {
    setSelectedProgram(event.target.value);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!selectedFile || !selectedProgram) {
      setUploadStatus("Please select a file and a program first.");
      return;
    }

    const formData = new FormData();
    formData.append("resultImage", selectedFile);
    formData.append("program", selectedProgram);

    try {
      const response = await fetch("http://localhost:8000/result-upload", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        setUploadStatus("File uploaded successfully.");
      } else {
        setUploadStatus("Failed to upload file.");
      }
    } catch (error) {
      setUploadStatus("Error while uploading: " + error.message);
    }
  };

  return (
    <div>
      <h2>Upload Your Result Image</h2>
      <Form onSubmit={handleSubmit}>
        <Form.Group controlId="formProgram" className="mb-3">
          <Form.Label>Select Program</Form.Label>
          <Form.Select value={selectedProgram} onChange={handleProgramChange}>
            <option value="">-- Select a Program --</option>
            {programOptions.map((program, index) => (
              <option key={index} value={program}>
                {program}
              </option>
            ))}
          </Form.Select>
        </Form.Group>

        <Form.Group controlId="formFile" className="mb-3">
          <Form.Label>Choose Image</Form.Label>
          <Form.Control
            type="file"
            accept="image/*"
            onChange={handleFileChange}
          />
        </Form.Group>

        <Button variant="primary" type="submit">
          Upload
        </Button>
      </Form>
      {uploadStatus && <p>{uploadStatus}</p>}
    </div>
  );
};

export default ResultUpload;
