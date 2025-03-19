'use client';

import React, { useState } from 'react';
import UserProfileHeader, { UserProfile } from '@/components/profile/UserProfileHeader';
import UserInterviewHistory, { InterviewHistoryItem } from '@/components/profile/UserInterviewHistory';
import { useRouter } from 'next/navigation';

const ProfilePage: React.FC = () => {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);

  // Mock user profile data
  const userProfile: UserProfile = {
    id: 'user-123',
    name: 'Alex Johnson',
    email: 'alex.johnson@example.com',
    avatarUrl: 'https://randomuser.me/api/portraits/men/32.jpg',
    role: 'user',
    joinDate: '2024-08-15T10:30:00Z',
    interviewCount: 24,
    questionsAnswered: 148,
    subscriptionStatus: 'premium',
    subscriptionEndDate: '2025-05-15T23:59:59Z',
  };

  // Mock interview history data
  const interviewHistory: InterviewHistoryItem[] = [
    {
      id: 'interview-1',
      title: 'Frontend Developer Interview Prep',
      date: '2025-03-15T14:30:00Z',
      type: 'technical',
      questionCount: 10,
      duration: 45,
      status: 'completed',
      score: 87,
    },
    {
      id: 'interview-2',
      title: 'Leadership Skills Assessment',
      date: '2025-03-05T09:15:00Z',
      type: 'behavioral',
      questionCount: 8,
      duration: 32,
      status: 'completed',
      score: 92,
    },
    {
      id: 'interview-3',
      title: 'System Design Interview',
      date: '2025-02-28T11:00:00Z',
      type: 'system_design',
      questionCount: 5,
      duration: 55,
      status: 'completed',
      score: 78,
    },
    {
      id: 'interview-4',
      title: 'Full Stack Developer Practice',
      date: '2025-03-18T16:00:00Z',
      type: 'technical',
      questionCount: 12,
      duration: 60,
      status: 'in_progress',
    },
  ];

  // Handlers for user actions
  const handleEditProfile = () => {
    // In a real app, this would show a modal or navigate to edit profile page
    console.log('Edit profile clicked');
    // For demo purposes, we'll just show a loading state briefly
    setIsLoading(true);
    setTimeout(() => setIsLoading(false), 1000);
  };

  const handleManageSubscription = () => {
    // Navigate to subscription management page
    router.push('/dashboard/subscription');
  };

  const handleViewInterview = (interviewId: string) => {
    // In a real app, this would navigate to an interview details page
    console.log('View interview details for:', interviewId);
    // Mock navigation - this could be replaced with router.push
    alert(`Viewing details for interview ${interviewId}`);
  };

  const handleContinueInterview = (interviewId: string) => {
    // In a real app, this would navigate to the interview session
    console.log('Continue interview:', interviewId);
    // Mock navigation
    alert(`Continuing interview ${interviewId}`);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-5xl mx-auto space-y-8">
        <h1 className="text-2xl font-bold text-gray-800 mb-6">Your Profile</h1>
        
        {/* Profile Header */}
        <div className="mb-8">
          <UserProfileHeader
            profile={userProfile}
            onEditProfile={handleEditProfile}
            onManageSubscription={handleManageSubscription}
          />
        </div>
        
        {/* Interview History */}
        <div>
          <UserInterviewHistory
            interviews={interviewHistory}
            onViewInterview={handleViewInterview}
            onContinueInterview={handleContinueInterview}
            isLoading={isLoading}
          />
        </div>
        
        {/* Stats Summary (optional section) */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-medium text-gray-800 mb-2">Performance</h3>
            <div className="text-3xl font-bold text-blue-600">
              85
              <span className="text-sm text-gray-500 font-normal ml-1">/100</span>
            </div>
            <p className="text-sm text-gray-600 mt-1">Average score across all interviews</p>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-medium text-gray-800 mb-2">Skills</h3>
            <div className="space-y-2 mt-2">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Technical</span>
                  <span className="text-gray-800 font-medium">92%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-1.5">
                  <div className="bg-blue-600 h-1.5 rounded-full" style={{ width: '92%' }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Communication</span>
                  <span className="text-gray-800 font-medium">85%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-1.5">
                  <div className="bg-blue-600 h-1.5 rounded-full" style={{ width: '85%' }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Problem Solving</span>
                  <span className="text-gray-800 font-medium">78%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-1.5">
                  <div className="bg-blue-600 h-1.5 rounded-full" style={{ width: '78%' }}></div>
                </div>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-medium text-gray-800 mb-2">Activity</h3>
            <div className="flex items-center mb-4">
              <div className="text-3xl font-bold text-gray-800">{userProfile.questionsAnswered}</div>
              <div className="ml-2 text-sm text-gray-600">Questions<br />answered</div>
            </div>
            <div className="text-sm text-gray-600">
              Last interview: {new Date(interviewHistory[0].date).toLocaleDateString()}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
