'use client';

import React, { useState } from 'react';
import QuestionManagement from './QuestionManagement';
import AssessmentCriteriaManager from './AssessmentCriteriaManager';
import UserStatistics from './UserStatistics';
import ProductCloneManager from './ProductCloneManager';
import { Question, Category, QuestionType } from '@/types/questions';
import { AssessmentCriteria } from './AssessmentCriteriaManager';
import { UserStatsData } from './UserStatistics';
import { ProductTemplate } from './ProductCloneManager';

interface AdminPanelProps {
  initialActiveTab?: 'questions' | 'criteria' | 'statistics' | 'clones';
}

const AdminPanel: React.FC<AdminPanelProps> = ({
  initialActiveTab = 'questions'
}) => {
  const [activeTab, setActiveTab] = useState<'questions' | 'criteria' | 'statistics' | 'clones'>(initialActiveTab);
  const [isLoading, setIsLoading] = useState(false);

  // Mock data - would be replaced with actual API calls
  const mockQuestions: Question[] = [
    {
      id: '1',
      content: 'Implement a function to reverse a linked list',
      questionType: 'coding',
      difficulty: 'medium',
      category: 'data-structures',
      interviewId: 'interview1',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    },
    {
      id: '2',
      content: 'Describe a time when you had to deal with a team conflict',
      questionType: 'behavioral',
      difficulty: 'easy',
      category: 'leadership',
      interviewId: 'interview1',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    },
  ];

  const mockCategories: Category[] = [
    { id: 'algorithms', name: 'Algorithms', questionCount: 15 },
    { id: 'data-structures', name: 'Data Structures', questionCount: 12 },
    { id: 'leadership', name: 'Leadership', questionCount: 10 },
  ];

  const mockAssessmentCriteria: AssessmentCriteria[] = [
    {
      id: '1',
      name: 'Technical Interview Assessment',
      questionType: 'technical',
      criteria: [
        { id: '1-1', label: 'Technical Accuracy', description: 'Correctness of technical information', weight: 30 },
        { id: '1-2', label: 'Communication', description: 'Clarity of explanation', weight: 40 },
        { id: '1-3', label: 'Problem Solving', description: 'Approach to solving the problem', weight: 30 },
      ],
      isDefault: true,
    },
    {
      id: '2',
      name: 'Behavioral Interview Assessment',
      questionType: 'behavioral',
      criteria: [
        { id: '2-1', label: 'Situation Description', description: 'Clear explanation of the situation', weight: 20 },
        { id: '2-2', label: 'Action Taken', description: 'Appropriate actions described', weight: 40 },
        { id: '2-3', label: 'Results Achieved', description: 'Quantifiable results mentioned', weight: 40 },
      ],
    },
  ];

  const mockStatsData: UserStatsData = {
    totalUsers: 1250,
    activeUsers: 875,
    newUsers: 68,
    subscriptionStats: {
      free: 750,
      basic: 320,
      premium: 150,
      enterprise: 30,
    },
    interviewStats: {
      total: 3680,
      completed: 2845,
      inProgress: 835,
      averageDuration: 24, // minutes
    },
    questionStats: {
      total: 230,
      answeredCount: 28950,
      averageScore: 76.4,
      byCategory: [
        { categoryId: 'algorithms', categoryName: 'Algorithms', count: 65 },
        { categoryId: 'data-structures', categoryName: 'Data Structures', count: 45 },
        { categoryId: 'system-design', categoryName: 'System Design', count: 30 },
        { categoryId: 'leadership', categoryName: 'Leadership', count: 40 },
        { categoryId: 'problem-solving', categoryName: 'Problem Solving', count: 50 },
      ],
      byDifficulty: [
        { difficulty: 'easy', count: 85 },
        { difficulty: 'medium', count: 100 },
        { difficulty: 'hard', count: 45 },
      ],
    },
    revenueStats: {
      totalRevenue: 58750.00,
      monthlyRevenue: 6850.00,
      yearlyRevenue: 82200.00,
      bySubscriptionType: [
        { type: 'basic', amount: 12800.00, userCount: 320 },
        { type: 'premium', amount: 36000.00, userCount: 150 },
        { type: 'enterprise', amount: 9950.00, userCount: 30 },
      ],
    },
    retentionRate: 78.5,
    timeSeriesData: [
      { date: '2025-02-19', users: 45, interviews: 186, questions: 1254 },
      { date: '2025-02-26', users: 52, interviews: 205, questions: 1390 },
      { date: '2025-03-05', users: 48, interviews: 193, questions: 1302 },
      { date: '2025-03-12', users: 63, interviews: 231, questions: 1485 },
      { date: '2025-03-19', users: 68, interviews: 245, questions: 1528 },
    ],
  };

  const mockProductTemplates: ProductTemplate[] = [
    {
      id: 'template-1',
      name: 'Software Engineering Interview',
      description: 'Preparation for software engineering technical interviews',
      features: ['Technical Questions', 'Coding Challenges', 'System Design'],
      questionCount: 120,
      createdAt: '2024-09-15T12:00:00Z',
    },
    {
      id: 'template-2',
      name: 'Product Management Interview',
      description: 'Preparation for product management interviews',
      features: ['Product Strategy', 'Market Analysis', 'User Stories'],
      questionCount: 85,
      createdAt: '2024-10-20T09:30:00Z',
    },
  ];

  const mockExistingClones: ProductTemplate[] = [
    {
      id: 'template-1-clone-1',
      name: 'Frontend Developer Interview Prep',
      description: 'Focused on React, JavaScript, and frontend system design',
      features: ['Technical Questions', 'Coding Challenges', 'Frontend Design'],
      questionCount: 75,
      createdAt: '2025-01-10T14:20:00Z',
    },
  ];

  // Mock handlers - would be replaced with actual API calls
  const handleAddQuestion = (question: Omit<Question, 'id' | 'createdAt' | 'updatedAt'>) => {
    setIsLoading(true);
    // Simulate API call
    setTimeout(() => {
      setIsLoading(false);
      // Here you would normally update state with the new question from the API
    }, 1000);
  };

  const handleUpdateQuestion = (id: string, question: Partial<Question>) => {
    setIsLoading(true);
    // Simulate API call
    setTimeout(() => {
      setIsLoading(false);
      // Here you would normally update state with the updated question from the API
    }, 1000);
  };

  const handleDeleteQuestion = (id: string) => {
    setIsLoading(true);
    // Simulate API call
    setTimeout(() => {
      setIsLoading(false);
      // Here you would normally update state by removing the deleted question
    }, 1000);
  };

  const handleAddCategory = (category: Omit<Category, 'id'>) => {
    setIsLoading(true);
    // Simulate API call
    setTimeout(() => {
      setIsLoading(false);
      // Here you would normally update state with the new category from the API
    }, 1000);
  };

  const handleUpdateCategory = (id: string, category: Partial<Category>) => {
    setIsLoading(true);
    // Simulate API call
    setTimeout(() => {
      setIsLoading(false);
      // Here you would normally update state with the updated category from the API
    }, 1000);
  };

  const handleDeleteCategory = (id: string) => {
    setIsLoading(true);
    // Simulate API call
    setTimeout(() => {
      setIsLoading(false);
      // Here you would normally update state by removing the deleted category
    }, 1000);
  };

  const handleAddCriteria = (criteria: Omit<AssessmentCriteria, 'id'>) => {
    setIsLoading(true);
    // Simulate API call
    setTimeout(() => {
      setIsLoading(false);
      // Here you would normally update state with the new criteria from the API
    }, 1000);
  };

  const handleUpdateCriteria = (id: string, criteria: Partial<AssessmentCriteria>) => {
    setIsLoading(true);
    // Simulate API call
    setTimeout(() => {
      setIsLoading(false);
      // Here you would normally update state with the updated criteria from the API
    }, 1000);
  };

  const handleDeleteCriteria = (id: string) => {
    setIsLoading(true);
    // Simulate API call
    setTimeout(() => {
      setIsLoading(false);
      // Here you would normally update state by removing the deleted criteria
    }, 1000);
  };

  const handleDateRangeChange = (range: { startDate: string; endDate: string }) => {
    setIsLoading(true);
    // Simulate API call
    setTimeout(() => {
      setIsLoading(false);
      // Here you would normally update stats data from the API
    }, 1000);
  };

  const handleRefreshStats = () => {
    setIsLoading(true);
    // Simulate API call
    setTimeout(() => {
      setIsLoading(false);
      // Here you would normally update stats data from the API
    }, 1000);
  };

  const handleCreateClone = async (
    templateId: string, 
    name: string, 
    description: string, 
    settings?: Record<string, any>
  ) => {
    setIsLoading(true);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500));
    setIsLoading(false);
    // Here you would normally update state with the new clone from the API
  };

  const handleDeleteClone = async (cloneId: string) => {
    setIsLoading(true);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    setIsLoading(false);
    // Here you would normally update state by removing the deleted clone
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">Admin Dashboard</h1>
      
      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            className={`pb-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'questions'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
            onClick={() => setActiveTab('questions')}
          >
            Question Management
          </button>
          <button
            className={`pb-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'criteria'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
            onClick={() => setActiveTab('criteria')}
          >
            Assessment Criteria
          </button>
          <button
            className={`pb-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'statistics'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
            onClick={() => setActiveTab('statistics')}
          >
            User Statistics
          </button>
          <button
            className={`pb-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'clones'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
            onClick={() => setActiveTab('clones')}
          >
            Product Clones
          </button>
        </nav>
      </div>
      
      {/* Tab Content */}
      <div>
        {activeTab === 'questions' && (
          <QuestionManagement
            questions={mockQuestions}
            categories={mockCategories}
            onAddQuestion={handleAddQuestion}
            onUpdateQuestion={handleUpdateQuestion}
            onDeleteQuestion={handleDeleteQuestion}
            onAddCategory={handleAddCategory}
            onUpdateCategory={handleUpdateCategory}
            onDeleteCategory={handleDeleteCategory}
            isLoading={isLoading}
          />
        )}
        
        {activeTab === 'criteria' && (
          <AssessmentCriteriaManager
            assessmentCriteria={mockAssessmentCriteria}
            onAddCriteria={handleAddCriteria}
            onUpdateCriteria={handleUpdateCriteria}
            onDeleteCriteria={handleDeleteCriteria}
            isLoading={isLoading}
          />
        )}
        
        {activeTab === 'statistics' && (
          <UserStatistics
            statsData={mockStatsData}
            dateRange={{
              startDate: '2025-02-19',
              endDate: '2025-03-19',
            }}
            onDateRangeChange={handleDateRangeChange}
            onRefresh={handleRefreshStats}
            isLoading={isLoading}
          />
        )}
        
        {activeTab === 'clones' && (
          <ProductCloneManager
            templates={mockProductTemplates}
            existingClones={mockExistingClones}
            onCreateClone={handleCreateClone}
            onDeleteClone={handleDeleteClone}
            isLoading={isLoading}
          />
        )}
      </div>
    </div>
  );
};

export default AdminPanel;
