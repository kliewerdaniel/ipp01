'use client';

import React from 'react';
import AdminPanel from '@/components/admin/AdminPanel';
import { useRouter, useSearchParams } from 'next/navigation';

const AdminPage: React.FC = () => {
  const router = useRouter();
  const searchParams = useSearchParams();
  
  // Get the active tab from URL parameters, if available
  const tabParam = searchParams?.get('tab');
  const initialActiveTab = (tabParam === 'questions' || 
                           tabParam === 'criteria' || 
                           tabParam === 'statistics' || 
                           tabParam === 'clones') ? 
                          tabParam : 'questions';

  return (
    <div className="container mx-auto px-4 py-8">
      <AdminPanel initialActiveTab={initialActiveTab as any} />
    </div>
  );
};

export default AdminPage;
