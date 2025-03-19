import { Metadata } from 'next';
import Header from '@/components/layout/Header';
import DashboardSidebar from '@/components/layout/DashboardSidebar';

export const metadata: Metadata = {
  title: 'Dashboard - Interview Prep Platform',
  description: 'Your interview preparation dashboard',
};

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <div className="flex">
        {/* Sidebar - fixed on desktop, drawer on mobile */}
        <DashboardSidebar />
        
        {/* Main content */}
        <main className="flex-1 p-6 md:ml-64">
          {children}
        </main>
      </div>
    </div>
  );
}
