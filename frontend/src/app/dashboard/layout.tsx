'use client';

import React from 'react';
import Header from '@/components/layout/Header';
import DashboardSidebar from '@/components/layout/DashboardSidebar';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="flex">
        <DashboardSidebar />
        <main className="flex-1 pt-16 md:ml-64 p-6">{children}</main>
      </div>
    </div>
  );
}
