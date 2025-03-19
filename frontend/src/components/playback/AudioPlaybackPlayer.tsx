'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/Button';

interface AudioPlaybackPlayerProps {
  audioUrl: string;
  duration?: number; // in seconds
  waveformData?: number[]; // optional audio waveform data
}

const AudioPlaybackPlayer: React.FC<AudioPlaybackPlayerProps> = ({
  audioUrl,
  duration,
  waveformData,
}) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [audioDuration, setAudioDuration] = useState(duration || 0);
  const audioRef = useRef<HTMLAudioElement>(null);
  const progressRef = useRef<HTMLDivElement>(null);

  // Initialize audio element
  useEffect(() => {
    if (audioRef.current) {
      // Set up event listeners
      const audio = audioRef.current;
      
      const handleLoadedMetadata = () => {
        setAudioDuration(audio.duration);
      };
      
      const handleTimeUpdate = () => {
        setCurrentTime(audio.currentTime);
      };
      
      const handleEnded = () => {
        setIsPlaying(false);
        setCurrentTime(0);
      };
      
      audio.addEventListener('loadedmetadata', handleLoadedMetadata);
      audio.addEventListener('timeupdate', handleTimeUpdate);
      audio.addEventListener('ended', handleEnded);
      
      // Clean up event listeners
      return () => {
        audio.removeEventListener('loadedmetadata', handleLoadedMetadata);
        audio.removeEventListener('timeupdate', handleTimeUpdate);
        audio.removeEventListener('ended', handleEnded);
      };
    }
  }, []);

  // Format time in MM:SS format
  const formatTime = (timeInSeconds: number) => {
    const minutes = Math.floor(timeInSeconds / 60);
    const seconds = Math.floor(timeInSeconds % 60);
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  };

  // Toggle play/pause
  const togglePlayPause = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  // Handle seeking through the audio
  const handleSeek = (e: React.MouseEvent<HTMLDivElement>) => {
    if (progressRef.current && audioRef.current) {
      const progressBar = progressRef.current;
      const rect = progressBar.getBoundingClientRect();
      const clickPosition = (e.clientX - rect.left) / rect.width;
      const newTime = audioDuration * clickPosition;
      
      audioRef.current.currentTime = newTime;
      setCurrentTime(newTime);
    }
  };

  // Calculate progress percentage
  const progressPercentage = audioDuration > 0 
    ? (currentTime / audioDuration) * 100 
    : 0;

  return (
    <div className="bg-white rounded-lg p-4 shadow-sm">
      {/* Hidden audio element */}
      <audio ref={audioRef} src={audioUrl} />
      
      {/* Progress bar */}
      <div 
        ref={progressRef}
        className="h-2 bg-gray-200 rounded-full mb-2 cursor-pointer"
        onClick={handleSeek}
      >
        <div 
          className="h-full bg-blue-500 rounded-full"
          style={{ width: `${progressPercentage}%` }}
        />
      </div>
      
      {/* Controls and time display */}
      <div className="flex items-center justify-between">
        {/* Play/Pause button */}
        <Button
          onClick={togglePlayPause}
          variant="ghost"
          size="icon"
          className="p-1"
        >
          {isPlaying ? (
            <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 00-1 1v2a1 1 0 001 1h6a1 1 0 001-1V9a1 1 0 00-1-1H7z" clipRule="evenodd" />
            </svg>
          ) : (
            <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
            </svg>
          )}
        </Button>
        
        {/* Time display */}
        <div className="text-sm text-gray-600">
          {formatTime(currentTime)} / {formatTime(audioDuration)}
        </div>
        
        {/* Additional controls could be added here */}
        <div className="flex space-x-2">
          <Button
            onClick={() => {
              if (audioRef.current) {
                audioRef.current.playbackRate = 1.0;
              }
            }}
            variant="ghost"
            size="sm"
            className="text-xs px-2"
          >
            1.0x
          </Button>
          <Button
            onClick={() => {
              if (audioRef.current) {
                audioRef.current.playbackRate = 1.5;
              }
            }}
            variant="ghost"
            size="sm"
            className="text-xs px-2"
          >
            1.5x
          </Button>
          <Button
            onClick={() => {
              if (audioRef.current) {
                audioRef.current.playbackRate = 2.0;
              }
            }}
            variant="ghost"
            size="sm"
            className="text-xs px-2"
          >
            2.0x
          </Button>
        </div>
      </div>
      
      {/* Audio waveform visualization (simplified version) */}
      {waveformData && waveformData.length > 0 && (
        <div className="mt-2 h-12 flex items-center justify-center">
          <div className="flex items-center h-full space-x-0.5">
            {waveformData.map((amplitude, index) => (
              <div
                key={index}
                className="w-1 bg-blue-300"
                style={{
                  height: `${Math.max(4, amplitude * 100)}%`,
                  opacity: currentTime / audioDuration > index / waveformData.length ? 1 : 0.5,
                }}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default AudioPlaybackPlayer;
