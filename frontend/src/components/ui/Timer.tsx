"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { cn } from '@/lib/utils';
import { Button } from './Button';

interface TimerProps {
  initialTimeInSeconds: number;
  onComplete?: () => void;
  autoStart?: boolean;
  className?: string;
  showControls?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

const Timer: React.FC<TimerProps> = ({
  initialTimeInSeconds,
  onComplete,
  autoStart = false,
  className,
  showControls = true,
  size = 'md',
}) => {
  const [timeRemaining, setTimeRemaining] = useState(initialTimeInSeconds);
  const [isActive, setIsActive] = useState(autoStart);
  const [isPaused, setIsPaused] = useState(false);

  // Calculate percentage of time remaining
  const percentageComplete = Math.floor(
    ((initialTimeInSeconds - timeRemaining) / initialTimeInSeconds) * 100
  );

  // Format time as mm:ss
  const formatTime = useCallback((seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes.toString().padStart(2, '0')}:${remainingSeconds
      .toString()
      .padStart(2, '0')}`;
  }, []);

  // Handle timer completion
  const handleComplete = useCallback(() => {
    setIsActive(false);
    if (onComplete) {
      onComplete();
    }
  }, [onComplete]);

  // Timer logic
  useEffect(() => {
    let interval: NodeJS.Timeout | null = null;

    if (isActive && !isPaused) {
      interval = setInterval(() => {
        setTimeRemaining((prev) => {
          if (prev <= 1) {
            clearInterval(interval!);
            handleComplete();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    } else if (interval) {
      clearInterval(interval);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isActive, isPaused, handleComplete]);

  // Timer controls
  const startTimer = () => {
    setIsActive(true);
    setIsPaused(false);
  };

  const pauseTimer = () => {
    setIsPaused(true);
  };

  const resumeTimer = () => {
    setIsPaused(false);
  };

  const resetTimer = () => {
    setTimeRemaining(initialTimeInSeconds);
    setIsActive(false);
    setIsPaused(false);
  };

  // Determine timer size
  const sizeClass = {
    sm: 'text-xl',
    md: 'text-3xl',
    lg: 'text-5xl',
  };

  // Warning color when time is running low (less than 20%)
  const isWarning = timeRemaining / initialTimeInSeconds < 0.2 && timeRemaining > 0;

  return (
    <div className={cn('flex flex-col items-center', className)}>
      <div className="relative mb-2">
        <div className={cn('font-mono font-bold', sizeClass[size], isWarning ? 'text-red-600' : '')}>
          {formatTime(timeRemaining)}
        </div>
        {/* Progress indicator */}
        <div className="w-full h-2 bg-gray-200 rounded-full mt-2 overflow-hidden">
          <div
            className={cn(
              'h-full transition-all',
              isWarning ? 'bg-red-500' : 'bg-blue-500'
            )}
            style={{ width: `${percentageComplete}%` }}
          />
        </div>
      </div>

      {showControls && (
        <div className="flex space-x-2 mt-2">
          {!isActive && !isPaused ? (
            <Button size="sm" onClick={startTimer}>
              Start
            </Button>
          ) : isPaused ? (
            <Button size="sm" onClick={resumeTimer}>
              Resume
            </Button>
          ) : (
            <Button size="sm" onClick={pauseTimer}>
              Pause
            </Button>
          )}
          <Button
            size="sm"
            variant="secondary"
            onClick={resetTimer}
            disabled={timeRemaining === initialTimeInSeconds && !isActive}
          >
            Reset
          </Button>
        </div>
      )}
    </div>
  );
};

export default Timer;
