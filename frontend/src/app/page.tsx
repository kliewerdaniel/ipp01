import Link from 'next/link';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Home - Interview Prep Platform',
  description: 'Prepare for technical interviews with our comprehensive platform',
};

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      <div className="container mx-auto px-4 py-16">
        <header className="flex justify-between items-center mb-16">
          <h1 className="text-3xl font-bold text-blue-900">Interview Prep Platform</h1>
          <div className="flex gap-4">
            <Link 
              href="/auth/login" 
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              Log In
            </Link>
            <Link 
              href="/auth/register" 
              className="px-4 py-2 border border-blue-600 text-blue-600 rounded-md hover:bg-blue-50 transition-colors"
            >
              Sign Up
            </Link>
          </div>
        </header>
        
        <main>
          <section className="mb-16 text-center">
            <h2 className="text-4xl font-bold text-gray-900 mb-6">Ace Your Next Technical Interview</h2>
            <p className="text-xl text-gray-700 max-w-3xl mx-auto mb-8">
              Our platform provides comprehensive resources, practice questions, and mock interviews
              to help you prepare for technical interviews at top tech companies.
            </p>
            <Link 
              href="/auth/register" 
              className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-lg font-semibold"
            >
              Get Started Now
            </Link>
          </section>
          
          <section className="grid md:grid-cols-3 gap-8">
            <div className="p-6 bg-white rounded-lg shadow-md">
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Practice Questions</h3>
              <p className="text-gray-700">
                Access a curated library of technical questions from real interviews at top companies.
              </p>
            </div>
            <div className="p-6 bg-white rounded-lg shadow-md">
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Mock Interviews</h3>
              <p className="text-gray-700">
                Simulate real interview environments with our timed interview sessions and get feedback.
              </p>
            </div>
            <div className="p-6 bg-white rounded-lg shadow-md">
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Performance Analytics</h3>
              <p className="text-gray-700">
                Track your progress over time and identify areas for improvement with detailed analytics.
              </p>
            </div>
          </section>
        </main>
        
        <footer className="mt-16 py-8 border-t border-gray-200 text-center text-gray-600">
          <p>© {new Date().getFullYear()} Interview Prep Platform. All rights reserved.</p>
        </footer>
      </div>
    </div>
  );
}
