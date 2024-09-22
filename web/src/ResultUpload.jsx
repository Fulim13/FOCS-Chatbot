import React, { useState } from "react";
import { Form, Button } from "react-bootstrap";

const ResultUpload = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isGeneratingResponse, setIsGeneratingResponse] = useState(false);
  const [selectedProgram, setSelectedProgram] = useState("");
  const [responseMessage, setResponseMessage] = useState("");

  const programOptions = [
    "Foundation in Computing",
    "Diploma in Computer Science",
    "Diploma in Information Technology",
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
      setResponseMessage("Please select a file and a program first.");
      return;
    }

    const formData = new FormData();
    formData.append("resultImage", selectedFile);
    formData.append("program", selectedProgram);

    setIsGeneratingResponse(true);

    try {
      const response = await fetch("http://localhost:8000/upload-result/", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        setResponseMessage(data.data);
      } else {
        setResponseMessage(data.error || "An unknown error occurred.");
      }
    } catch (error) {
      setResponseMessage("Error while uploading: " + error.message);
    } finally {
      setIsGeneratingResponse(false);
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

        <Button variant="primary" type="submit" disabled={isGeneratingResponse}>
          {isGeneratingResponse ? "Generating Response..." : "Upload"}
        </Button>
      </Form>
      {isGeneratingResponse && <p>Response is generating, please wait...</p>}
      {responseMessage && (
        <div
          style={{ textAlign: "left", whiteSpace: "pre-wrap" }} // Left align and pre-wrap the response text
          dangerouslySetInnerHTML={{ __html: responseMessage }}
        />
      )}
    </div>
  );
};

export default ResultUpload;
