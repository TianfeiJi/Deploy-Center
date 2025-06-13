// src/types/Template.ts

export interface Template {
  id: string;
  template_name: string;
  relative_path: string;
  template_type: string;
  project_type: string;
  description?: string;
  created_at?: string;
  updated_at?: string;
}
