# TenderLens Database Architecture & Schema Specification
=========================================================

## 1. Purpose
This document describes the relational database architecture, data models, Row-Level Security (RLS) policies, and persistence conventions used in TenderLens.

## 2. Database Stack
- **Database Engine**: PostgreSQL 15+ hosted on Supabase Cloud.
- **Access Protocol**: PostgREST REST API, Supabase Auth, and `supabase-py` client.
- **Security Paradigm**: PostgreSQL Row-Level Security (RLS) tied strictly to `auth.uid()`.
- **Primary Schema Setup**: [`supabase/setup.sql`](../supabase/setup.sql).

## 3. Environment & Connection Rules
- The database connection URL and service keys are managed via environment variables (`SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`).
- Browser clients only ever receive the public publishable/anon key via `/api/v1/auth/config`.
- Direct PostgreSQL passwords and service-role keys must NEVER be committed to version control or sent to client code.

## 4. Core Tables & Schemas

### 4.1 Table: `public.profiles`
Stores the authenticated bidder's organization details, MSME status, financial metrics, and certifications.

| Column | Type | Constraints / Defaults | Description |
| :--- | :--- | :--- | :--- |
| `user_id` | `UUID` | `PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE` | Owner user ID from Supabase Auth |
| `full_name` | `TEXT` | `DEFAULT ''` | Contact person's full name |
| `organization` | `TEXT` | `NOT NULL DEFAULT ''` | Legal business/entity name |
| `bidder_type` | `TEXT` | `DEFAULT 'System Integrator'` | OEM, System Integrator, EPC, etc. |
| `years_active` | `TEXT` | `DEFAULT ''` | Descriptive experience band |
| `region` | `TEXT` | `DEFAULT ''` | Primary operating territory |
| `is_msme_registered` | `BOOLEAN` | `DEFAULT FALSE` | Udyam MSME status |
| `msme_category` | `TEXT` | `DEFAULT ''` | MICRO, SMALL, MEDIUM |
| `is_startup_recognized`| `BOOLEAN` | `DEFAULT FALSE` | DPIIT Startup status |
| `turnover_year_1_lakhs`| `NUMERIC(12, 2)`| `DEFAULT 0.0` | FY-1 Turnover (₹ Lakhs) |
| `turnover_year_2_lakhs`| `NUMERIC(12, 2)`| `DEFAULT 0.0` | FY-2 Turnover (₹ Lakhs) |
| `turnover_year_3_lakhs`| `NUMERIC(12, 2)`| `DEFAULT 0.0` | FY-3 Turnover (₹ Lakhs) |
| `years_in_business` | `INTEGER` | `DEFAULT 0` | Numerical years of experience |
| `local_content_percentage`| `NUMERIC(5, 2)`| `DEFAULT 50.0` | Make in India local content % |
| `held_certifications` | `JSONB` | `DEFAULT '[]'::jsonb` | Array of ISO, BIS, CE certs |
| `past_similar_project_values_lakhs` | `JSONB` | `DEFAULT '[]'::jsonb` | Past project values for CPWD checks |
| `created_at` | `TIMESTAMPTZ` | `DEFAULT NOW()` | Record creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | `DEFAULT NOW()` | Record update timestamp |

### 4.2 Table: `public.saved_tenders`
Stores tender bookmarks explicitly saved by signed-in bidders.

| Column | Type | Constraints / Defaults | Description |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | `PRIMARY KEY DEFAULT gen_random_uuid()` | Unique bookmark ID |
| `user_id` | `UUID` | `NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE` | Owner user ID |
| `title` | `TEXT` | `NOT NULL` | Tender notice title |
| `source_url` | `TEXT` | `NOT NULL` | Official portal URL |
| `source_portal` | `TEXT` | `DEFAULT 'Tender portal'` | GeM, CPPP, BHEL, etc. |
| `snippet` | `TEXT` | `DEFAULT ''` | Brief clause excerpt or summary |
| `created_at` | `TIMESTAMPTZ` | `DEFAULT NOW()` | Timestamp bookmark was saved |

*Constraint*: `UNIQUE (user_id, source_url)` prevents duplicate bookmarks per user.

### 4.3 Table: `public.tender_audits`
Stores completed qualification audit scorecards and 5-pillar strategy reports.

| Column | Type | Constraints / Defaults | Description |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | `PRIMARY KEY DEFAULT gen_random_uuid()` | Unique audit report ID |
| `user_id` | `UUID` | `NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE` | Evaluator user ID |
| `tender_id` | `TEXT` | `NOT NULL DEFAULT ''` | Bid/Notice reference number |
| `tender_title` | `TEXT` | `NOT NULL DEFAULT ''` | Full tender title |
| `tender_url` | `TEXT` | `DEFAULT ''` | Source document or portal link |
| `source_portal` | `TEXT` | `DEFAULT 'GeM'` | Procuring portal name |
| `recommendation` | `TEXT` | `NOT NULL` | STRONG_BID, CONDITIONAL_BID, RED_FLAG_NO_BID |
| `qualification_score` | `NUMERIC(4, 2)` | `DEFAULT 0.0` | Overall score (0.0 to 5.0) |
| `scorecard_data` | `JSONB` | `NOT NULL DEFAULT '{}'::jsonb` | Full QualificationScorecard JSON |
| `created_at` | `TIMESTAMPTZ` | `DEFAULT NOW()` | Timestamp of audit |

---

## 5. Row-Level Security (RLS) Policies
Row-Level Security is strictly enabled on every table. Users can only select, insert, update, or delete their own rows:

```sql
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.saved_tenders ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tender_audits ENABLE ROW LEVEL SECURITY;

CREATE POLICY "profiles_owner_access" ON public.profiles
  FOR ALL TO authenticated
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "saved_tenders_owner_access" ON public.saved_tenders
  FOR ALL TO authenticated
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "tender_audits_owner_access" ON public.tender_audits
  FOR ALL TO authenticated
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);
```
