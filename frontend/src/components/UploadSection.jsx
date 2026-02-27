import React, { useRef, useState } from 'react';
import { UploadCloud } from 'lucide-react';

const UploadSection = ({ onUpload, disabled }) => {
    const [dragActive, setDragActive] = useState(false);
    const inputRef = useRef(null);

    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        if (!disabled && e.dataTransfer.files && e.dataTransfer.files[0]) {
            const file = e.dataTransfer.files[0];
            if (file.type === "application/pdf" || file.name.endsWith(".pdf")) {
                onUpload(file);
            } else {
                alert("Please upload a PDF file.");
            }
        }
    };

    const handleChange = (e) => {
        e.preventDefault();
        if (e.target.files && e.target.files[0]) {
            onUpload(e.target.files[0]);
        }
    };

    return (
        <div
            className={`upload-section ${dragActive ? "drag-active" : ""} ${disabled ? "disabled" : ""}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => !disabled && inputRef.current.click()}
        >
            <input
                ref={inputRef}
                type="file"
                accept=".pdf"
                onChange={handleChange}
                style={{ display: "none" }}
                disabled={disabled}
            />
            <div className="upload-content">
                <UploadCloud size={64} className="upload-icon" />
                <h3>Drop your research paper</h3>
                <p>Or click to browse (PDF only)</p>
            </div>
        </div>
    );
};

export default UploadSection;
