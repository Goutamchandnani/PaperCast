import React from 'react';

const AudioPlayer = ({ audioUrl }) => {
    if (!audioUrl) return null;

    return (
        <div className="audio-player-container">
            <h3>Your Podcast is Ready</h3>
            <div className="audio-wrapper">
                <audio controls className="custom-audio" autoPlay>
                    <source src={audioUrl} type="audio/mpeg" />
                    Your browser does not support the audio element.
                </audio>
            </div>
            <div className="audio-actions">
                <a href={audioUrl} download="papercast_podcast.mp3" className="download-btn">
                    Download MP3
                </a>
            </div>
        </div>
    );
};

export default AudioPlayer;
