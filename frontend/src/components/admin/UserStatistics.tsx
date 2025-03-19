'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/Button';

export interface UserStatsData {
  totalUsers: number;
  activeUsers: number;
  newUsers: number;
  subscriptionStats: {
    free: number;
    basic: number;
    premium: number;
    enterprise: number;
  };
  interviewStats: {
    total: number;
    completed: number;
    inProgress: number;
    averageDuration: number; // in minutes
  };
  questionStats: {
    total: number;
    answeredCount: number;
    averageScore: number;
    byCategory: {
      categoryId: string;
      categoryName: string;
      count: number;
    }[];
    byDifficulty: {
      difficulty: string;
      count: number;
    }[];
  };
  revenueStats?: {
    totalRevenue: number;
    monthlyRevenue: number;
    yearlyRevenue: number;
    bySubscriptionType: {
      type: string;
      amount: number;
      userCount: number;
    }[];
  };
  retentionRate?: number; // percentage
  timeSeriesData: {
    date: string;
    users: number;
    interviews: number;
    questions: number;
  }[];
}

interface UserStatisticsProps {
  statsData: UserStatsData;
  dateRange: {
    startDate: string;
    endDate: string;
  };
  onDateRangeChange: (range: { startDate: string; endDate: string }) => void;
  onRefresh: () => void;
  isLoading?: boolean;
}

