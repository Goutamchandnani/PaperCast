import { useState, useEffect } from 'react'
import axios from 'axios'
import UploadSection from './components/UploadSection'
import ProgressBar from './components/ProgressBar'
import AudioPlayer from './components/AudioPlayer'
import { Headphones, Loader2, AlertCircle, Github, Linkedin, Heart, Car, Activity, Zap } from 'lucide-react'

const API_BASE_URL = 'http://127.0.0.1:8000/api/podcast'

function App() {
    const [file, setFile] = useState(null)
    const [jobId, setJobId] = useState(null)
    const [status, setStatus] = useState('idle') // idle, uploading, processing, completed, error
    const [progress, setProgress] = useState(0)
    const [statusText, setStatusText] = useState('')
    const [audioUrl, setAudioUrl] = useState(null)
    const [error, setError] = useState(null)
    const [language, setLanguage] = useState('english')

    useEffect(() => {
        let pollInterval;

        const checkStatus = async () => {
            if (!jobId) return;

            try {
                const response = await axios.get(`${API_BASE_URL}/status/${jobId}`)
                const data = response.data

                setProgress(data.progress)
                setStatusText(data.status)

                if (data.status === 'completed') {
                    setStatus('completed')
                    setAudioUrl(data.audio_url)
                    clearInterval(pollInterval)
                } else if (data.status === 'failed') {
                    setStatus('error')
                    setError(data.error || 'An error occurred during processing.')
                    clearInterval(pollInterval)
                }
            } catch (err) {
                console.error("Error checking status:", err)
                // We'll keep polling unless it's a 404
                if (err.response && err.response.status === 404) {
                    setStatus('error')
                    setError('Job not found.')
                    clearInterval(pollInterval)
                }
            }
        };

        if (status === 'processing') {
            pollInterval = setInterval(checkStatus, 2000)
        }

        return () => {
            if (pollInterval) clearInterval(pollInterval)
        }
    }, [jobId, status])

    const handleUpload = async (selectedFile) => {
        setFile(selectedFile)
        setStatus('uploading')
        setError(null)
        setAudioUrl(null)
        setProgress(0)

        const formData = new FormData()
        formData.append('file', selectedFile)
        formData.append('language', language)

        try {
            const response = await axios.post(`${API_BASE_URL}/generate`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            })
            setJobId(response.data.job_id)
            setStatus('processing')
        } catch (err) {
            console.error("Upload error:", err)
            setStatus('error')
            setError(err.response?.data?.detail || 'Failed to upload file.')
        }
    }

    const resetState = () => {
        setFile(null)
        setJobId(null)
        setStatus('idle')
        setProgress(0)
        setStatusText('')
        setAudioUrl(null)
        setError(null)
    }

    return (
        <div className="app-container">
            <div className="glass-morphism-bg"></div>

            <header className="header">
                <div className="logo">
                    <Headphones size={40} className="logo-icon" />
                    <h1>PaperCast</h1>
                </div>
                <p>Turn complex research papers into engaging, conversational podcasts.</p>
            </header>

            {status === 'idle' && (
                <div className="features-section">
                    <div className="feature-card">
                        <div className="feature-icon-wrapper">
                            <Car size={24} className="feature-icon" />
                        </div>
                        <h3>Commute & Learn</h3>
                        <p>Listen to latest research papers while driving or taking the train.</p>
                    </div>
                    <div className="feature-card">
                        <div className="feature-icon-wrapper">
                            <Activity size={24} className="feature-icon" />
                        </div>
                        <h3>Cardio Companion</h3>
                        <p>Turn your workout sessions into productive learning experiences.</p>
                    </div>
                    <div className="feature-card">
                        <div className="feature-icon-wrapper">
                            <Zap size={24} className="feature-icon" />
                        </div>
                        <h3>Screen-Free</h3>
                        <p>Rest your eyes from screens without falling behind on research.</p>
                    </div>
                </div>
            )}

            <main className="main-content glass-card">
                {status === 'idle' && (
                    <div className="upload-container">
                        <div className="language-selector">
                            <label htmlFor="language">Podcast Language:</label>
                            <select
                                id="language"
                                value={language}
                                onChange={(e) => setLanguage(e.target.value)}
                                className="language-dropdown"
                            >
                                <option value="english">English</option>
                                <option value="spanish">Spanish</option>
                                <option value="french">French</option>
                                <option value="german">German</option>
                                <option value="hindi">Hindi</option>
                                <option value="chinese">Chinese</option>
                                <option value="arabic">Arabic</option>
                            </select>
                        </div>
                        <UploadSection onUpload={handleUpload} disabled={false} />
                    </div>
                )}

                {status === 'uploading' && (
                    <div className="state-container updating">
                        <Loader2 className="spinner" size={48} />
                        <h3>Uploading your document...</h3>
                        <p>Please wait while we secure your file.</p>
                    </div>
                )}

                {status === 'processing' && (
                    <div className="state-container processing">
                        <ProgressBar progress={progress} status={statusText} />
                        <div className="processing-fun-fact">
                            <p>Did you know? Gemini 2.5 Flash processes up to thousands of pages in seconds!</p>
                        </div>
                    </div>
                )}

                {status === 'completed' && (
                    <div className="state-container success slide-up">
                        <div className="success-icon-wrapper">
                            <Headphones size={48} className="success-icon" />
                        </div>
                        <AudioPlayer audioUrl={audioUrl} />
                        <button className="secondary-btn mt-4" onClick={resetState}>
                            Convert Another Paper
                        </button>
                    </div>
                )}

                {status === 'error' && (
                    <div className="state-container error shake">
                        <AlertCircle size={48} className="error-icon" />
                        <h3>Oops! Something went wrong</h3>
                        <p className="error-message">{error}</p>
                        <button className="primary-btn mt-4" onClick={resetState}>
                            Try Again
                        </button>
                    </div>
                )}
            </main>

            <footer className="footer">
                <p>
                    Made with <Heart size={16} className="heart-icon" /> by Goutam Chandnani
                </p>
                <div className="social-links">
                    <a href="https://www.linkedin.com/in/goutamchandnani/" target="_blank" rel="noopener noreferrer" className="social-icon" aria-label="LinkedIn">
                        <Linkedin size={24} />
                    </a>
                    <a href="https://github.com/Goutamchandnani/PaperCast" target="_blank" rel="noopener noreferrer" className="social-icon" aria-label="GitHub">
                        <Github size={24} />
                    </a>
                </div>
            </footer>
        </div>
    )
}

export default App
