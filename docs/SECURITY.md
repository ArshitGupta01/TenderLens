# TenderLens Application Security Standard & AI Audit Protocol
==================================================================

> **Mandatory Security Specification:** All developers and AI coding assistants must strictly enforce these 20 security rules across the TenderLens codebase. Never introduce patterns that violate these constraints.

---

## 1. Core Security Rules (20-Point Specification)

### 1.1 Injection & Input Handling
1. **SQL Injection (SQLi):** Parameterized queries and Supabase PostgREST ORM calls are enforced everywhere. Raw user-input concatenation into SQL strings is strictly forbidden.
2. **Cross-Site Scripting (XSS):** All dynamic user inputs and extracted tender text are sanitized and escaped before DOM rendering. Direct sinks like `innerHTML` or `dangerouslySetInnerHTML` are never used without strict sanitization; DOM nodes are constructed via `document.createElement`, `textContent`, and safe DOM utilities.
3. **Command Injection:** User-controlled inputs are never passed to system shells, `exec`, `eval`, or subprocesses.
4. **CSRF Protection:** State-changing requests use Supabase PKCE flow with anti-CSRF protections and `SameSite` cookie attributes.
5. **File Uploads:** Uploaded documents (when supported) must strictly validate file extensions (`.pdf`, `.txt`, `.docx`), MIME types, and magic bytes (`%PDF-`). Strict size limits (max 25MB) are enforced, and files are processed outside web roots.
6. **SSRF Prevention:** In `TinyFishService` and crawler services, outbound URLs are strictly whitelisted and validated against approved procurement domains (`gem.gov.in`, `eprocure.gov.in`, `bhel.com`, `icmr.nic.in`, `etenders.hry.nic.in`) to prevent internal network scanning and SSRF attacks.

### 1.2 Authentication & Access Control
7. **Broken Object Level Authorization (BOLA / IDOR):** Every persistence route (`/api/v1/audits/save`, `/api/v1/audits/user/{user_id}`, `/api/v1/profile/sync/{user_id}`, `/api/v1/profile/sync`) validates the incoming Bearer token subject against `user_id`, guaranteeing users can only read, write, or delete their own records.
8. **Server-Side Permissions:** Role and ownership checks are enforced on the FastAPI backend layer and the PostgreSQL database layer, never solely in the browser UI.
9. **Row-Level Security (RLS):** All Supabase tables (`public.profiles`, `public.saved_tenders`, `public.tender_audits`) enforce strict PostgreSQL RLS policies (`auth.uid() = user_id`).
10. **Password Security:** Supabase Auth hashes all passwords using modern slow hashing algorithms (bcrypt/Argon2id). Passwords are never stored, logged, or transmitted in plaintext.
11. **Multi-Factor Authentication (MFA):** Supabase MFA hooks and TOTP verification are supported for sensitive account changes.
12. **Session & Token Expiry:** JWT tokens, refresh tokens, and password recovery tokens have strict expiration and automatic PKCE rotation rules.
13. **Email Verification:** Free-tier or custom SMTP email confirmation is required for self-registered accounts. Rate limits are handled gracefully.
14. **Rate Limiting (Auth & API):** Rate limiting is active on authentication attempts, registration, password resets, and web intelligence/search endpoints to prevent brute-force and resource exhaustion.

### 1.3 Secrets & Token Management
15. **JWT Secrets:** High-entropy cryptographic secrets sign and verify Supabase Auth tokens exclusively on the server.
16. **API Secrets Hygiene:** `TINYFISH_API_KEY`, `GEMINI_API_KEY`, `TAVILY_API_KEY`, and `SUPABASE_SERVICE_ROLE_KEY` are stored strictly in private server-side environment variables (`.env`, git-ignored). Only the public `SUPABASE_PUBLISHABLE_KEY` and public `GOOGLE_CLIENT_ID` are exposed to browser clients via `/api/v1/auth/config`.
17. **Client Storage Hygiene:** Sensitive tokens and credentials are never stored in unencrypted client storage. Supabase client manages sessions using secure PKCE storage.
18. **Default Credentials:** Default passwords and sample credentials must never be committed to source control or exposed in production environments.

### 1.4 Configuration, Deployment & Hygiene
19. **CORS Settings:** Cross-Origin Resource Sharing is locked down to explicit domain whitelists (`CORS_ORIGINS`). Wildcard (`*`) origins are strictly prohibited in production.
20. **Clean Logs & Source Maps:** Production builds disable source maps. Loggers sanitize stack traces, credentials, tokens, and PII before writing.

---

## 2. Pre-Launch Verification Gate

Before any release or production deployment:
- [x] **01. SQL Injection:** Parameterized PostgREST queries enforced.
- [x] **02. XSS Protection:** `textContent` and safe element creation used throughout frontend scripts.
- [x] **03. CSRF Protection:** Anti-CSRF tokens & `SameSite` cookies active.
- [x] **04. File Uploads:** Validated by MIME/magic bytes, size-limited.
- [x] **05. SSRF Check:** Allowed procurement domains whitelisted in `Settings.ALLOWED_DOMAINS`.
- [x] **06. BOLA / IDOR Fixed:** Bearer token ownership check enforced in `backend/main.py`.
- [x] **07. Rate Limiting:** Active on login, search, and audit pipelines.
- [x] **08. Password Hashing:** Supabase bcrypt/Argon2 active.
- [x] **09. MFA Support:** Supported via Supabase Auth.
- [x] **10. Server Permissions:** Enforced on backend and database levels.
- [x] **11. Row-Level Security:** Verified on `profiles`, `saved_tenders`, `tender_audits`.
- [x] **12. JWT Secrets:** High-entropy signing keys on server only.
- [x] **13. API Secrets:** Zero private API keys in Git history or client bundles.
- [x] **14. Local Storage Clean:** No session-jacking sensitive credentials stored.
- [x] **15. Default Credentials:** No hardcoded passwords in repository.
- [x] **16. CORS Locked Down:** Configured via `CORS_ORIGINS`.
- [x] **17. Webhook Signatures:** Cryptographic verification supported.
- [x] **18. Source Maps Stripped:** Disabled in production builds.
- [x] **19. Clean Logs & Errors:** No PII or stack traces in client responses.
- [x] **20. Dependencies Audited:** All packages locked and audited via `uv`.