const UserStatistics: React.FC<UserStatisticsProps> = ({
  statsData,
  dateRange,
  onDateRangeChange,
  onRefresh,
  isLoading = false,
}) => {
  const [selectedTab, setSelectedTab] = useState<'overview' | 'users' | 'content' | 'revenue'>('overview');

  // Predefined date ranges
  const dateRanges = [
    { label: 'Last 7 days', days: 7 },
    { label: 'Last 30 days', days: 30 },
    { label: 'Last 90 days', days: 90 },
    { label: 'Year to date', days: 'ytd' },
    { label: 'All time', days: 'all' },
  ];

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('en-US').format(num);
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount);
  };

  const handleDateRangeClick = (days: number | string) => {
    const endDate = new Date();
    let startDate = new Date();

    if (days === 'ytd') {
      startDate = new Date(endDate.getFullYear(), 0, 1); // January 1st of current year
    } else if (days === 'all') {
      startDate = new Date(2020, 0, 1); // Use a far past date or adjust as needed
    } else if (typeof days === 'number') {
      startDate.setDate(endDate.getDate() - days);
    }

    onDateRangeChange({
      startDate: startDate.toISOString().split('T')[0],
      endDate: endDate.toISOString().split('T')[0],
    });
  };

  const calculateGrowth = (current: number, previous: number) => {
    if (previous === 0) return 100;
    const growth = ((current - previous) / previous) * 100;
    return growth;
  };

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      {/* Header */}
      <div className="bg-gray-50 p-6 border-b border-gray-200">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center">
          <div>
            <h2 className="text-xl font-semibold text-gray-800">User Statistics</h2>
            <p className="text-sm text-gray-600">
              {dateRange.startDate} to {dateRange.endDate}
            </p>
          </div>
          <div className="mt-4 md:mt-0 flex flex-wrap gap-2">
            {dateRanges.map((range) => (
              <button
                key={range.label}
                className="px-3 py-1 text-sm rounded-md border border-gray-300 hover:bg-gray-100"
                onClick={() => handleDateRangeClick(range.days)}
              >
                {range.label}
              </button>
            ))}
            <Button size="sm" onClick={onRefresh} disabled={isLoading}>
              {isLoading ? 'Refreshing...' : 'Refresh'}
            </Button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200">
        <button
          className={`px-6 py-3 font-medium text-sm focus:outline-none ${
            selectedTab === 'overview'
              ? 'border-b-2 border-blue-500 text-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
          onClick={() => setSelectedTab('overview')}
        >
          Overview
        </button>
        <button
          className={`px-6 py-3 font-medium text-sm focus:outline-none ${
            selectedTab === 'users'
              ? 'border-b-2 border-blue-500 text-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
          onClick={() => setSelectedTab('users')}
        >
          Users
        </button>
        <button
          className={`px-6 py-3 font-medium text-sm focus:outline-none ${
            selectedTab === 'content'
              ? 'border-b-2 border-blue-500 text-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
          onClick={() => setSelectedTab('content')}
        >
          Content Usage
        </button>
        {statsData.revenueStats && (
          <button
            className={`px-6 py-3 font-medium text-sm focus:outline-none ${
              selectedTab === 'revenue'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
            onClick={() => setSelectedTab('revenue')}
          >
            Revenue
          </button>
        )}
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center z-10">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      )}

      {/* Content based on selected tab */}
      <div className="p-6 relative">
        {selectedTab === 'overview' && (
          <div>
            {/* Key Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="text-sm font-medium text-gray-500">Total Users</h3>
                <p className="text-3xl font-bold text-gray-800 mt-1">{formatNumber(statsData.totalUsers)}</p>
                <div className="mt-2 flex items-center text-sm">
                  <span className="text-green-600">+{formatNumber(statsData.newUsers)}</span>
                  <span className="text-gray-600 ml-1">new users</span>
                </div>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="text-sm font-medium text-gray-500">Interviews</h3>
                <p className="text-3xl font-bold text-gray-800 mt-1">{formatNumber(statsData.interviewStats.total)}</p>
                <div className="mt-2 flex items-center text-sm">
                  <span className="text-gray-600">{formatNumber(statsData.interviewStats.completed)} completed</span>
                </div>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="text-sm font-medium text-gray-500">Questions Answered</h3>
                <p className="text-3xl font-bold text-gray-800 mt-1">{formatNumber(statsData.questionStats.answeredCount)}</p>
                <div className="mt-2 flex items-center text-sm">
                  <span className="text-gray-600">Avg. Score: {statsData.questionStats.averageScore.toFixed(1)}</span>
                </div>
              </div>

              {statsData.revenueStats ? (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="text-sm font-medium text-gray-500">Total Revenue</h3>
                  <p className="text-3xl font-bold text-gray-800 mt-1">{formatCurrency(statsData.revenueStats.totalRevenue)}</p>
                  <div className="mt-2 flex items-center text-sm">
                    <span className="text-gray-600">{formatCurrency(statsData.revenueStats.monthlyRevenue)}/month</span>
                  </div>
                </div>
              ) : (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="text-sm font-medium text-gray-500">Active Users</h3>
                  <p className="text-3xl font-bold text-gray-800 mt-1">{formatNumber(statsData.activeUsers)}</p>
                  <div className="mt-2 flex items-center text-sm">
                    <span className="text-gray-600">{((statsData.activeUsers / statsData.totalUsers) * 100).toFixed(1)}% of total</span>
                  </div>
                </div>
              )}
            </div>

            {/* Time Series Chart (simplified visualization) */}
            <div className="mb-8">
              <h3 className="text-lg font-medium text-gray-800 mb-4">Activity Over Time</h3>
              <div className="h-64 bg-gray-50 rounded-lg p-4 flex items-end justify-between">
                {statsData.timeSeriesData.map((dataPoint, index) => {
                  // Normalize values for the chart
                  const maxUsers = Math.max(...statsData.timeSeriesData.map(d => d.users));
                  const maxInterviews = Math.max(...statsData.timeSeriesData.map(d => d.interviews));
                  
                  const userHeight = (dataPoint.users / maxUsers) * 100;
                  const interviewHeight = (dataPoint.interviews / maxInterviews) * 100;

                  return (
                    <div key={index} className="flex flex-col items-center" style={{ width: `${100 / statsData.timeSeriesData.length}%` }}>
                      <div className="text-xs text-gray-500 mb-1">
                        {new Date(dataPoint.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                      </div>
                      <div className="relative w-full flex justify-center">
                        <div className="h-52 flex items-end space-x-1">
                          <div className="bg-blue-400 w-3 rounded-t-sm" style={{ height: `${userHeight}%` }}></div>
                          <div className="bg-green-400 w-3 rounded-t-sm" style={{ height: `${interviewHeight}%` }}></div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
              <div className="flex justify-center mt-2">
                <div className="flex items-center mr-4">
                  <div className="w-3 h-3 bg-blue-400 mr-1"></div>
                  <span className="text-sm text-gray-600">Users</span>
                </div>
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-green-400 mr-1"></div>
                  <span className="text-sm text-gray-600">Interviews</span>
                </div>
              </div>
            </div>

            {/* Subscription Distribution */}
            <div>
              <h3 className="text-lg font-medium text-gray-800 mb-4">Subscription Distribution</h3>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="w-full bg-gray-200 rounded-full h-2.5 mb-4 overflow-hidden">
                  {Object.entries(statsData.subscriptionStats).map(([type, count], index) => {
                    const percentage = (count / statsData.totalUsers) * 100;
                    let color = '';
                    
                    switch(type) {
                      case 'free': color = 'bg-gray-400'; break;
                      case 'basic': color = 'bg-green-400'; break;
                      case 'premium': color = 'bg-blue-500'; break;
                      case 'enterprise': color = 'bg-purple-500'; break;
                    }
                    
                    return (
                      <div 
                        key={type}
                        className={`h-2.5 ${color} inline-block`}
                        style={{ width: `${percentage}%` }}
                      ></div>
                    );
                  })}
                </div>
                
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {Object.entries(statsData.subscriptionStats).map(([type, count]) => (
                    <div key={type} className="flex items-center">
                      <div 
                        className={`w-3 h-3 mr-2 rounded-full ${
                          type === 'free' ? 'bg-gray-400' :
                          type === 'basic' ? 'bg-green-400' :
                          type === 'premium' ? 'bg-blue-500' :
                          'bg-purple-500'
                        }`}
                      ></div>
                      <div>
                        <div className="text-sm font-medium text-gray-700 capitalize">{type}</div>
                        <div className="text-sm text-gray-500">{formatNumber(count)} users</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {selectedTab === 'users' && (
          <div>
            {/* User Growth */}
            <div className="mb-8">
              <h3 className="text-lg font-medium text-gray-800 mb-4">User Growth</h3>
              <div className="bg-gray-50 rounded-lg p-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div>
                    <h4 className="text-sm font-medium text-gray-500">Total Users</h4>
                    <p className="text-3xl font-bold text-gray-800 mt-1">{formatNumber(statsData.totalUsers)}</p>
                    {statsData.retentionRate !== undefined && (
                      <div className="mt-2 text-sm text-gray-600">
                        Retention Rate: <span className="font-medium">{statsData.retentionRate.toFixed(1)}%</span>
                      </div>
                    )}
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-gray-500">Active Users</h4>
                    <p className="text-3xl font-bold text-gray-800 mt-1">{formatNumber(statsData.activeUsers)}</p>
                    <div className="mt-2 text-sm text-gray-600">
                      {((statsData.activeUsers / statsData.totalUsers) * 100).toFixed(1)}% of total users
                    </div>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-gray-500">New Users</h4>
                    <p className="text-3xl font-bold text-gray-800 mt-1">{formatNumber(statsData.newUsers)}</p>
                    <div className="mt-2 text-sm text-gray-600">
                      In selected date range
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* User Activity */}
            <div>
              <h3 className="text-lg font-medium text-gray-800 mb-4">User Activity</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-gray-50 rounded-lg p-6">
                  <h4 className="text-sm font-medium text-gray-500 mb-4">Average Activity per User</h4>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-sm text-gray-600">Interviews</span>
                        <span className="text-sm font-medium text-gray-700">
                          {(statsData.interviewStats.total / statsData.activeUsers).toFixed(1)}
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-500 h-2 rounded-full"
                          style={{ width: `${Math.min(100, (statsData.interviewStats.total / statsData.activeUsers) / 0.1 * 10)}%` }}
                        ></div>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-sm text-gray-600">Questions Answered</span>
                        <span className="text-sm font-medium text-gray-700">
                          {(statsData.questionStats.answeredCount / statsData.activeUsers).toFixed(1)}
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-green-500 h-2 rounded-full"
                          style={{ width: `${Math.min(100, (statsData.questionStats.answeredCount / statsData.activeUsers) / 0.5 * 10)}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="bg-gray-50 rounded-lg p-6">
                  <h4 className="text-sm font-medium text-gray-500 mb-4">Interview Completion Rate</h4>
                  <div className="flex items-center justify-center h-32">
                    <div className="relative w-32 h-32">
                      <svg className="w-full h-full" viewBox="0 0 36 36">
                        <path
                          d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                          fill="none"
                          stroke="#e5e7eb"
                          strokeWidth="3"
                          strokeDasharray="100, 100"
                        />
                        <path
                          d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                          fill="none"
                          stroke="#4f46e5"
                          strokeWidth="3"
                          strokeDasharray={`${(statsData.interviewStats.completed / statsData.interviewStats.total) * 100}, 100`}
                        />
                      </svg>
                      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-center">
                        <span className="text-2xl font-bold text-gray-800">
                          {((statsData.interviewStats.completed / statsData.interviewStats.total) * 100).toFixed(0)}%
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="text-center mt-4 text-sm text-gray-600">
                    <p><span className="font-medium">{formatNumber(statsData.interviewStats.completed)}</span> completed</p>
                    <p><span className="font-medium">{formatNumber(statsData.interviewStats.inProgress)}</span> in progress</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {selectedTab === 'content' && (
          <div>
            {/* Content Usage Summary */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="bg-gray-50 rounded-lg p-6">
                <h4 className="text-sm font-medium text-gray-500">Total Questions</h4>
                <p className="text-3xl font-bold text-gray-800 mt-1">{formatNumber(statsData.questionStats.total)}</p>
                <div className="mt-2 text-sm text-gray-600">
                  {formatNumber(statsData.questionStats.answeredCount)} answered
                </div>
              </div>
              <div className="bg-gray-50 rounded-lg p-6">
                <h4 className="text-sm font-medium text-gray-500">Average Score</h4>
                <p className="text-3xl font-bold text-gray-800 mt-1">{statsData.questionStats.averageScore.toFixed(1)}/100</p>
                <div className="mt-2 text-sm text-gray-600">
                  Across all answered questions
                </div>
              </div>
              <div className="bg-gray-50 rounded-lg p-6">
                <h4 className="text-sm font-medium text-gray-500">Average Interview Duration</h4>
                <p className="text-3xl font-bold text-gray-800 mt-1">{statsData.interviewStats.averageDuration} min</p>
                <div className="mt-2 text-sm text-gray-600">
                  For completed interviews
                </div>
              </div>
            </div>

            {/* Questions by Category */}
            <div className="mb-8">
              <h3 className="text-lg font-medium text-gray-800 mb-4">Questions by Category</h3>
              <div className="bg-gray-50 rounded-lg p-6">
                <div className="space-y-4">
                  {statsData.questionStats.byCategory.map((category) => (
                    <div key={category.categoryId}>
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-sm text-gray-600">{category.categoryName}</span>
                        <span className="text-sm font-medium text-gray-700">
                          {formatNumber(category.count)}
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-500 h-2 rounded-full"
                          style={{ width: `${(category.count / statsData.questionStats.total) * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Questions by Difficulty */}
            <div>
              <h3 className="text-lg font-medium text-gray-800 mb-4">Questions by Difficulty</h3>
              <div className="bg-gray-50 rounded-lg p-6">
                <div className="flex items-center justify-center">
                  <div className="grid grid-cols-3 gap-8 w-full">
                    {statsData.questionStats.byDifficulty.map((item) => {
                      const percentage = (item.count / statsData.questionStats.total) * 100;
                      let color = '';
                      
                      switch(item.difficulty.toLowerCase()) {
                        case 'easy': color = 'bg-green-500'; break;
                        case 'medium': color = 'bg-yellow-500'; break;
                        case 'hard': color = 'bg-red-500'; break;
                      }
                      
                      return (
                        <div key={item.difficulty} className="text-center">
                          <div className="relative mb-2">
                            <div className="w-full h-4 bg-gray-200 rounded-full"></div>
                            <div 
                              className={`absolute top-0 left-0 h-4 ${color} rounded-full`}
                              style={{ width: `${percentage}%` }}
                            ></div>
                          </div>
                          <p className="text-sm font-medium text-gray-700 capitalize">{item.difficulty}</p>
                          <p className="text-xs text-gray-500">{formatNumber(item.count)} questions</p>
                          <p className="text-xs text-gray-500">({percentage.toFixed(1)}%)</p>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {selectedTab === 'revenue' && statsData.revenueStats && (
          <div>
            {/* Revenue Overview */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="bg-gray-50 rounded-lg p-6">
                <h4 className="text-sm font-medium text-gray-500">Total Revenue</h4>
                <p className="text-3xl font-bold text-gray-800 mt-1">{formatCurrency(statsData.revenueStats.totalRevenue)}</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-6">
                <h4 className="text-sm font-medium text-gray-500">Monthly Revenue</h4>
                <p className="text-3xl font-bold text-gray-800 mt-1">{formatCurrency(statsData.revenueStats.monthlyRevenue)}</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-6">
                <h4 className="text-sm font-medium text-gray-500">Yearly Revenue</h4>
                <p className="text-3xl font-bold text-gray-800 mt-1">{formatCurrency(statsData.revenueStats.yearlyRevenue)}</p>
              </div>
            </div>

            {/* Revenue by Subscription Type */}
            <div>
              <h3 className="text-lg font-medium text-gray-800 mb-4">Revenue by Subscription Type</h3>
              <div className="bg-gray-50 rounded-lg p-6">
                <div className="overflow-x-auto">
                  <table className="min-w-full">
                    <thead>
                      <tr className="border-b border-gray-200">
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Subscription Type
                        </th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Users
                        </th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Revenue
                        </th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          % of Total
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {statsData.revenueStats.bySubscriptionType.map((item) => (
                        <tr key={item.type} className="border-b border-gray-200">
                          <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-800 capitalize">
                            {item.type}
                          </td>
                          <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-600">
                            {formatNumber(item.userCount)}
                          </td>
                          <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-600">
                            {formatCurrency(item.amount)}
                          </td>
                          <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-600">
                            {((item.amount / statsData.revenueStats!.totalRevenue) * 100).toFixed(1)}%
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default UserStatistics;
