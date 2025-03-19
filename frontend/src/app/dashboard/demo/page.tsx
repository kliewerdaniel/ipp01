'use client';

import React, { useState } from 'react';
import QuestionSelectionInterface from '@/components/questions/QuestionSelectionInterface';
import VoiceRecordingComponent from '@/components/recording/VoiceRecordingComponent';
import PlaybackReviewInterface from '@/components/playback/PlaybackReviewInterface';
import SelfAssessmentChecklist from '@/components/assessment/SelfAssessmentChecklist';
import FeedbackDisplay, { Feedback } from '@/components/feedback/FeedbackDisplay';
import UserProfileHeader from '@/components/profile/UserProfileHeader';
import UserInterviewHistory from '@/components/profile/UserInterviewHistory';
import SubscriptionPlans, { PlanFeature, SubscriptionPlan } from '@/components/subscription/SubscriptionPlans';
import { Question } from '@/types/questions';

// Mock data for demo
const mockQuestion: Question = {
  id: '1',
  content: 'Describe a situation where you had to solve a complex problem. What was your approach and what was the outcome?',
  questionType: 'behavioral',
  difficulty: 'medium',
  category: 'problem-solving',
  interviewId: 'interview1',
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
};

const mockFeedback: Feedback = {
  overallScore: 85,
  strengths: [
    'Clear explanation of the problem context',
    'Structured approach to problem-solving',
    'Good communication of technical concepts',
    'Demonstrated teamwork and collaboration'
  ],
  areasForImprovement: [
    'Could provide more specific metrics on the outcome',
    'Consider discussing alternative approaches you considered',
    'More emphasis on your specific contributions'
  ],
  detailedFeedback: [
    { category: 'Clarity', score: 90, comment: 'Your explanation was very clear and well-articulated.' },
    { category: 'Structure', score: 85, comment: 'Good use of the STAR method, with a logical flow to your answer.' },
    { category: 'Relevance', score: 80, comment: 'The example was relevant, though could be more tailored to the question.' },
    { category: 'Impact', score: 75, comment: 'You described the outcome, but could have emphasized the impact more strongly.' },
  ],
  summary: 'Overall, this was a strong response that demonstrated your problem-solving abilities and teamwork skills. Your structured approach and clear communication were particularly effective. To improve, focus more on quantifying outcomes and highlighting your specific contributions.',
  suggestedAnswer: 'At my previous company, we faced an issue where our application response times had increased by 40% over a month, affecting user experience. As the lead developer, I first organized a cross-functional team to investigate, including backend, frontend, and infrastructure specialists.\n\nI established a methodical approach: we collected performance metrics, identified bottlenecks through log analysis, and created a test environment to reproduce the issues. The data revealed three key problems: inefficient database queries, memory leaks in our caching layer, and unoptimized frontend rendering.\n\nI prioritized these issues based on impact and assigned specialized team members to each area. I personally tackled the database queries, implementing indexing strategies and query optimizations, while guiding others on their areas.\n\nThe result was a 60% improvement in response times, exceeding our initial performance. We also implemented monitoring tools to prevent future issues and documented our approach for the team. This experience taught me the value of structured problem analysis and collaborative problem-solving.'
};

const mockUserProfile = {
  id: 'user1',
  name: 'Alex Johnson',
  email: 'alex.johnson@example.com',
  avatarUrl: 'https://randomuser.me/api/portraits/men/32.jpg',
  role: 'user' as const,
  joinDate: '2023-04-15T12:00:00Z',
  interviewCount: 24,
  questionsAnswered: 152,
  subscriptionStatus: 'premium' as const,
  subscriptionEndDate: '2025-04-15T12:00:00Z',
};

const mockInterviewHistory = [
  {
    id: 'int1',
    title: 'Full Stack Developer Practice',
    date: '2025-03-15T14:30:00Z',
    type: 'Technical',
    questionCount: 8,
    duration: 45,
    status: 'completed' as const,
    score: 82,
  },
  {
    id: 'int2',
    title: 'Leadership Assessment',
    date: '2025-03-10T09:15:00Z',
    type: 'Behavioral',
    questionCount: 5,
    duration: 30,
    status: 'completed' as const,
    score: 91,
  },
  {
    id: 'int3',
    title: 'System Design Interview',
    date: '2025-03-05T16:00:00Z',
    type: 'System Design',
    questionCount: 3,
    duration: 60,
    status: 'in_progress' as const,
  },
];

const mockSubscriptionPlans: SubscriptionPlan[] = [
  {
    id: 'free',
    name: 'Free',
    description: 'Basic interview practice for casual users',
    price: 0,
    features: [
      { name: 'Basic question library', included: true },
      { name: 'Limited practice sessions', included: true, limit: '5/month' },
      { name: 'AI feedback on responses', included: false },
      { name: 'Personalized question recommendations', included: false },
      { name: 'Progress tracking', included: false },
    ],
  },
  {
    id: 'basic',
    name: 'Basic',
    description: 'Essential tools for serious job seekers',
    price: 1499, // $14.99
    yearlyDiscount: 15,
    features: [
      { name: 'Full question library', included: true },
      { name: 'Unlimited practice sessions', included: true },
      { name: 'Basic AI feedback', included: true },
      { name: 'Personalized question recommendations', included: false },
      { name: 'Progress tracking', included: true },
    ],
    isPopular: true,
  },
  {
    id: 'premium',
    name: 'Premium',
    description: 'Comprehensive preparation for professionals',
    price: 2499, // $24.99
    yearlyDiscount: 20,
    features: [
      { name: 'Full question library', included: true },
      { name: 'Unlimited practice sessions', included: true },
      { name: 'Advanced AI feedback', included: true },
      { name: 'Personalized question recommendations', included: true },
      { name: 'Detailed progress analytics', included: true },
      { name: 'Mock interviews with industry experts', included: true, limit: '2/month' },
    ],
  },
];

