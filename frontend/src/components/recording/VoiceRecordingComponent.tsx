'use client';

import React, { useState, useRef } from 'react';
import { Button } from '@/components/ui/Button';
import Timer from '@/components/ui/Timer';
import AudioRecorder from './AudioRecorder';
import { Question } from '@/types/questions';

interface VoiceRecordingComponentProps {
  question: Question;
  onRecordingComplete: (audioBlob: Blob, duration: number) => void;
  maxDuration?: number; // In seconds
  onCancel?: () => void;
}

const VoiceRecordingComponent: React.FC<VoiceRecordingComponentProps> = ({
  question,
  onRecordingComplete,
  maxDuration = 180, // Default 3 minutes
  onCancel,
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingComplete, setRecordingComplete] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const timerIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const startRecording = () => {
    setIsRecording(true);
    setRecordingComplete(false);
    setRecordingTime(0);
    
    // Start a timer to track recording duration
    timerIntervalRef.current = setInterval(() => {
      setRecordingTime(prev => prev + 1);
    }, 1000);
  };

  const stopRecording = () => {
    setIsRecording(false);
    
    // Clear the timer
    if (timerIntervalRef.current) {
      clearInterval(timerIntervalRef.current);
      timerIntervalRef.current = null;
    }
  };

  const handleRecordingComplete = (audioBlob: Blob) => {
    setRecordingComplete(true);
    onRecordingComplete(audioBlob, recordingTime);
  };

  const handleTimerComplete = () => {
    stopRecording();
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      {/* Question display */}
      <div className="mb-6">
        <h3 className="text-xl font-medium text-gray-800 mb-2">Question:</h3>
        <div className="p-4 bg-gray-50 rounded-lg">
          <p className="text-gray-700">{question.content}</p>
        </div>
      </div>

      {/* Recording interface */}
      <div className="space-y-6">
        {/* Timer */}
        <div className="flex justify-center">
          <Timer
            initialTimeInSeconds={maxDuration}
            onComplete={handleTimerComplete}
            autoStart={isRecording}
            showControls={false}
            size="lg"
          />
        </div>

        {/* Recording status */}
        <div className="flex justify-center items-center">
          {isRecording ? (
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
              <span className="text-gray-700">Recording in progress...</span>
            </div>
          ) : recordingComplete ? (
            <div className="text-green-600 font-medium">Recording complete!</div>
          ) : (
            <div className="text-gray-600">Ready to record your answer</div>
          )}
        </div>

        {/* Hidden audio recorder component */}
        <AudioRecorder
          onRecordingComplete={handleRecordingComplete}
          maxDuration={maxDuration}
          isRecording={isRecording}
          onRecordingStart={() => {}}
          onRecordingStop={stopRecording}
        />

        {/* Controls */}
        <div className="flex justify-center space-x-3">
          {!isRecording && !recordingComplete && (
            <Button 
              onClick={startRecording}
              className="px-8"
            >
              <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
              </svg>
              Start Recording
            </Button>
          )}
          
          {isRecording && (
            <Button 
              onClick={stopRecording}
              variant="destructive"
              className="px-8"
            >
              <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 001 1h4a1 1 0 001-1V8a1 1 0 00-1-1H8z" clipRule="evenodd" />
              </svg>
              Stop Recording
            </Button>
          )}
          
          {!isRecording && (
            <Button 
              onClick={onCancel}
              variant="outline"
            >
              Cancel
            </Button>
          )}
        </div>

        {/* Recording tips */}
        <div className="border-t border-gray-200 pt-4 mt-4">
          <h4 className="text-sm font-medium text-gray-800 mb-2">Tips for a great answer:</h4>
          <ul className="text-sm text-gray-600 list-disc list-inside space-y-1">
            <li>Speak clearly and at a moderate pace</li>
            <li>Structure your answer with a beginning, middle, and conclusion</li>
            <li>Use specific examples to support your points</li>
            <li>Keep your answer concise and on-topic</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default VoiceRecordingComponent;
