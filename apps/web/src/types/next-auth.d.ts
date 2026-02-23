import "next-auth";

declare module "next-auth" {
  interface Session {
    accessToken?: string;
    backendUser?: {
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
    };
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    accessToken?: string;
    backendUser?: {
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
    };
  }
}
