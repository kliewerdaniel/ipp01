import { DefaultSession, DefaultUser } from "next-auth";
import { JWT } from "next-auth/jwt";

declare module "next-auth" {
  interface Session extends DefaultSession {
    accessToken: string;
    refreshToken: string;
    csrfToken: string;
    provider: string;
    error?: string;
    user: {
      id: string;
      name: string;
      email: string;
      role: string;
      permissions: string[];
    } & DefaultSession["user"];
  }

  interface User extends DefaultUser {
    id: string;
    email: string;
    name: string;
    role: string;
    permissions?: string[];
    accessToken?: string;
    refreshToken?: string;
    csrfToken?: string;
    provider?: string;
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    id?: string;
    name?: string;
    email?: string;
    role?: string;
    permissions?: string[];
    accessToken?: string;
    refreshToken?: string;
    csrfToken?: string;
    provider?: string;
    error?: string;
  }
}
