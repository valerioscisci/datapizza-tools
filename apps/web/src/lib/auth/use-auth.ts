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
  user_type: string;
  company_name: string | null;
  company_website: string | null;
  company_size: string | null;
  industry: string | null;
  created_at: string;
}

interface UseAuthReturn {
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;
  isCompany: boolean;
  logout: () => Promise<void>;
  accessToken: string | null;
}

export function useAuth(): UseAuthReturn {
  const { data: session, status } = useSession();
  const customSession = session as CustomSession | null;

  const logout = async () => {
    await nextAuthSignOut({ redirect: false });
  };

  const user = (customSession?.backendUser as User) ?? null;

  return {
    user,
    loading: status === "loading",
    isAuthenticated: status === "authenticated" && !!customSession?.user,
    isCompany: user?.user_type === "company",
    logout,
    accessToken: customSession?.accessToken ?? null,
  };
}
