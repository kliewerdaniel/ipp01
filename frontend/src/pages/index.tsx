import React from 'react';
import Head from 'next/head';
import Link from 'next/link';
import Image from 'next/image';

export default function Home() {
  return (
    <div className="min-h-screen">
      <Head>
        <title>Interview Prep Platform</title>
        <meta name="description" content="Prepare for your interviews with AI-powered feedback" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main>
        {/* Hero Section */}
        <section className="bg-gradient-to-r from-primary-600 to-secondary-600 text-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
              <div>
                <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight mb-4">
                  Ace Your Next Interview
                </h1>
                <p className="text-xl mb-8">
                  Practice interviews, get AI-powered feedback, and track your progress to improve your interview skills.
                </p>
                <div className="flex flex-col sm:flex-row gap-4">
                  <Link href="/register" className="btn bg-white text-primary-600 hover:bg-gray-100">
                    Get Started
                  </Link>
                  <Link href="/about" className="btn bg-transparent border border-white hover:bg-white/10">
                    Learn More
                  </Link>
                </div>
              </div>
              <div className="relative h-64 md:h-80">
                {/* Placeholder for hero image */}
                <div className="w-full h-full bg-white/20 rounded-lg flex items-center justify-center">
                  <span className="text-lg font-medium">Interview Practice Platform</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-16 bg-gray-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-3xl font-bold mb-4">Key Features</h2>
              <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                Everything you need to prepare for your next interview
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {/* Feature 1 */}
              <div className="card">
                <div className="h-12 w-12 bg-primary-100 text-primary-600 rounded-md flex items-center justify-center mb-4">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold mb-2">AI-Generated Questions</h3>
                <p className="text-gray-600">
                  Practice with industry-specific questions tailored to your experience level.
                </p>
              </div>

              {/* Feature 2 */}
              <div className="card">
                <div className="h-12 w-12 bg-primary-100 text-primary-600 rounded-md flex items-center justify-center mb-4">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold mb-2">Voice Recording</h3>
                <p className="text-gray-600">
                  Record your answers and get them automatically transcribed for review.
                </p>
              </div>

              {/* Feature 3 */}
              <div className="card">
                <div className="h-12 w-12 bg-primary-100 text-primary-600 rounded-md flex items-center justify-center mb-4">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold mb-2">Smart Feedback</h3>
                <p className="text-gray-600">
                  Get personalized feedback on your answers to improve your interview performance.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Call to Action */}
        <section className="py-16 bg-primary-600 text-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="text-3xl font-bold mb-4">Ready to ace your next interview?</h2>
            <p className="text-xl mb-8 max-w-3xl mx-auto">
              Join thousands of users who have improved their interview skills with our platform.
            </p>
            <Link href="/register" className="btn bg-white text-primary-600 hover:bg-gray-100">
              Get Started Today
            </Link>
          </div>
        </section>
      </main>

      <footer className="bg-gray-800 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <h3 className="text-lg font-semibold mb-4">Interview Prep Platform</h3>
              <p className="text-gray-400">
                Your ultimate companion for interview preparation.
              </p>
            </div>
            <div>
              <h4 className="text-lg font-semibold mb-4">Features</h4>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="/features">AI Feedback</Link></li>
                <li><Link href="/features">Voice Recording</Link></li>
                <li><Link href="/features">Progress Tracking</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="text-lg font-semibold mb-4">Resources</h4>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="/blog">Blog</Link></li>
                <li><Link href="/guides">Interview Guides</Link></li>
                <li><Link href="/faq">FAQ</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="text-lg font-semibold mb-4">Legal</h4>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="/privacy">Privacy Policy</Link></li>
                <li><Link href="/terms">Terms of Service</Link></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-700 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; {new Date().getFullYear()} Interview Prep Platform. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
