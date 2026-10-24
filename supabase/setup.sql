-- Run this once in Supabase Dashboard > SQL Editor.
-- Account records are private to the signed-in owner through row-level security.

create table if not exists public.profiles (
  user_id uuid primary key references auth.users (id) on delete cascade,
  full_name text not null default '' check (char_length(full_name) <= 100),
  organization text not null default '' check (char_length(organization) <= 100),
  bidder_type text not null default '' check (char_length(bidder_type) <= 60),
  years_active text not null default '' check (char_length(years_active) <= 40),
  region text not null default '' check (char_length(region) <= 60),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.saved_tenders (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  title text not null check (char_length(title) between 1 and 240),
  source_url text not null check (char_length(source_url) <= 2048 and source_url ~ '^https?://'),
  source_portal text not null default 'Tender portal' check (char_length(source_portal) <= 120),
  snippet text not null default '' check (char_length(snippet) <= 1200),
  created_at timestamptz not null default now(),
  unique (user_id, source_url)
);

create index if not exists saved_tenders_user_created_idx
  on public.saved_tenders (user_id, created_at desc);

alter table public.profiles enable row level security;
alter table public.saved_tenders enable row level security;

revoke all on table public.profiles from anon, public;
revoke all on table public.saved_tenders from anon, public;
grant select, insert, update, delete on table public.profiles to authenticated;
grant select, insert, update, delete on table public.saved_tenders to authenticated;

drop policy if exists "Owners can read their profile" on public.profiles;
create policy "Owners can read their profile"
  on public.profiles for select to authenticated
  using ((select auth.uid()) = user_id);

drop policy if exists "Owners can create their profile" on public.profiles;
create policy "Owners can create their profile"
  on public.profiles for insert to authenticated
  with check ((select auth.uid()) = user_id);

drop policy if exists "Owners can update their profile" on public.profiles;
create policy "Owners can update their profile"
  on public.profiles for update to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

drop policy if exists "Owners can delete their profile" on public.profiles;
create policy "Owners can delete their profile"
  on public.profiles for delete to authenticated
  using ((select auth.uid()) = user_id);

drop policy if exists "Owners can read their saved tenders" on public.saved_tenders;
create policy "Owners can read their saved tenders"
  on public.saved_tenders for select to authenticated
  using ((select auth.uid()) = user_id);

drop policy if exists "Owners can save their tenders" on public.saved_tenders;
create policy "Owners can save their tenders"
  on public.saved_tenders for insert to authenticated
  with check ((select auth.uid()) = user_id);

drop policy if exists "Owners can update their saved tenders" on public.saved_tenders;
create policy "Owners can update their saved tenders"
  on public.saved_tenders for update to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

drop policy if exists "Owners can remove their saved tenders" on public.saved_tenders;
create policy "Owners can remove their saved tenders"
  on public.saved_tenders for delete to authenticated
  using ((select auth.uid()) = user_id);
