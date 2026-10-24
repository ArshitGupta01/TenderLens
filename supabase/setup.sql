-- ============================================================================
-- TenderLens - Supabase PostgreSQL Schema & Migrations 
-- ============================================================================
-- Run this script once in Supabase Dashboard > SQL Editor > New Query > Run.
--
-- Features:
-- 1. `profiles`: Basic user details + full financial & statutory BidderProfile
-- 2. `saved_tenders`: Live tender notices bookmarked by signed-in users
-- 3. `tender_audits`: Historical AI qualification scorecards & strategy reports
-- 4. Complete Row Level Security (RLS) ensuring strict user data isolation
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. Bidder Profiles Table
-- ----------------------------------------------------------------------------
create table if not exists public.profiles (
  user_id uuid primary key references auth.users (id) on delete cascade,
  full_name text not null default '' check (char_length(full_name) <= 100),
  organization text not null default '' check (char_length(organization) <= 100),
  bidder_type text not null default '' check (char_length(bidder_type) <= 60),
  years_active text not null default '' check (char_length(years_active) <= 40),
  region text not null default '' check (char_length(region) <= 60),
  
  -- Statutory & Financial Bidder Capacity (TenderLens Engine Extensions)
  is_msme_registered boolean not null default false,
  msme_category text not null default '',
  is_startup_recognized boolean not null default false,
  turnover_year_1_lakhs numeric not null default 0.0,
  turnover_year_2_lakhs numeric not null default 0.0,
  turnover_year_3_lakhs numeric not null default 0.0,
  years_in_business integer not null default 0,
  local_content_percentage numeric not null default 50.0,
  held_certifications text[] not null default '{}'::text[],
  past_similar_project_values_lakhs numeric[] not null default '{}'::numeric[],

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Idempotent column additions in case table was created with earlier partial schema
alter table public.profiles add column if not exists is_msme_registered boolean not null default false;
alter table public.profiles add column if not exists msme_category text not null default '';
alter table public.profiles add column if not exists is_startup_recognized boolean not null default false;
alter table public.profiles add column if not exists turnover_year_1_lakhs numeric not null default 0.0;
alter table public.profiles add column if not exists turnover_year_2_lakhs numeric not null default 0.0;
alter table public.profiles add column if not exists turnover_year_3_lakhs numeric not null default 0.0;
alter table public.profiles add column if not exists years_in_business integer not null default 0;
alter table public.profiles add column if not exists local_content_percentage numeric not null default 50.0;
alter table public.profiles add column if not exists held_certifications text[] not null default '{}'::text[];
alter table public.profiles add column if not exists past_similar_project_values_lakhs numeric[] not null default '{}'::numeric[];

-- ----------------------------------------------------------------------------
-- 2. Saved Tenders Bookmarks Table
-- ----------------------------------------------------------------------------
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

-- ----------------------------------------------------------------------------
-- 3. Tender Qualification Audits & Strategy Reports Table
-- ----------------------------------------------------------------------------
create table if not exists public.tender_audits (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  tender_id text not null default '',
  tender_title text not null check (char_length(tender_title) <= 240),
  tender_url text not null default '',
  source_portal text not null default 'GeM' check (char_length(source_portal) <= 120),
  recommendation text not null default 'CONDITIONAL_BID' check (recommendation in ('STRONG_BID', 'CONDITIONAL_BID', 'RED_FLAG_NO_BID')),
  qualification_score numeric not null default 0.0,
  scorecard_data jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists tender_audits_user_created_idx
  on public.tender_audits (user_id, created_at desc);

-- ----------------------------------------------------------------------------
-- 4. Row Level Security (RLS) Enablement & Permissions
-- ----------------------------------------------------------------------------
alter table public.profiles enable row level security;
alter table public.saved_tenders enable row level security;
alter table public.tender_audits enable row level security;

-- Revoke dangerous public and anon direct permissions
revoke all on table public.profiles from anon, public;
revoke all on table public.saved_tenders from anon, public;
revoke all on table public.tender_audits from anon, public;

-- Grant standard permissions to authenticated users
grant select, insert, update, delete on table public.profiles to authenticated;
grant select, insert, update, delete on table public.saved_tenders to authenticated;
grant select, insert, update, delete on table public.tender_audits to authenticated;

-- Grant administrative access to service_role (backend orchestrator)
grant all on table public.profiles to service_role;
grant all on table public.saved_tenders to service_role;
grant all on table public.tender_audits to service_role;

-- ----------------------------------------------------------------------------
-- 5. RLS Policies: Profiles
-- ----------------------------------------------------------------------------
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

-- ----------------------------------------------------------------------------
-- 6. RLS Policies: Saved Tenders
-- ----------------------------------------------------------------------------
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

-- ----------------------------------------------------------------------------
-- 7. RLS Policies: Tender Audits
-- ----------------------------------------------------------------------------
drop policy if exists "Owners can read their tender audits" on public.tender_audits;
create policy "Owners can read their tender audits"
  on public.tender_audits for select to authenticated
  using ((select auth.uid()) = user_id);

drop policy if exists "Owners can insert their tender audits" on public.tender_audits;
create policy "Owners can insert their tender audits"
  on public.tender_audits for insert to authenticated
  with check ((select auth.uid()) = user_id);

drop policy if exists "Owners can update their tender audits" on public.tender_audits;
create policy "Owners can update their tender audits"
  on public.tender_audits for update to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

drop policy if exists "Owners can delete their tender audits" on public.tender_audits;
create policy "Owners can delete their tender audits"
  on public.tender_audits for delete to authenticated
  using ((select auth.uid()) = user_id);

-- ----------------------------------------------------------------------------
-- Verification helper comment
-- ----------------------------------------------------------------------------
comment on table public.profiles is 'Stores user bidder profiles and financial capacity for TenderLens audits.';
comment on table public.saved_tenders is 'Stores live public tender notices bookmarked by users.';
comment on table public.tender_audits is 'Stores full AI qualification scorecards and strategic pillar outputs.';
