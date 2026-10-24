# TenderLens — Supabase Cloud Database & Authentication (Free Tier Guide)

TenderLens uses **Supabase** (managed PostgreSQL + Auth) to eliminate the complexity of running a local monolithic database server, Docker containers, or managing authentication credentials.

With a **free Supabase account**, you get:
- Full PostgreSQL database with automatic backups
- Managed Authentication (Email/Password, Password Recovery)
- Instant Row-Level Security (RLS) ensuring strict tenant isolation
- Fast PostgREST API for client and backend persistence

---

## 🚀 3-Minute Setup Instructions

### 1. Create Your Free Project
1. Go to [supabase.com](https://supabase.com) and sign in (or create a free account).
2. Click **"New Project"**, choose an organization, give it a name (e.g. `tenderlens-db`), and set a database password.
3. Select your nearest AWS region (e.g. `ap-south-1` for Mumbai / India) and click **Create new project**.

---

### 2. Copy Your API Keys
In your Supabase project dashboard:
1. Navigate to **Project Settings** (gear icon at bottom-left) > **API**.
2. Copy two values:
   - **Project URL**: `https://<your-project-ref>.supabase.co`
   - **Project API Keys (`anon` / `public`)**: A long string (starts with `eyJ...` or `sb_publishable_...`).
   - *(Optional)* **`service_role` key**: If you wish to allow backend admin operations.

Open your TenderLens `.env` file (in the project root) and paste them:
```env
# Supabase Cloud Database & Auth (Free Tier)
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
# Optional:
# SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1Ni...
```

---

### 3. Run the Database Schema Migration
1. In the Supabase left navigation bar, click on **SQL Editor** (`>_`).
2. Click **"New query"**.
3. Open [`supabase/setup.sql`](setup.sql) in this repository, copy all contents, paste it into the query box, and click **Run** (green button).
4. You will see `Success. No rows returned`.

This creates three tables with Row-Level Security enabled:
| Table | Description | Access Policy |
| :--- | :--- | :--- |
| **`public.profiles`** | Corporate identity & financial/statutory BidderProfile (turnover, MSME, certifications) | Owner-only (`auth.uid() = user_id`) |
| **`public.saved_tenders`** | Live tender opportunities bookmarked from GeM, CPPP, or BHEL searches | Owner-only (`auth.uid() = user_id`) |
| **`public.tender_audits`** | Historical AI qualification scorecards, deterministic gate results & strategy pillars | Owner-only (`auth.uid() = user_id`) |

---

## 🔍 Verification

1. Start your TenderLens backend:
   ```bash
   uv run uvicorn backend.main:app --reload --port 8000
   ```
2. Open `http://127.0.0.1:8000/healthz` in your browser. You will see:
   ```json
   {
     "status": "healthy",
     "service": "TenderLens Backend Engine",
     "version": "1.0.1",
     "supabase_configured": true,
     "supabase_status": {
       "configured": true,
       "connected": true,
       "free_tier_ready": true
     }
   }
   ```
3. Open `http://127.0.0.1:8000/` (or `account.html`).
   - Click **Sign Up** to create an account.
   - Save a bidder profile or bookmark a live tender notice.
   - Everything syncs automatically to your cloud Supabase database!
