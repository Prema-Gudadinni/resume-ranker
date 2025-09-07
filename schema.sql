-- 1) user profiles (link to supabase auth)
create table if not exists public.profiles (
  id uuid primary key default gen_random_uuid(),
  full_name text,
  email text unique,
  created_at timestamptz default now()
);

-- 2) resumes table (metadata + storage path)
create table if not exists public.resumes (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references public.profiles(id),
  filename text not null,
  storage_path text not null, -- e.g. "resumes/<uuid>.pdf" in Supabase Storage
  uploaded_at timestamptz default now(),
  text_content text, -- extracted text
  is_ocr boolean default false
);

-- 3) embeddings stored as vector (we'll use float8[] for simplicity)
create table if not exists public.resume_embeddings (
  id uuid primary key default gen_random_uuid(),
  resume_id uuid references public.resumes(id) on delete cascade,
  embedding float8[] not null,
  created_at timestamptz default now()
);

-- 4) ranking results for a given job/request
create table if not exists public.rankings (
  id uuid primary key default gen_random_uuid(),
  job_title text,
  job_description text,
  created_by uuid references public.profiles(id),
  created_at timestamptz default now()
);

create table if not exists public.ranking_items (
  id uuid primary key default gen_random_uuid(),
  ranking_id uuid references public.rankings(id) on delete cascade,
  resume_id uuid references public.resumes(id),
  score numeric, -- percentage or similarity score
  note text
);