// Demo page component
export default function DemoPage() {
  const [activeSection, setActiveSection] = useState<
    'questionSelection' | 
    'recording' | 
    'playback' | 
    'assessment' | 
    'feedback' | 
    'profile' | 
    'subscription'
  >('questionSelection');

  const [selectedQuestion, setSelectedQuestion] = useState<Question | null>(null);
  const [recordedAudioUrl, setRecordedAudioUrl] = useState<string | null>(null);
  const [recordedDuration, setRecordedDuration] = useState<number>(0);
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('monthly');

  const handleQuestionSelect = (questionId: string) => {
    setSelectedQuestion(mockQuestion);
    setActiveSection('recording');
  };

  const handleRecordingComplete = (audioBlob: Blob, duration: number) => {
    // Create URL for the audio blob
    const url = URL.createObjectURL(audioBlob);
    setRecordedAudioUrl(url);
    setRecordedDuration(duration);
    setActiveSection('playback');
  };

  const handleRequestFeedback = () => {
    setActiveSection('assessment');
  };

  const handleAssessmentComplete = () => {
    setActiveSection('feedback');
  };

  const resetDemo = () => {
    setSelectedQuestion(null);
    if (recordedAudioUrl) {
      URL.revokeObjectURL(recordedAudioUrl);
    }
    setRecordedAudioUrl(null);
    setRecordedDuration(0);
    setActiveSection('questionSelection');
  };

  return (
    <div className="max-w-5xl mx-auto pb-20">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">Interactive Component Demo</h1>
        <p className="text-gray-600">
          Explore the various components of the interview preparation platform.
        </p>
      </div>

      {/* Navigation */}
      <div className="mb-8 overflow-x-auto">
        <div className="flex border-b border-gray-200 min-w-max">
          <button
            className={`px-4 py-2 font-medium text-sm focus:outline-none ${
              activeSection === 'questionSelection'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
            onClick={() => setActiveSection('questionSelection')}
          >
            Question Selection
          </button>
          <button
            className={`px-4 py-2 font-medium text-sm focus:outline-none ${
              activeSection === 'recording'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
            onClick={() => selectedQuestion && setActiveSection('recording')}
            disabled={!selectedQuestion}
          >
            Voice Recording
          </button>
          <button
            className={`px-4 py-2 font-medium text-sm focus:outline-none ${
              activeSection === 'playback'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
            onClick={() => recordedAudioUrl && setActiveSection('playback')}
            disabled={!recordedAudioUrl}
          >
            Playback & Review
          </button>
          <button
            className={`px-4 py-2 font-medium text-sm focus:outline-none ${
              activeSection === 'assessment'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
            onClick={() => recordedAudioUrl && setActiveSection('assessment')}
            disabled={!recordedAudioUrl}
          >
            Self Assessment
          </button>
          <button
            className={`px-4 py-2 font-medium text-sm focus:outline-none ${
              activeSection === 'feedback'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
            onClick={() => recordedAudioUrl && setActiveSection('feedback')}
            disabled={!recordedAudioUrl}
          >
            AI Feedback
          </button>
          <button
            className={`px-4 py-2 font-medium text-sm focus:outline-none ${
              activeSection === 'profile'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
            onClick={() => setActiveSection('profile')}
          >
            User Profile
          </button>
          <button
            className={`px-4 py-2 font-medium text-sm focus:outline-none ${
              activeSection === 'subscription'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
            onClick={() => setActiveSection('subscription')}
          >
            Subscription
          </button>
        </div>
      </div>

      {/* Content based on active section */}
      <div>
        {activeSection === 'questionSelection' && (
          <QuestionSelectionInterface onSelectQuestion={handleQuestionSelect} />
        )}

        {activeSection === 'recording' && selectedQuestion && (
          <VoiceRecordingComponent 
            question={selectedQuestion}
            onRecordingComplete={handleRecordingComplete}
            onCancel={resetDemo}
          />
        )}

        {activeSection === 'playback' && selectedQuestion && recordedAudioUrl && (
          <PlaybackReviewInterface
            question={selectedQuestion}
            audioUrl={recordedAudioUrl}
            duration={recordedDuration}
            onReRecord={resetDemo}
            onRequestFeedback={handleRequestFeedback}
          />
        )}

        {activeSection === 'assessment' && selectedQuestion && (
          <div>
            <SelfAssessmentChecklist 
              question={selectedQuestion}
              onAssessmentComplete={handleAssessmentComplete}
            />
            <div className="mt-4 flex justify-end">
              <button
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                onClick={() => setActiveSection('feedback')}
              >
                Continue to Feedback
              </button>
            </div>
          </div>
        )}

        {activeSection === 'feedback' && selectedQuestion && (
          <FeedbackDisplay 
            feedback={mockFeedback}
            originalQuestion={selectedQuestion.content}
            onClose={resetDemo}
          />
        )}

        {activeSection === 'profile' && (
          <div className="space-y-8">
            <UserProfileHeader 
              profile={mockUserProfile}
              onEditProfile={() => {}}
              onManageSubscription={() => setActiveSection('subscription')}
            />
            <UserInterviewHistory 
              interviews={mockInterviewHistory}
              onViewInterview={() => {}}
              onContinueInterview={() => {}}
            />
          </div>
        )}

        {activeSection === 'subscription' && (
          <SubscriptionPlans
            plans={mockSubscriptionPlans}
            currentPlanId="premium" 
            billingCycle={billingCycle}
            onBillingCycleChange={setBillingCycle}
            onSelectPlan={() => {}}
          />
        )}
      </div>
    </div>
  );
}
