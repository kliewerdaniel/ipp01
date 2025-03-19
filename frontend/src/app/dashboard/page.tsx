"use client";

import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/Card';
import Timer from '@/components/ui/Timer';
import Link from 'next/link';

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
      </div>

      {/* Quick stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">
              Completed Interviews
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">0</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">
              Problems Solved
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">0</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">
              Overall Progress
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">0%</div>
          </CardContent>
        </Card>
      </div>
      
      {/* Main actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Start interview section */}
        <Card>
          <CardHeader>
            <CardTitle>Start a Mock Interview</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-gray-600">
              Practice with a timed interview session. Choose from different difficulty levels and topics.
            </p>
            
            <div className="flex justify-center py-4">
              <Timer 
                initialTimeInSeconds={1800} 
                size="lg" 
                autoStart={false} 
                showControls={true}
              />
            </div>
          </CardContent>
          <CardFooter>
            <Link
              href="/dashboard/interviews/new"
              className="w-full bg-blue-600 text-white py-2 px-4 rounded text-center hover:bg-blue-700 transition-colors"
            >
              Start Interview
            </Link>
          </CardFooter>
        </Card>
        
        {/* Practice questions section */}
        <Card>
          <CardHeader>
            <CardTitle>Practice Questions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-gray-600">
              Solve individual questions to build your skills. Filter by topic, difficulty, or company.
            </p>
            
            <div className="space-y-2">
              <div className="flex justify-between items-center p-3 bg-gray-50 rounded-md">
                <span className="font-medium">Algorithms</span>
                <span className="text-sm text-gray-500">150 questions</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-gray-50 rounded-md">
                <span className="font-medium">Data Structures</span>
                <span className="text-sm text-gray-500">120 questions</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-gray-50 rounded-md">
                <span className="font-medium">System Design</span>
                <span className="text-sm text-gray-500">35 questions</span>
              </div>
            </div>
          </CardContent>
          <CardFooter>
            <Link
              href="/dashboard/practice"
              className="w-full bg-blue-600 text-white py-2 px-4 rounded text-center hover:bg-blue-700 transition-colors"
            >
              Browse Questions
            </Link>
          </CardFooter>
        </Card>
      </div>
      
      {/* Recent activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-gray-500">
            <p>No recent activity yet. Start practicing to see your progress here!</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
