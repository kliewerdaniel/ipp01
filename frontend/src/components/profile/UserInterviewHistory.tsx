'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/Button';

export interface InterviewHistoryItem {
  id: string;
  title: string;
  date: string;
  type: string; // e.g., 'technical', 'behavioral', etc.
  questionCount: number;
  duration: number; // in minutes
  status: 'completed' | 'in_progress' | 'cancelled';
  score?: number; // optional overall score
}

interface UserInterviewHistoryProps {
  interviews: InterviewHistoryItem[];
  onViewInterview: (interviewId: string) => void;
  onContinueInterview?: (interviewId: string) => void;
  isLoading?: boolean;
}

const UserInterviewHistory: React.FC<UserInterviewHistoryProps> = ({
  interviews,
  onViewInterview,
  onContinueInterview,
  isLoading = false,
}) => {
  const [filter, setFilter] = useState<'all' | 'completed' | 'in_progress'>('all');
  const [sortBy, setSortBy] = useState<'date' | 'score'>('date');

  const filteredInterviews = interviews.filter(interview => {
    if (filter === 'all') return true;
    if (filter === 'completed') return interview.status === 'completed';
    if (filter === 'in_progress') return interview.status === 'in_progress';
    return true;
  });

  const sortedInterviews = [...filteredInterviews].sort((a, b) => {
    if (sortBy === 'date') {
      return new Date(b.date).getTime() - new Date(a.date).getTime();
    } else if (sortBy === 'score' && a.score !== undefined && b.score !== undefined) {
      return b.score - a.score;
    }
    return 0;
  });

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    }).format(date);
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">Completed</span>;
      case 'in_progress':
        return <span className="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded-full">In Progress</span>;
      case 'cancelled':
        return <span className="bg-red-100 text-red-800 text-xs px-2 py-1 rounded-full">Cancelled</span>;
      default:
        return null;
    }
  };

  const getScoreColor = (score?: number) => {
    if (score === undefined) return 'text-gray-500';
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6">
        <h2 className="text-xl font-bold text-gray-800 mb-3 sm:mb-0">Interview History</h2>
        
        <div className="flex space-x-2">
          {/* Filter */}
          <select
            className="px-3 py-1.5 bg-white border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={filter}
            onChange={(e) => setFilter(e.target.value as any)}
          >
            <option value="all">All Interviews</option>
            <option value="completed">Completed</option>
            <option value="in_progress">In Progress</option>
          </select>
          
          {/* Sort */}
          <select
            className="px-3 py-1.5 bg-white border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as any)}
          >
            <option value="date">Sort by Date</option>
            <option value="score">Sort by Score</option>
          </select>
        </div>
      </div>
      
      {isLoading ? (
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      ) : sortedInterviews.length === 0 ? (
        <div className="text-center py-10 border border-dashed border-gray-300 rounded-lg">
          <p className="text-gray-500 mb-3">No interviews found</p>
          <p className="text-gray-400 text-sm">Start a new interview to build your history.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {sortedInterviews.map((interview) => (
            <div 
              key={interview.id} 
              className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex flex-col md:flex-row md:items-center justify-between">
                <div>
                  <div className="flex items-center">
                    <h3 className="text-lg font-medium text-gray-800 mr-2">{interview.title}</h3>
                    {getStatusBadge(interview.status)}
                  </div>
                  <div className="mt-1 text-sm text-gray-600">
                    {formatDate(interview.date)} • {interview.type} • {interview.questionCount} questions • {interview.duration} min
                  </div>
                </div>
                
                <div className="flex items-center mt-3 md:mt-0">
                  {interview.score !== undefined && (
                    <div className={`mr-4 font-medium ${getScoreColor(interview.score)}`}>
                      Score: {interview.score}/100
                    </div>
                  )}
                  
                  <div className="space-x-2">
                    {interview.status === 'in_progress' && onContinueInterview && (
                      <Button 
                        size="sm" 
                        onClick={() => onContinueInterview(interview.id)}
                      >
                        Continue
                      </Button>
                    )}
                    <Button 
                      variant="outline" 
                      size="sm" 
                      onClick={() => onViewInterview(interview.id)}
                    >
                      View Details
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default UserInterviewHistory;
