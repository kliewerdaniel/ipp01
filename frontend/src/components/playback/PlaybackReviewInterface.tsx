'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/Button';
import AudioPlaybackPlayer from './AudioPlaybackPlayer';
import { Question } from '@/types/questions';

interface PlaybackReviewInterfaceProps {
  question: Question;
  audioUrl: string;
  duration: number; // in seconds
  transcript?: string;
  onReRecord?: () => void;
  onSubmit?: () => void;
  onRequestFeedback?: () => void;
  waveformData?: number[]; // optional audio waveform data
}

const PlaybackReviewInterface: React.FC<PlaybackReviewInterfaceProps> = ({
  question,
  audioUrl,
  duration,
  transcript,
  onReRecord,
  onSubmit,
  onRequestFeedback,
  waveformData,
}) => {
  const [showTranscript, setShowTranscript] = useState(!!transcript);
  const [isTranscriptLoading, setIsTranscriptLoading] = useState(false);

  const handleTranscriptToggle = () => {
    if (!transcript && !isTranscriptLoading) {
      // If transcript doesn't exist yet, we simulate a request to generate it
      setIsTranscriptLoading(true);
      // In a real app, this would be an API call to transcribe the audio
      setTimeout(() => {
        setIsTranscriptLoading(false);
        setShowTranscript(true);
      }, 2000);
    } else {
      setShowTranscript(!showTranscript);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      {/* Question display */}
      <div className="p-6 border-b border-gray-200">
        <h3 className="text-xl font-medium text-gray-800 mb-2">Question:</h3>
        <div className="p-4 bg-gray-50 rounded-lg">
          <p className="text-gray-700">{question.content}</p>
        </div>
      </div>

      {/* Audio player section */}
      <div className="p-6 border-b border-gray-200">
        <h3 className="text-xl font-medium text-gray-800 mb-4">Your Answer</h3>
        <AudioPlaybackPlayer 
          audioUrl={audioUrl} 
          duration={duration} 
          waveformData={waveformData}
        />
        
        {/* Transcript toggle button */}
        <div className="mt-4 flex justify-end">
          <Button
            variant="outline"
            size="sm"
            onClick={handleTranscriptToggle}
            disabled={isTranscriptLoading}
          >
            {isTranscriptLoading ? (
              <>
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Generating Transcript...
              </>
            ) : (
              showTranscript ? 'Hide Transcript' : 'Show Transcript'
            )}
          </Button>
        </div>
      </div>

      {/* Transcript section */}
      {showTranscript && (
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-xl font-medium text-gray-800 mb-2">Transcript</h3>
          <div className="p-4 bg-gray-50 rounded-lg">
            {transcript ? (
              <p className="text-gray-700 whitespace-pre-line">{transcript}</p>
            ) : (
              <p className="text-gray-500 italic">No transcript available. For a real implementation, this would be generated from the audio.</p>
            )}
          </div>
          <p className="text-xs text-gray-500 mt-2">Note: AI-generated transcripts may not be 100% accurate.</p>
        </div>
      )}

      {/* Action buttons */}
      <div className="p-6 flex flex-wrap gap-3 justify-between">
        <Button
          variant="outline"
          onClick={onReRecord}
        >
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Record Again
        </Button>
        
        <div className="flex gap-3">
          <Button
            variant="secondary"
            onClick={onRequestFeedback}
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
            Get AI Feedback
          </Button>
          
          <Button
            onClick={onSubmit}
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
            </svg>
            Submit Answer
          </Button>
        </div>
      </div>
    </div>
  );
};

export default PlaybackReviewInterface;
