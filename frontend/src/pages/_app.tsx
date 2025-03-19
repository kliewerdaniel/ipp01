import '@styles/globals.css';
import type { AppProps } from 'next/app';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from '@context/AuthContext';
import { Toaster } from 'react-hot-toast';
import { Elements } from '@stripe/react-stripe-js';
import { loadStripe } from '@stripe/stripe-js';

// Create a client
const queryClient = new QueryClient();

// Load Stripe outside of a component render cycle
const stripePromise = process.env.NEXT_PUBLIC_STRIPE_PUBLIC_KEY 
  ? loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLIC_KEY)
  : null;

export default function App({ Component, pageProps }: AppProps) {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        {stripePromise ? (
          <Elements stripe={stripePromise}>
            <Component {...pageProps} />
            <Toaster position="top-right" />
          </Elements>
        ) : (
          <>
            <Component {...pageProps} />
            <Toaster position="top-right" />
          </>
        )}
      </AuthProvider>
    </QueryClientProvider>
  );
}
