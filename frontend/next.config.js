/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  images: {
    domains: ['localhost'],
    // Add any CDN or external image domains here
  },
  env: {
    // Default environment variables
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    NEXT_PUBLIC_STRIPE_PUBLIC_KEY: process.env.NEXT_PUBLIC_STRIPE_PUBLIC_KEY,
  },
  // Enable experimental features if needed
  experimental: {
    // serverActions: true,
    // appDir: true,
  },
  // Customize webpack config if needed
  webpack(config) {
    return config;
  },
};

module.exports = nextConfig;
