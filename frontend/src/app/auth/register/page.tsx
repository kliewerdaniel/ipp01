import { Metadata } from 'next';
import Link from 'next/link';
import RegisterForm from './RegisterForm';

export const metadata: Metadata = {
  title: 'Register - Interview Prep Platform',
  description: 'Create a new account on the Interview Prep Platform',
};

export default function RegisterPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900">Create an account</h1>
          <p className="mt-2 text-sm text-gray-600">
            Join today and start preparing for your technical interviews
          </p>
        </div>

        <RegisterForm />

        <div className="text-center mt-6">
          <p className="text-sm text-gray-600">
            Already have an account?{' '}
            <Link
              href="/auth/login"
              className="font-medium text-blue-600 hover:text-blue-500"
            >
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
