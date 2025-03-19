'use client';

import React, { useState, useEffect, useRef } from 'react';

interface AudioRecorderProps {
  onRecordingComplete: (audioBlob: Blob) => void;
  maxDuration?: number; // Maximum recording duration in seconds
  isRecording: boolean;
  onRecordingStart?: () => void;
  onRecordingStop?: () => void;
}

const AudioRecorder: React.FC<AudioRecorderProps> = ({
  onRecordingComplete,
  maxDuration = 300, // Default 5 minutes
  isRecording,
  onRecordingStart,
  onRecordingStop,
}) => {
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);
  const [audioChunks, setAudioChunks] = useState<Blob[]>([]);
  const [isInitialized, setIsInitialized] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  
  // Initialize the media recorder
  useEffect(() => {
    if (!isInitialized) {
      initializeMediaRecorder();
    }
    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
    };
  }, []);

  // Control recording state
  useEffect(() => {
    if (isRecording && mediaRecorder && mediaRecorder.state === 'inactive') {
      startRecording();
    } else if (!isRecording && mediaRecorder && mediaRecorder.state === 'recording') {
      stopRecording();
    }
  }, [isRecording, mediaRecorder]);

  const initializeMediaRecorder = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      
      recorder.addEventListener('dataavailable', (event) => {
        if (event.data.size > 0) {
          setAudioChunks((prev) => [...prev, event.data]);
        }
      });

      recorder.addEventListener('stop', () => {
        if (onRecordingStop) {
          onRecordingStop();
        }
        
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        onRecordingComplete(audioBlob);
        setAudioChunks([]);
      });

      setMediaRecorder(recorder);
      setIsInitialized(true);
    } catch (err) {
      setError('Could not access microphone. Please ensure you have granted microphone permissions.');
      console.error('Error initializing media recorder:', err);
    }
  };

  const startRecording = () => {
    if (mediaRecorder) {
      setAudioChunks([]);
      mediaRecorder.start(1000); // Collect data in 1-second chunks
      
      if (onRecordingStart) {
        onRecordingStart();
      }
      
      // Set up max duration timer
      if (maxDuration > 0) {
        timerRef.current = setTimeout(() => {
          if (mediaRecorder.state === 'recording') {
            stopRecording();
          }
        }, maxDuration * 1000);
      }
    }
  };

  const stopRecording = () => {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
      mediaRecorder.stop();
      
      if (timerRef.current) {
        clearTimeout(timerRef.current);
        timerRef.current = null;
      }
    }
  };

  return (
    <div>
      {error && <div className="text-red-500 mb-2">{error}</div>}
      <div className="hidden">
        {/* Visualization could be added here in the future */}
      </div>
    </div>
  );
};

export default AudioRecorder;
