import NextAuth, { NextAuthOptions } from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";
import GoogleProvider from "next-auth/providers/google";
import FacebookProvider from "next-auth/providers/facebook";
import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const authOptions: NextAuthOptions = {
  providers: [
    // Credentials provider for email/password login
    CredentialsProvider({
      name: "credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
        remember_me: { label: "Remember me", type: "checkbox" }
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          return null;
        }

        try {
          const response = await axios.post(`${API_URL}/api/auth/login/json`, {
            email: credentials.email,
            password: credentials.password,
            remember_me: credentials.remember_me === "true"
          });
          
          const { user, access_token, refresh_token, csrf_token } = response.data;
          
          if (user && access_token) {
            return {
              ...user,
              accessToken: access_token,
              refreshToken: refresh_token,
              csrfToken: csrf_token,
              provider: "credentials"
            };
          }
          
          return null;
        } catch (error) {
          console.error("NextAuth credentials error:", error);
          return null;
        }
      }
    }),
    
    // Google OAuth provider
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID || "",
      clientSecret: process.env.GOOGLE_CLIENT_SECRET || "",
      authorization: {
        params: {
          prompt: "consent",
          access_type: "offline",
          response_type: "code"
        }
      }
    }),
    
    // Facebook OAuth provider
    FacebookProvider({
      clientId: process.env.FACEBOOK_CLIENT_ID || "",
      clientSecret: process.env.FACEBOOK_CLIENT_SECRET || "",
    })
  ],
  callbacks: {
    async signIn({ account, profile }) {
      // For OAuth sign-ins, we need to create/update the user in our API
      if (account?.provider === "google" || account?.provider === "facebook") {
        try {
          // Redirect to our backend OAuth handler instead of using NextAuth's built-in handling
          // This is a workaround - we redirect to our custom OAuth flow
          window.location.href = `${API_URL}/api/auth/oauth/${account.provider}`;
          // We don't actually want NextAuth to complete its flow at this point
          // But we return true to avoid errors
          return true;
        } catch (error) {
          console.error(`Error during ${account.provider} sign in:`, error);
          return false;
        }
      }
      
      return true;
    },
    
    async jwt({ token, user, account }) {
      // Initial sign in
      if (user && account) {
        // For credentials login, we have the tokens
        if (account.provider === "credentials") {
          token.accessToken = user.accessToken;
          token.refreshToken = user.refreshToken;
          token.csrfToken = user.csrfToken;
          token.id = user.id;
          token.email = user.email;
          token.name = user.name;
          token.role = user.role;
          token.permissions = user.permissions || [];
          token.provider = "credentials";
        }
      }
      
      // Check if access token expired and try to refresh
      const tokenExpiry = new Date(Date.now() + 1000 * 60 * 30); // 30 minutes from now
      if (Date.now() > tokenExpiry.getTime() && token.refreshToken) {
        try {
          const response = await axios.post(`${API_URL}/api/auth/refresh`, {
            refresh_token: token.refreshToken
          });
          
          if (response.data.access_token) {
            token.accessToken = response.data.access_token;
            token.refreshToken = response.data.refresh_token;
            token.csrfToken = response.data.csrf_token;
          }
        } catch (error) {
          console.error("Error refreshing token:", error);
          // Token refresh failed - user will have to log in again
          return { ...token, error: "RefreshAccessTokenError" };
        }
      }
      
      return token;
    },
    
    async session({ session, token }) {
      if (token) {
        session.user = {
          id: token.id as string,
          name: token.name as string,
          email: token.email as string,
          role: token.role as string,
          permissions: (token.permissions as string[]) || [],
        };
        session.accessToken = token.accessToken as string;
        session.refreshToken = token.refreshToken as string;
        session.csrfToken = token.csrfToken as string;
        session.provider = token.provider as string;
        
        // Add error if present
        if (token.error) {
          session.error = token.error;
        }
      }
      return session;
    }
  },
  events: {
    async signOut({ token }) {
      // Call backend logout to invalidate the token
      if (token?.accessToken) {
        try {
          await axios.post(
            `${API_URL}/api/auth/logout`, 
            {}, 
            {
              headers: { 
                Authorization: `Bearer ${token.accessToken}`,
                "X-CSRF-Token": token.csrfToken || "",
              }
            }
          );
        } catch (error) {
          console.error("Error during logout:", error);
        }
      }
    }
  },
  pages: {
    signIn: '/auth/login',
    signOut: '/',
    error: '/auth/error',
  },
  session: {
    strategy: 'jwt',
    maxAge: 30 * 24 * 60 * 60, // 30 days
  },
  cookies: {
    sessionToken: {
      name: `next-auth.session-token`,
      options: {
        httpOnly: true,
        sameSite: 'lax',
        path: '/',
        secure: process.env.NODE_ENV === 'production',
      }
    }
  },
  secret: process.env.NEXTAUTH_SECRET || 'your-secret-key',
  debug: process.env.NODE_ENV === 'development',
};

const handler = NextAuth(authOptions);

export { handler as GET, handler as POST };
