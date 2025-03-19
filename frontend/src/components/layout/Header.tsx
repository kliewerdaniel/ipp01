'use client';

import Link from 'next/link';
import { useSession, signOut } from 'next-auth/react';

const Header = () => {
  const { data: session, status } = useSession();
  const isAuthenticated = status === 'authenticated';

  return (
    <header className="bg-white shadow-sm">
      <div className="container mx-auto px-4 py-4">
        <div className="flex justify-between items-center">
          <Link href="/" className="text-2xl font-bold text-blue-900">
            Interview Prep
          </Link>

          <nav className="hidden md:flex items-center space-x-8">
            <Link href="/" className="text-gray-700 hover:text-blue-600 transition-colors">
              Home
            </Link>
            {isAuthenticated && (
              <>
                <Link href="/dashboard" className="text-gray-700 hover:text-blue-600 transition-colors">
                  Dashboard
                </Link>
                <Link href="/dashboard/practice" className="text-gray-700 hover:text-blue-600 transition-colors">
                  Practice
                </Link>
                <Link href="/dashboard/interviews" className="text-gray-700 hover:text-blue-600 transition-colors">
                  Interviews
                </Link>
              </>
            )}
          </nav>

          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <div className="flex items-center space-x-4">
                <span className="text-gray-700">
                  {session?.user?.name}
                </span>
                <button
                  onClick={() => signOut({ callbackUrl: '/' })}
                  className="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
                >
                  Log Out
                </button>
              </div>
            ) : (
              <div className="flex space-x-4">
                <Link
                  href="/auth/login"
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                >
                  Log In
                </Link>
                <Link
                  href="/auth/register" 
                  className="hidden md:inline-block px-4 py-2 border border-blue-600 text-blue-600 rounded-md hover:bg-blue-50 transition-colors"
                >
                  Sign Up
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
