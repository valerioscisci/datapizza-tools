export interface Course {
  id: string;
  title: string;
  description: string;
  provider: string;
  url: string;
  instructor: string | null;
  level: string;
  duration: string | null;
  price: string | null;
  rating: string | null;
  students_count: number | null;
  category: string;
  tags: string[];
  image_url: string | null;
  created_at: string;
}

export interface CourseListResponse {
  items: Course[];
  total: number;
  page: number;
  page_size: number;
}
