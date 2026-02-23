import NextAuth from "next-auth";
import type { NextAuthConfig, Session } from "next-auth";
import type { JWT } from "next-auth/jwt";
import Credentials from "next-auth/providers/credentials";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8003";

interface BackendUser {
  id: string;
  email: string;
  full_name: string;
  phone: string | null;
  bio: string | null;
  location: string | null;
  experience_level: string | null;
  experience_years: string | null;
  current_role: string | null;
  skills: string[];
  availability_status: string;
  reskilling_status: string | null;
  adopted_by_company: string | null;
  created_at: string;
}

interface AuthUser {
  id: string;
  accessToken: string;
  backendUser: BackendUser;
}

interface CustomJWT extends JWT {
  accessToken?: string;
  backendUser?: BackendUser;
}

export interface CustomSession extends Session {
  accessToken?: string;
  backendUser?: BackendUser;
}

const config: NextAuthConfig = {
  providers: [
    Credentials({
      id: "credentials",
      name: "Credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          return null;
        }

        try {
          // Login to get the access token
          const loginRes = await fetch(`${API_URL}/api/v1/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              email: credentials.email,
              password: credentials.password,
            }),
          });

          if (!loginRes.ok) {
            return null;
          }

          const loginData = await loginRes.json();
          const accessToken = loginData.access_token;

          // Fetch user profile with the token
          const meRes = await fetch(`${API_URL}/api/v1/auth/me`, {
            headers: { Authorization: `Bearer ${accessToken}` },
          });

          if (!meRes.ok) {
            return null;
          }

          const backendUser: BackendUser = await meRes.json();

          return {
            id: backendUser.id,
            accessToken,
            backendUser,
          };
        } catch {
          return null;
        }
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user }): Promise<CustomJWT> {
      // Initial sign in
      if (user) {
        const authUser = user as unknown as AuthUser;
        return {
          ...token,
          accessToken: authUser.accessToken,
          backendUser: authUser.backendUser,
        };
      }

      return token as CustomJWT;
    },
    async session({ session, token }): Promise<CustomSession> {
      const customToken = token as CustomJWT;
      const customSession = session as CustomSession;

      if (customToken.backendUser) {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        customSession.user = customToken.backendUser as any;
        customSession.backendUser = customToken.backendUser;
      }
      customSession.accessToken = customToken.accessToken;

      return customSession;
    },
  },
  pages: {
    signIn: "/it/login",
  },
  session: {
    strategy: "jwt",
    maxAge: 24 * 60 * 60, // 24 hours — matches backend JWT expiry
  },
  trustHost: true,
};

export const { handlers, signIn, signOut, auth } = NextAuth(config);
