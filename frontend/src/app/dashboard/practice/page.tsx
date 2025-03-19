'use client';

import React, { useState } from 'react';
import QuestionSelectionInterface from '@/components/questions/QuestionSelectionInterface';
import VoiceRecordingComponent from '@/components/recording/VoiceRecordingComponent';
import PlaybackReviewInterface from '@/components/playback/PlaybackReviewInterface';
import SelfAssessmentChecklist from '@/components/assessment/SelfAssessmentChecklist';
import FeedbackDisplay, { Feedback } from '@/components/feedback/FeedbackDisplay';
import { Question } from '@/types/questions';

const PracticePage: React.FC = () => {
  // Step state for the interview flow
  const [step, setStep] = useState<'selection' | 'recording' | 'review' | 'assessment' | 'feedback'>('selection');
  
  // Selected question state
  const [selectedQuestion, setSelectedQuestion] = useState<Question | null>(null);
  
  // Recording data
  const [recordingData, setRecordingData] = useState<{
    audioBlob: Blob | null;
    audioUrl: string;
    duration: number;
  }>({
    audioBlob: null,
    audioUrl: '',
    duration: 0,
  });

  // Assessment results
  const [assessmentResults, setAssessmentResults] = useState<Record<string, boolean>>({});
  
  // Mock feedback data (would come from an API in a real app)
  const mockFeedback: Feedback = {
    overallScore: 82,
    strengths: [
      'Clear explanation of technical concepts',
      'Well-structured answer with good examples',
      'Effective use of industry terminology',
    ],
    areasForImprovement: [
      'Could provide more specific examples from your experience',
      'Consider discussing alternative approaches or trade-offs',
      'Time management - try to be more concise in your response',
    ],
    detailedFeedback: [
      {
        category: 'Technical Accuracy',
        score: 85,
        comment: 'Your explanation was technically accurate and demonstrated good understanding of the concepts involved.',
      },
      {
        category: 'Communication',
        score: 78,
        comment: 'You communicated clearly, but could improve by using more concrete examples to illustrate your points.',
      },
      {
        category: 'Problem Solving',
        score: 90,
        comment: 'You demonstrated a methodical approach to problem-solving with good consideration of edge cases.',
      },
      {
        category: 'Completeness',
        score: 75,
        comment: 'Your answer covered the main points but missed some important considerations about scalability.',
      },
    ],
    summary: 'Overall, this was a strong response that demonstrated good technical knowledge and communication skills. Your answer was well-structured and covered most key points. To improve further, focus on providing more specific examples from your experience and discussing potential trade-offs or alternative approaches.',
    suggestedAnswer: 'A strong answer to this question would include a clear explanation of the linked list data structure, the approach to reversing it (iterative or recursive), time and space complexity analysis, and consideration of edge cases such as empty lists or single-node lists.\n\nExample: "To reverse a linked list, I would use an iterative approach with three pointers: previous, current, and next. Starting with previous as null and current at the head, I\'d iterate through the list, saving the next node, then reversing the current node\'s pointer to previous, and advancing the pointers. This approach has O(n) time complexity and O(1) space complexity..."',
  };

  // Loading states
  const [isFeedbackLoading, setIsFeedbackLoading] = useState(false);

  // Handlers for user actions
  const handleSelectQuestion = (questionId: string) => {
    // In a real app, this would fetch the question by ID
    // For demo, we'll use mock data
    const mockQuestion: Question = {
      id: questionId,
      content: 'Implement a function to reverse a linked list',
      questionType: 'coding',
      difficulty: 'medium',
      category: 'data-structures',
      interviewId: 'interview1',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    
    setSelectedQuestion(mockQuestion);
    setStep('recording');
  };

  const handleRecordingComplete = (audioBlob: Blob, duration: number) => {
    // Create URL for the audio blob
    const audioUrl = URL.createObjectURL(audioBlob);
    
    setRecordingData({
      audioBlob,
      audioUrl,
      duration,
    });
    
    setStep('review');
  };

  const handleReRecord = () => {
    // Clean up previous recording URL
    if (recordingData.audioUrl) {
      URL.revokeObjectURL(recordingData.audioUrl);
    }
    
    setRecordingData({
      audioBlob: null,
      audioUrl: '',
      duration: 0,
    });
    
    setStep('recording');
  };

  const handleSubmitRecording = () => {
    setStep('assessment');
  };

  const handleRequestFeedback = () => {
    setIsFeedbackLoading(true);
    
    // Simulate API call to get feedback
    setTimeout(() => {
      setIsFeedbackLoading(false);
      setStep('feedback');
    }, 2000);
  };

  const handleAssessmentComplete = (assessment: Record<string, boolean>) => {
    setAssessmentResults(assessment);
  };

  const handleCloseFeedback = () => {
    // Reset the flow to select a new question
    if (recordingData.audioUrl) {
      URL.revokeObjectURL(recordingData.audioUrl);
    }
    
    setSelectedQuestion(null);
    setRecordingData({
      audioBlob: null,
      audioUrl: '',
      duration: 0,
    });
    setAssessmentResults({});
    setStep('selection');
  };

  // Render different components based on the current step
  const renderStepContent = () => {
    switch (step) {
      case 'selection':
        return (
          <QuestionSelectionInterface
            onSelectQuestion={handleSelectQuestion}
          />
        );
      
      case 'recording':
        if (!selectedQuestion) return null;
        return (
          <VoiceRecordingComponent
            question={selectedQuestion}
            onRecordingComplete={handleRecordingComplete}
            maxDuration={180} // 3 minutes
            onCancel={() => setStep('selection')}
          />
        );
      
      case 'review':
        if (!selectedQuestion || !recordingData.audioUrl) return null;
        return (
          <PlaybackReviewInterface
            question={selectedQuestion}
            audioUrl={recordingData.audioUrl}
            duration={recordingData.duration}
            transcript="In this implementation, I would use an iterative approach to reverse a linked list. First, I'd initialize three pointers: prev set to null, current set to the head, and next. Then I'd iterate through the list, for each node saving the next node, reversing the current node's pointer to prev, and advancing the pointers. This has O(n) time complexity and O(1) space complexity."
            onReRecord={handleReRecord}
            onSubmit={handleSubmitRecording}
            onRequestFeedback={handleRequestFeedback}
          />
        );
      
      case 'assessment':
        if (!selectedQuestion) return null;
        return (
          <div className="space-y-6">
            <SelfAssessmentChecklist
              question={selectedQuestion}
              onAssessmentComplete={handleAssessmentComplete}
            />
            
            <div className="flex justify-end">
              <button
                onClick={handleRequestFeedback}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                Get AI Feedback
              </button>
            </div>
          </div>
        );
      
      case 'feedback':
        if (!selectedQuestion) return null;
        return (
          <FeedbackDisplay
            feedback={mockFeedback}
            isLoading={isFeedbackLoading}
            originalQuestion={selectedQuestion.content}
            onClose={handleCloseFeedback}
          />
        );
      
      default:
        return null;
    }
  };

  // Track progress
  const stepNumbers: Record<typeof step, number> = {
    selection: 1,
    recording: 2,
    review: 3,
    assessment: 4,
    feedback: 5,
  };

  const currentStepNumber = stepNumbers[step];

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-5xl mx-auto">
        {/* Progress Steps */}
        {step !== 'selection' && (
          <div className="mb-8">
            <div className="flex items-center justify-between">
              {['Question', 'Record', 'Review', 'Assess', 'Feedback'].map((label, index) => {
                const stepNum = index + 1;
                const isActive = stepNum === currentStepNumber;
                const isCompleted = stepNum < currentStepNumber;
                
                return (
                  <div 
                    key={label} 
                    className={`flex flex-col items-center w-1/5 ${
                      isActive || isCompleted ? 'text-blue-600' : 'text-gray-400'
                    }`}
                  >
                    <div className={`flex items-center justify-center w-8 h-8 rounded-full border-2 ${
                      isActive 
                        ? 'border-blue-600 bg-blue-600 text-white'
                        : isCompleted
                        ? 'border-blue-600 bg-white text-blue-600'
                        : 'border-gray-300 bg-white text-gray-400'
                    }`}>
                      {isCompleted ? (
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                        </svg>
                      ) : (
                        stepNum
                      )}
                    </div>
                    <span className="mt-2 text-sm font-medium">{label}</span>
                  </div>
                );
              })}
            </div>
            
            <div className="relative flex items-center justify-between mt-2 mb-6">
              <div className="absolute inset-x-0 top-1/2 h-0.5 -translate-y-1/2 bg-gray-200"></div>
              <div 
                className="absolute left-0 top-1/2 h-0.5 -translate-y-1/2 bg-blue-600 transition-all duration-300" 
                style={{ width: `${(currentStepNumber - 1) * 25}%` }}
              ></div>
            </div>
          </div>
        )}
        
        {/* Main Content */}
        <div>
          {renderStepContent()}
        </div>
      </div>
    </div>
  );
};

export default PracticePage;
