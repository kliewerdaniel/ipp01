'use client';

import React from 'react';
import { Button } from '@/components/ui/Button';

export interface UserProfile {
  id: string;
  name: string;
  email: string;
  avatarUrl?: string;
  role: 'user' | 'admin';
  joinDate: string;
  interviewCount?: number;
  questionsAnswered?: number;
  subscriptionStatus?: 'free' | 'basic' | 'premium' | 'enterprise';
  subscriptionEndDate?: string;
}

interface UserProfileHeaderProps {
  profile: UserProfile;
  onEditProfile?: () => void;
  onManageSubscription?: () => void;
}

const UserProfileHeader: React.FC<UserProfileHeaderProps> = ({
  profile,
  onEditProfile,
  onManageSubscription,
}) => {
  const getSubscriptionBadge = () => {
    switch (profile.subscriptionStatus) {
      case 'premium':
        return <span className="bg-purple-100 text-purple-800 text-xs px-2 py-1 rounded-full">Premium</span>;
      case 'enterprise':
        return <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">Enterprise</span>;
      case 'basic':
        return <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">Basic</span>;
      default:
        return <span className="bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded-full">Free</span>;
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    }).format(date);
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex flex-col md:flex-row md:items-center">
        {/* Avatar and name */}
        <div className="flex items-center mb-4 md:mb-0">
          <div className="relative">
            {profile.avatarUrl ? (
              <img 
                src={profile.avatarUrl} 
                alt={profile.name} 
                className="w-20 h-20 rounded-full object-cover border-2 border-gray-200"
              />
            ) : (
              <div className="w-20 h-20 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 text-2xl font-bold border-2 border-gray-200">
                {profile.name.charAt(0).toUpperCase()}
              </div>
            )}
            {profile.role === 'admin' && (
              <div className="absolute bottom-0 right-0 bg-blue-500 text-white text-xs p-1 rounded-full">
                Admin
              </div>
            )}
          </div>
          
          <div className="ml-4">
            <h2 className="text-2xl font-bold text-gray-800">{profile.name}</h2>
            <p className="text-gray-600">{profile.email}</p>
            <div className="mt-1 flex items-center space-x-2">
              {getSubscriptionBadge()}
              <span className="text-xs text-gray-500">Member since {formatDate(profile.joinDate)}</span>
            </div>
          </div>
        </div>
        
        {/* Stats and actions */}
        <div className="md:ml-auto flex flex-col md:items-end">
          <div className="flex space-x-6 mb-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-800">{profile.interviewCount || 0}</p>
              <p className="text-sm text-gray-600">Interviews</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-800">{profile.questionsAnswered || 0}</p>
              <p className="text-sm text-gray-600">Questions</p>
            </div>
          </div>
          
          <div className="flex space-x-3">
            <Button variant="outline" size="sm" onClick={onEditProfile}>
              Edit Profile
            </Button>
            <Button 
              size="sm" 
              onClick={onManageSubscription}
              className={profile.subscriptionStatus === 'free' ? 'bg-green-600 hover:bg-green-700' : ''}
            >
              {profile.subscriptionStatus === 'free' ? 'Upgrade Plan' : 'Manage Subscription'}
            </Button>
          </div>
        </div>
      </div>
      
      {/* Subscription info (if subscribed) */}
      {profile.subscriptionStatus !== 'free' && profile.subscriptionEndDate && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <p className="text-sm text-gray-600">
            Your {profile.subscriptionStatus} subscription is active until {formatDate(profile.subscriptionEndDate)}.
          </p>
        </div>
      )}
    </div>
  );
};

export default UserProfileHeader;
