'use client';

import { useSession, signOut as nextAuthSignOut } from "next-auth/react";
import type { CustomSession } from "./auth";

interface User {
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

interface UseAuthReturn {
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;
  logout: () => Promise<void>;
  accessToken: string | null;
}

export function useAuth(): UseAuthReturn {
  const { data: session, status } = useSession();
  const customSession = session as CustomSession | null;

  const logout = async () => {
    await nextAuthSignOut({ redirect: false });
  };

  return {
    user: (customSession?.backendUser as User) ?? null,
    loading: status === "loading",
    isAuthenticated: status === "authenticated" && !!customSession?.user,
    logout,
    accessToken: customSession?.accessToken ?? null,
  };
}
