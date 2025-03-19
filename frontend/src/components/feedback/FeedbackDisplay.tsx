'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/Button';

export interface FeedbackItem {
  category: string;
  score: number; // 0-100
  comment: string;
}

export interface Feedback {
  overallScore: number; // 0-100
  strengths: string[];
  areasForImprovement: string[];
  detailedFeedback: FeedbackItem[];
  summary: string;
  suggestedAnswer?: string;
}

interface FeedbackDisplayProps {
  feedback: Feedback;
  isLoading?: boolean;
  originalQuestion?: string;
  onClose?: () => void;
}

const FeedbackDisplay: React.FC<FeedbackDisplayProps> = ({
  feedback,
  isLoading = false,
  originalQuestion,
  onClose,
}) => {
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    strengths: true,
    improvements: true,
    detailed: false,
    suggested: false,
  });

  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBackground = (score: number) => {
    if (score >= 80) return 'bg-green-100';
    if (score >= 60) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 min-h-[400px] flex flex-col items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mb-4"></div>
        <p className="text-gray-600">Generating feedback...</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      {/* Header with overall score */}
      <div className="bg-gray-50 p-6 border-b border-gray-200">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-800">AI Feedback</h2>
          <div className={`${getScoreBackground(feedback.overallScore)} px-4 py-2 rounded-full flex items-center`}>
            <span className={`text-xl font-bold ${getScoreColor(feedback.overallScore)}`}>
              {feedback.overallScore}/100
            </span>
          </div>
        </div>
        
        {originalQuestion && (
          <div className="mt-4">
            <h3 className="text-sm font-medium text-gray-500 mb-1">Original Question:</h3>
            <p className="text-gray-700">{originalQuestion}</p>
          </div>
        )}
      </div>

      {/* Summary */}
      <div className="p-6 border-b border-gray-200">
        <h3 className="text-lg font-medium text-gray-800 mb-2">Summary</h3>
        <p className="text-gray-700">{feedback.summary}</p>
      </div>

      {/* Strengths */}
      <div className="border-b border-gray-200">
        <button 
          className="flex justify-between items-center w-full p-6 text-left focus:outline-none"
          onClick={() => toggleSection('strengths')}
        >
          <h3 className="text-lg font-medium text-gray-800">Strengths</h3>
          <svg 
            className={`h-5 w-5 text-gray-500 transform ${expandedSections.strengths ? 'rotate-180' : ''}`} 
            fill="none" 
            viewBox="0 0 24 24" 
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        {expandedSections.strengths && (
          <div className="px-6 pb-6">
            <ul className="list-disc list-inside space-y-2 text-gray-700">
              {feedback.strengths.map((strength, index) => (
                <li key={index}>{strength}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Areas for Improvement */}
      <div className="border-b border-gray-200">
        <button 
          className="flex justify-between items-center w-full p-6 text-left focus:outline-none"
          onClick={() => toggleSection('improvements')}
        >
          <h3 className="text-lg font-medium text-gray-800">Areas for Improvement</h3>
          <svg 
            className={`h-5 w-5 text-gray-500 transform ${expandedSections.improvements ? 'rotate-180' : ''}`} 
            fill="none" 
            viewBox="0 0 24 24" 
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        {expandedSections.improvements && (
          <div className="px-6 pb-6">
            <ul className="list-disc list-inside space-y-2 text-gray-700">
              {feedback.areasForImprovement.map((area, index) => (
                <li key={index}>{area}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Detailed Feedback */}
      <div className="border-b border-gray-200">
        <button 
          className="flex justify-between items-center w-full p-6 text-left focus:outline-none"
          onClick={() => toggleSection('detailed')}
        >
          <h3 className="text-lg font-medium text-gray-800">Detailed Assessment</h3>
          <svg 
            className={`h-5 w-5 text-gray-500 transform ${expandedSections.detailed ? 'rotate-180' : ''}`} 
            fill="none" 
            viewBox="0 0 24 24" 
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        {expandedSections.detailed && (
          <div className="px-6 pb-6">
            {feedback.detailedFeedback.map((item, index) => (
              <div key={index} className="mb-4 last:mb-0">
                <div className="flex justify-between items-center mb-2">
                  <h4 className="font-medium text-gray-800">{item.category}</h4>
                  <div className={`${getScoreBackground(item.score)} px-2 py-1 rounded`}>
                    <span className={`text-sm font-medium ${getScoreColor(item.score)}`}>
                      {item.score}/100
                    </span>
                  </div>
                </div>
                <p className="text-gray-700">{item.comment}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Suggested Answer (if available) */}
      {feedback.suggestedAnswer && (
        <div className="border-b border-gray-200">
          <button 
            className="flex justify-between items-center w-full p-6 text-left focus:outline-none"
            onClick={() => toggleSection('suggested')}
          >
            <h3 className="text-lg font-medium text-gray-800">Sample Answer</h3>
            <svg 
              className={`h-5 w-5 text-gray-500 transform ${expandedSections.suggested ? 'rotate-180' : ''}`} 
              fill="none" 
              viewBox="0 0 24 24" 
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {expandedSections.suggested && (
            <div className="px-6 pb-6">
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-gray-700 whitespace-pre-line">{feedback.suggestedAnswer}</p>
              </div>
              <p className="text-sm text-gray-500 mt-2">
                Note: This is just one example of how the question could be answered. There are many valid approaches.
              </p>
            </div>
          )}
        </div>
      )}

      {/* Actions */}
      <div className="p-6 flex justify-end">
        <Button onClick={onClose}>
          Close Feedback
        </Button>
      </div>
    </div>
  );
};

export default FeedbackDisplay;
