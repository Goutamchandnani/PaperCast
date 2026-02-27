import React from 'react';
import { FileText, Mic, Headphones } from 'lucide-react';

const ProgressBar = ({ progress, status }) => {
    const getStatusText = () => {
        switch (status) {
            case 'extracting_text': return 'Reading and extracting text...';
            case 'generating_script': return 'Writing the podcast script...';
            case 'generating_audio': return 'Recording the podcast audio...';
            case 'uploading_audio': return 'Finalizing your MP3...';
            case 'completed': return 'Podcast ready!';
            default: return 'Starting...';
        }
    };

    return (
        <div className="progress-container">
            <div className="progress-info">
                <span className="status-text">{getStatusText()}</span>
                <span className="progress-percentage">{progress}%</span>
            </div>
            <div className="progress-bar-bg">
                <div
                    className="progress-bar-fill"
                    style={{ width: `${progress}%` }}
                ></div>
            </div>
            <div className="progress-steps">
                <div className={`step ${progress >= 10 ? 'active' : ''}`}>
                    <FileText size={20} />
                    <span>Parse</span>
                </div>
                <div className={`step ${progress >= 30 ? 'active' : ''}`}>
                    <Mic size={20} />
                    <span>Script</span>
                </div>
                <div className={`step ${progress >= 60 ? 'active' : ''}`}>
                    <Headphones size={20} />
                    <span>Audio</span>
                </div>
            </div>
        </div>
    );
};

export default ProgressBar;
