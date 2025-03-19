import { Inter } from 'next/font/google';
import { Metadata } from 'next';
import AuthProvider from '@/context/AuthProvider';
import { AppStateProvider } from '@/context/AppStateContext';
import '@/styles/globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Interview Prep Platform',
  description: 'A platform to help you prepare for technical interviews',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AuthProvider>
          <AppStateProvider>
            {children}
          </AppStateProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
