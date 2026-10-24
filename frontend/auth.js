(() => {
  const apiUrlFromMeta = document.querySelector('meta[name="tenderlens-api"]')?.content.trim();
  const isLocalPreview = ['localhost', '127.0.0.1'].includes(window.location.hostname);
  const apiBaseUrl = (apiUrlFromMeta || (isLocalPreview ? 'http://127.0.0.1:8000' : '')).replace(/\/$/, '');
  const currentPage = window.location.pathname.split('/').pop() || 'index.html';
  let supabaseClient = null;
  let signedInUser = null;
  let currentSession = null;
  let profileCache = null;
  let authConfigCache = null;
  const EYE_OPEN_SVG = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>';
  const EYE_CLOSED_SVG = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.88 9.88a3 3 0 1 0 4.24 4.24"/><path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68"/><path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61"/><line x1="2" x2="22" y1="2" y2="22"/></svg>';

  // Immediate recovery check on script evaluation
  var urlParams = new URLSearchParams(window.location.search);
  var hashStr = window.location.hash || '';
  if (urlParams.get('mode') === 'reset' || hashStr.indexOf('type=recovery') !== -1) {
    document.documentElement.classList.add('is-recovery-mode');
    if (document.body) document.body.classList.add('is-recovery-mode');
  }


  function setStatus(element, message, state = '') {
    if (!element) return;
    element.textContent = message;
    if (state) element.dataset.state = state;
    else delete element.dataset.state;
  }

  function setEveryStatus(selector, message, state = '') {
    document.querySelectorAll(selector).forEach((element) => setStatus(element, message, state));
  }

  function accountRedirect() {
    const requested = new URLSearchParams(window.location.search).get('next');
    return ['account.html', 'saved-tenders.html', 'strategy.html'].includes(requested) ? requested : 'account.html';
  }

  function updateHeader() {
    const hasAccount = Boolean(signedInUser);
    document.querySelectorAll('[data-auth-signin]').forEach((link) => {
      link.href = hasAccount ? 'account.html' : 'signin.html';
      link.textContent = hasAccount ? 'My account' : 'Sign in';
    });
    document.querySelectorAll('[data-auth-signup]').forEach((link) => {
      link.href = hasAccount ? 'saved-tenders.html' : 'signup.html';
      link.innerHTML = hasAccount ? 'Saved tenders <span aria-hidden="true">↗</span>' : 'Create account <span aria-hidden="true">↗</span>';
    });
    document.querySelectorAll('[data-account-email]').forEach((element) => {
      element.textContent = signedInUser?.email || '';
    });
    document.querySelectorAll('[data-account-name]').forEach((element) => {
      element.textContent = profileCache?.full_name || signedInUser?.user_metadata?.full_name || signedInUser?.email?.split('@')[0] || 'Your account';
    });
    const visibleName = profileCache?.full_name || signedInUser?.user_metadata?.full_name || signedInUser?.email || '';
    const initials = visibleName.split(/[\s@._-]+/).filter(Boolean).slice(0, 2).map((part) => part[0].toUpperCase()).join('') || 'TL';
    document.querySelectorAll('[data-account-initials]').forEach((element) => { element.textContent = initials; });
    document.querySelectorAll('[data-auth-signed-in]').forEach((element) => { element.hidden = !hasAccount; });
    document.querySelectorAll('[data-auth-signed-out]').forEach((element) => { element.hidden = hasAccount; });
    document.dispatchEvent(new CustomEvent('tenderlens:auth-state', { detail: { user: signedInUser, profile: profileCache } }));
  }

  function setConfigState(available, message = '') {
    document.querySelectorAll('[data-auth-config-needed]').forEach((element) => { element.hidden = available; });
    if (!available) {
      setEveryStatus('[data-auth-status]', message || 'Account sign-in is not connected yet. Follow the setup steps in the easy guide.', 'unavailable');
      document.querySelectorAll('[data-auth-submit], [data-password-reset], [data-password-update]').forEach((button) => {
        button.disabled = true;
      });
    }
  }

  async function loadProfile() {
    if (!supabaseClient || !signedInUser) return { data: null, error: new Error('Sign in first.') };
    const { data, error } = await supabaseClient
      .from('profiles')
      .select('full_name, organization, bidder_type, years_active, region, is_msme_registered, msme_category, is_startup_recognized, turnover_year_1_lakhs, turnover_year_2_lakhs, turnover_year_3_lakhs, years_in_business, local_content_percentage, held_certifications, past_similar_project_values_lakhs')
      .eq('user_id', signedInUser.id)
      .maybeSingle();
    if (!error) {
      profileCache = data || null;
      updateHeader();
    }
    return { data, error };
  }

  async function saveProfile(profile) {
    if (!supabaseClient || !signedInUser) return { error: new Error('Sign in to sync this profile between devices.') };
    const row = {
      user_id: signedInUser.id,
      full_name: String(profile.full_name || profileCache?.full_name || signedInUser.user_metadata?.full_name || '').trim().slice(0, 100),
      organization: String(profile.organization || profileCache?.organization || '').trim().slice(0, 100),
      bidder_type: String(profile.bidder_type || profile.bidderType || profileCache?.bidder_type || '').trim().slice(0, 60),
      years_active: String(profile.years_active || profile.years || profileCache?.years_active || '').trim().slice(0, 40),
      region: String(profile.region || profileCache?.region || '').trim().slice(0, 60),
      updated_at: new Date().toISOString()
    };

    if (profile.is_msme_registered !== undefined) row.is_msme_registered = Boolean(profile.is_msme_registered);
    if (profile.msme_category !== undefined) row.msme_category = String(profile.msme_category || '').trim().slice(0, 30);
    if (profile.is_startup_recognized !== undefined) row.is_startup_recognized = Boolean(profile.is_startup_recognized);
    if (profile.turnover_year_1_lakhs !== undefined && profile.turnover_year_1_lakhs !== '') {
      row.turnover_year_1_lakhs = Math.max(0, Number(profile.turnover_year_1_lakhs) || 0);
    }
    if (profile.turnover_year_2_lakhs !== undefined && profile.turnover_year_2_lakhs !== '') {
      row.turnover_year_2_lakhs = Math.max(0, Number(profile.turnover_year_2_lakhs) || 0);
    }
    if (profile.turnover_year_3_lakhs !== undefined && profile.turnover_year_3_lakhs !== '') {
      row.turnover_year_3_lakhs = Math.max(0, Number(profile.turnover_year_3_lakhs) || 0);
    }
    if (profile.years_in_business !== undefined && profile.years_in_business !== '') {
      row.years_in_business = Math.max(0, Math.round(Number(profile.years_in_business) || 0));
    }
    if (profile.local_content_percentage !== undefined && profile.local_content_percentage !== '') {
      row.local_content_percentage = Math.min(100, Math.max(0, Number(profile.local_content_percentage) || 0));
    }
    if (profile.held_certifications !== undefined) {
      row.held_certifications = Array.isArray(profile.held_certifications)
        ? profile.held_certifications
        : String(profile.held_certifications || '')
            .split(',')
            .map((item) => item.trim())
            .filter(Boolean)
            .slice(0, 25);
    }

    const { data, error } = await supabaseClient.from('profiles').upsert(row, { onConflict: 'user_id' }).select().single();
    if (!error) {
      profileCache = data;
      updateHeader();
    }
    return { data, error };
  }

  async function saveTender(tender) {
    if (!supabaseClient || !signedInUser) return { error: new Error('Sign in to save live tender notices across devices.') };
    let sourceUrl;
    try {
      sourceUrl = new URL(tender?.source_url || tender?.url);
      if (!['https:', 'http:'].includes(sourceUrl.protocol)) throw new Error('invalid');
    } catch (error) {
      return { error: new Error('This notice does not have a valid official link to save.') };
    }
    const row = {
      user_id: signedInUser.id,
      title: String(tender.title || 'Tender notice').trim().slice(0, 240),
      source_url: sourceUrl.href.slice(0, 2048),
      source_portal: String(tender.source_portal || 'Tender portal').trim().slice(0, 120),
      snippet: String(tender.snippet || '').trim().slice(0, 1200)
    };
    const { data, error } = await supabaseClient
      .from('saved_tenders')
      .upsert(row, { onConflict: 'user_id,source_url' })
      .select()
      .single();
    return { data, error };
  }

  async function removeTender(id) {
    if (!supabaseClient || !signedInUser) return { error: new Error('Sign in to manage saved tenders.') };
    return supabaseClient.from('saved_tenders').delete().eq('id', id).eq('user_id', signedInUser.id);
  }

  function profileErrorMessage(error) {
    if (error?.code === '42P01' || error?.code === 'PGRST205') {
      return 'The account tables are not set up yet. Follow the database setup in the easy guide, then try again.';
    }
    return error?.message || 'Something went wrong. Please try again.';
  }

  function fillProfileFields(profile) {
    const values = {
      'account-full-name': profile?.full_name || signedInUser?.user_metadata?.full_name || '',
      'account-organization': profile?.organization || '',
      'account-bidder-type': profile?.bidder_type || '',
      'account-years': profile?.years_active || '',
      'account-region': profile?.region || '',
      'account-msme-category': profile?.msme_category || '',
      'account-years-numeric': profile?.years_in_business != null ? String(profile.years_in_business) : '',
      'account-turnover-1': profile?.turnover_year_1_lakhs != null ? String(profile.turnover_year_1_lakhs) : '',
      'account-turnover-2': profile?.turnover_year_2_lakhs != null ? String(profile.turnover_year_2_lakhs) : '',
      'account-turnover-3': profile?.turnover_year_3_lakhs != null ? String(profile.turnover_year_3_lakhs) : '',
      'account-local-content': profile?.local_content_percentage != null ? String(profile.local_content_percentage) : '',
      'account-certifications': Array.isArray(profile?.held_certifications) ? profile.held_certifications.join(', ') : ''
    };
    Object.entries(values).forEach(([id, value]) => {
      const field = document.getElementById(id);
      if (field && typeof value === 'string') field.value = value;
    });
    const msmeCheck = document.getElementById('account-is-msme');
    if (msmeCheck) msmeCheck.checked = Boolean(profile?.is_msme_registered);
    const startupCheck = document.getElementById('account-is-startup');
    if (startupCheck) startupCheck.checked = Boolean(profile?.is_startup_recognized);
  }

  async function initAccountProfile() {
    const form = document.querySelector('[data-account-profile-form]');
    if (!form || !signedInUser) return;
    const status = document.querySelector('[data-account-profile-status]');
    const result = await loadProfile();
    if (result.error) {
      setStatus(status, profileErrorMessage(result.error), 'error');
      return;
    }
    fillProfileFields(result.data);
    setStatus(status, result.data ? 'Your bidder profile is saved to your account and available across devices and Strategy Studio.' : 'Add your business basics and optional capacity metrics, then save them to your account.', '');
    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      const fields = new FormData(form);
      const button = form.querySelector('[type="submit"]');
      if (button) button.disabled = true;
      setStatus(status, 'Saving your account profile…', 'loading');
      const payload = {
        full_name: fields.get('full_name'),
        organization: fields.get('organization'),
        bidder_type: fields.get('bidder_type'),
        years_active: fields.get('years_active'),
        region: fields.get('region')
      };
      if (form.elements.namedItem('is_msme_registered')) {
        payload.is_msme_registered = form.elements.namedItem('is_msme_registered').checked;
      }
      if (form.elements.namedItem('is_startup_recognized')) {
        payload.is_startup_recognized = form.elements.namedItem('is_startup_recognized').checked;
      }
      if (fields.has('msme_category')) payload.msme_category = fields.get('msme_category');
      if (fields.has('years_in_business') && fields.get('years_in_business') !== '') {
        payload.years_in_business = fields.get('years_in_business');
      }
      if (fields.has('turnover_year_1_lakhs') && fields.get('turnover_year_1_lakhs') !== '') {
        payload.turnover_year_1_lakhs = fields.get('turnover_year_1_lakhs');
      }
      if (fields.has('turnover_year_2_lakhs') && fields.get('turnover_year_2_lakhs') !== '') {
        payload.turnover_year_2_lakhs = fields.get('turnover_year_2_lakhs');
      }
      if (fields.has('turnover_year_3_lakhs') && fields.get('turnover_year_3_lakhs') !== '') {
        payload.turnover_year_3_lakhs = fields.get('turnover_year_3_lakhs');
      }
      if (fields.has('local_content_percentage') && fields.get('local_content_percentage') !== '') {
        payload.local_content_percentage = fields.get('local_content_percentage');
      }
      if (fields.has('held_certifications')) {
        payload.held_certifications = fields.get('held_certifications');
      }
      const saved = await saveProfile(payload);
      if (button) button.disabled = false;
      setStatus(status, saved.error ? profileErrorMessage(saved.error) : 'Profile saved to Supabase Postgres (RLS protected). Ready across devices and Strategy Studio.', saved.error ? 'error' : 'success');
    });
  }

  function makeSavedTenderCard(tender) {
    const card = document.createElement('article');
    card.className = 'saved-tender-card';
    const source = document.createElement('p');
    source.className = 'saved-tender-source';
    source.textContent = tender.source_portal || 'Tender portal';
    const title = document.createElement('h3');
    title.textContent = tender.title || 'Tender notice';
    const snippet = document.createElement('p');
    snippet.textContent = tender.snippet || 'Open the official notice to review its latest terms.';
    const actions = document.createElement('div');
    actions.className = 'saved-tender-actions';
    const link = document.createElement('a');
    link.href = tender.source_url;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    link.textContent = 'Open official notice ↗';
    const remove = document.createElement('button');
    remove.type = 'button';
    remove.dataset.removeSavedTender = tender.id;
    remove.textContent = 'Remove';
    actions.append(link, remove);
    card.append(source, title, snippet, actions);
    return card;
  }

  async function initSavedTenders() {
    const list = document.querySelector('[data-saved-tender-list]');
    if (!list || !signedInUser) return;
    const status = document.querySelector('[data-saved-tender-status]');
    setStatus(status, 'Loading your saved notices…', 'loading');
    const { data, error } = await supabaseClient
      .from('saved_tenders')
      .select('id, title, source_url, source_portal, snippet, created_at')
      .eq('user_id', signedInUser.id)
      .order('created_at', { ascending: false });
    if (error) {
      setStatus(status, profileErrorMessage(error), 'error');
      return;
    }
    list.replaceChildren(...data.map(makeSavedTenderCard));
    setStatus(status, data.length ? `${data.length} notice${data.length === 1 ? '' : 's'} saved to your account.` : 'No live notices saved yet. Search for current tenders and choose “Save to account”.', data.length ? 'success' : '');
  }

  async function handleSignIn(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const status = form.querySelector('[data-auth-status]');
    const fields = new FormData(form);
    setStatus(status, 'Signing you in…', 'loading');
    const { error } = await supabaseClient.auth.signInWithPassword({
      email: String(fields.get('email') || '').trim(),
      password: String(fields.get('password') || '')
    });
    if (error) {
      setStatus(status, error.message, 'error');
      return;
    }
    window.location.assign(accountRedirect());
  }

  function initDemoLogin() {
    document.querySelectorAll('[data-demo-fill]').forEach((button) => {
      if (button.dataset.demoBound === 'true') return;
      button.dataset.demoBound = 'true';
      button.addEventListener('click', () => {
        const card = button.closest('[data-demo-account]');
        const form = document.querySelector('[data-signin-form]');
        const email = form?.querySelector('[name="email"]');
        const passwordInput = form?.querySelector('[name="password"]');
        if (!card || !email) return;
        email.value = card.dataset.demoEmail || '';
        setStatus(card.querySelector('[data-demo-status]'), 'Demo email filled. Enter the demo password privately, then choose “Sign in”.', 'success');
        passwordInput?.focus({ preventScroll: true });
      });
    });
  }

  async function handleSignUp(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const status = form.querySelector('[data-auth-status]');
    const fields = new FormData(form);
    const password = String(fields.get('password') || '');
    if (password !== String(fields.get('password_confirm') || '')) {
      setStatus(status, 'Those passwords do not match. Check them and try again.', 'error');
      return;
    }
    setStatus(status, 'Creating your account…', 'loading');
    const { data, error } = await supabaseClient.auth.signUp({
      email: String(fields.get('email') || '').trim(),
      password,
      options: {
        data: { full_name: String(fields.get('full_name') || '').trim() },
        emailRedirectTo: new URL('account.html', window.location.href).href
      }
    });
    if (error) {
      const msg = String(error.message || '');
      if (error.status === 429 || msg.toLowerCase().includes('rate limit')) {
        setStatus(
          status,
          'Supabase free-tier confirmation email limit reached (2–3 emails/hour). You can sign in immediately using the pre-confirmed Shared Demo Account on the Sign in page, or disable "Confirm email" in Supabase Dashboard → Authentication → Providers → Email.',
          'error'
        );
      } else {
        setStatus(status, msg, 'error');
      }
      return;
    }
    if (data.session) {
      window.location.assign('account.html');
      return;
    }
    setStatus(status, 'Check your email for a confirmation link. After confirming, sign in to finish your profile.', 'success');
  }

  async function handlePasswordRecovery() {
    const form = document.querySelector('[data-password-recovery]');
    if (!form || form.dataset.recoveryBound === 'true') return;
    form.dataset.recoveryBound = 'true';
    form.hidden = false;

    // Activate clean recovery mode: hide story and other sections, center reset card
    document.documentElement.classList.add('is-recovery-mode');
    document.body.classList.add('is-recovery-mode');
    document.querySelector('.auth-layout')?.classList.add('is-recovery-mode');

    const story = document.querySelector('.auth-story');
    if (story) story.hidden = true;

    document.querySelector('[data-signin-form]')?.setAttribute('hidden', '');
    document.querySelector('[data-auth-title]')?.replaceChildren(document.createTextNode('Choose a new password'));
    const intro = document.querySelector('.auth-intro');
    if (intro) intro.textContent = 'Enter and confirm your new secure password.';

    // Hide standard sign-in switch footer and reveal return-to-signin link
    document.querySelectorAll('[data-signin-switch]').forEach(el => el.hidden = true);
    document.querySelectorAll('[data-recovery-footer]').forEach(el => el.hidden = false);

    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      const fields = new FormData(form);
      const password = String(fields.get('password') || '');
      const confirm = String(fields.get('password_confirm') || '');
      const status = form.querySelector('[data-auth-status]');
      if (password.length < 8) return setStatus(status, 'Password must be at least 8 characters.', 'error');
      if (password !== confirm) return setStatus(status, 'Those passwords do not match.', 'error');
      if (!supabaseClient) return setStatus(status, 'Authentication service is not connected.', 'error');
      setStatus(status, 'Updating password…', 'loading');
      const { error } = await supabaseClient.auth.updateUser({ password });
      if (error) return setStatus(status, error.message, 'error');
      setStatus(status, 'Password updated successfully! Redirecting to your account…', 'success');
      window.setTimeout(() => window.location.assign('account.html'), 1000);
    }, { once: true });
  }

  async function init() {
    initDemoLogin();
    if (!apiBaseUrl || !window.supabase?.createClient) {
      setConfigState(false, 'Account sign-in needs the TenderLens API and Supabase settings. Follow the account setup in the easy guide.');
      return null;
    }
    let config;
    try {
      const response = await fetch(`${apiBaseUrl}/api/v1/auth/config`, { headers: { Accept: 'application/json' } });
      if (!response.ok) throw new Error('The TenderLens API could not load account settings.');
      config = await response.json();
      authConfigCache = config;
    } catch (error) {
      setConfigState(false, 'Could not reach the TenderLens API. Start the FastAPI service and check the easy guide.');
      return null;
    }
    if (!config.configured || !config.supabase_url || !config.publishable_key) {
      setConfigState(false, 'Account sign-in is not configured yet. Add your Supabase URL and publishable key to the private .env file, then restart FastAPI.');
      return null;
    }
    supabaseClient = window.supabase.createClient(config.supabase_url, config.publishable_key, {
      auth: { flowType: 'pkce', autoRefreshToken: true, persistSession: true, detectSessionInUrl: true }
    });
    const { data, error } = await supabaseClient.auth.getSession();
    if (error) setEveryStatus('[data-auth-status]', error.message, 'error');
    currentSession = data?.session || null;
    signedInUser = currentSession?.user || null;
    setConfigState(true);
    updateHeader();

    supabaseClient.auth.onAuthStateChange((event, session) => {
      currentSession = session || null;
      signedInUser = session?.user || null;
      updateHeader();
      if (event === 'PASSWORD_RECOVERY') handlePasswordRecovery();
    });
    document.querySelectorAll('[data-signin-form]').forEach((form) => form.addEventListener('submit', handleSignIn));
    document.querySelectorAll('[data-signup-form]').forEach((form) => form.addEventListener('submit', handleSignUp));
    document.querySelectorAll('[data-password-reset]').forEach((button) => button.addEventListener('click', async () => {
      const email = document.querySelector('[name="email"]')?.value.trim();
      const status = document.querySelector('[data-signin-form] [data-auth-status]');
      if (!email) return setStatus(status, 'Enter your email address first, then choose reset password.', 'error');
      const { error: resetError } = await supabaseClient.auth.resetPasswordForEmail(email, {
        redirectTo: new URL('signin.html?mode=reset', window.location.href).href
      });
      setStatus(status, resetError ? resetError.message : 'If an account uses that email, a password reset link is on its way.', resetError ? 'error' : 'success');
    }));
    document.querySelectorAll('[data-password-recovery]').forEach((form) => {
      if (new URLSearchParams(window.location.search).get('mode') === 'reset') handlePasswordRecovery();
    });
    document.querySelectorAll('[data-signout]').forEach((button) => button.addEventListener('click', async () => {
      const { error: signOutError } = await supabaseClient.auth.signOut();
      if (signOutError) return setEveryStatus('[data-auth-status]', signOutError.message, 'error');
      window.location.assign('index.html');
    }));
        // Enhanced password visibility toggles
    document.querySelectorAll('.auth-password-toggle').forEach((button) => {
      button.addEventListener('click', (e) => {
        e.preventDefault();
        const wrapper = button.closest('.auth-input-wrapper');
        const input = wrapper?.querySelector('input');
        if (!input) return;
        const isPassword = input.type === 'password';
        input.type = isPassword ? 'text' : 'password';
        const icon = button.querySelector('.eye-icon');
        if (icon) icon.innerHTML = isPassword ? EYE_CLOSED_SVG : EYE_OPEN_SVG;
        button.setAttribute('aria-label', isPassword ? 'Hide password' : 'Show password');
        input.focus();
      });
    });

    // Enhanced password strength meter
    const signupPwInput = document.querySelector('#signup-password');
    const meterWrap = document.querySelector('#password-meter');
    if (signupPwInput && meterWrap) {
      signupPwInput.addEventListener('input', () => {
        const val = signupPwInput.value;
        const bars = meterWrap.querySelectorAll('.meter-bar');
        const label = meterWrap.querySelector('[data-meter-label]');
        if (!val) {
          bars.forEach((b) => { b.className = 'meter-bar'; });
          if (label) {
            label.textContent = 'Password strength';
            label.className = 'password-meter-label';
          }
          return;
        }
        let score = 0;
        if (val.length >= 8) score++;
        if (/[0-9]/.test(val) || /[^A-Za-z0-9]/.test(val)) score++;
        if (val.length >= 10 && /[A-Z]/.test(val) && /[a-z]/.test(val)) score++;

        bars.forEach((b, idx) => {
          if (idx < score) {
            b.className = 'meter-bar is-active ' + (score === 1 ? 'is-weak' : score === 2 ? 'is-medium' : 'is-strong');
          } else {
            b.className = 'meter-bar';
          }
        });

        if (label) {
          label.textContent = score === 1 ? 'Weak ? add numbers or symbols' : score === 2 ? 'Good ? meets security baseline' : 'Strong ? robust enterprise password';
          label.className = 'password-meter-label ' + (score === 1 ? 'text-weak' : score === 2 ? 'text-medium' : 'text-strong');
        }
      });
    }

    await initAccountProfile();
    await initSavedTenders();
    if (signedInUser && ['signin.html', 'signup.html'].includes(currentPage) && new URLSearchParams(window.location.search).get('mode') !== 'reset') {
      window.location.replace(accountRedirect());
      return supabaseClient;
    }
    if (currentPage === 'index.html' && signedInUser) {
      const localForm = document.getElementById('bidder-profile-form');
      if (localForm) {
        const result = await loadProfile();
        if (result.data) {
          const ids = { organization: 'bidder-profile-name', bidder_type: 'bidder-profile-type', years_active: 'bidder-profile-years', region: 'bidder-profile-region' };
          Object.entries(ids).forEach(([key, id]) => {
            const field = document.getElementById(id);
            if (field && result.data[key]) field.value = result.data[key];
          });
          const status = document.getElementById('profile-save-status');
          if (status) status.textContent = 'Your profile is synced to your account and available on other devices.';
          const label = document.querySelector('.profile-storage-label');
          if (label) label.textContent = 'ACCOUNT SYNC';
          const privacyStrong = document.querySelector('.profile-privacy strong');
          const privacySmall = document.querySelector('.profile-privacy small');
          if (privacyStrong) privacyStrong.textContent = 'Synced to your account';
          if (privacySmall) privacySmall.textContent = 'Your basic profile is available when you sign in on another device. Keep sensitive records out.';
        }
      }
    }
    document.addEventListener('click', async (event) => {
      const saveButton = event.target.closest('[data-live-save]');
      if (saveButton) {
        if (saveButton.disabled) return;
        const payload = JSON.parse(saveButton.dataset.liveSave || '{}');
        const { error: saveError } = await saveTender(payload);
        if (saveError) {
          const status = saveButton.closest('.live-result-card')?.querySelector('[data-live-save-status]');
          if (status && !signedInUser && supabaseClient) {
            setStatus(status, 'Sign in to save this notice across your devices. ', 'error');
            const signInLink = document.createElement('a');
            signInLink.href = 'signin.html?next=saved-tenders.html';
            signInLink.textContent = 'Sign in';
            status.append(signInLink);
          } else {
            setStatus(status, supabaseClient ? profileErrorMessage(saveError) : 'Account setup is not complete. See the account setup steps in the easy guide.', 'error');
          }
          return;
        }
        saveButton.textContent = 'Saved to account';
        saveButton.disabled = true;
        setStatus(saveButton.closest('.live-result-card')?.querySelector('[data-live-save-status]'), 'Saved across your devices.', 'success');
      }
      const removeButton = event.target.closest('[data-remove-saved-tender]');
      if (removeButton) {
        removeButton.disabled = true;
        const { error: removeError } = await removeTender(removeButton.dataset.removeSavedTender);
        if (removeError) {
          removeButton.disabled = false;
          setStatus(document.querySelector('[data-saved-tender-status]'), profileErrorMessage(removeError), 'error');
          return;
        }
        removeButton.closest('.saved-tender-card')?.remove();
        const remaining = document.querySelectorAll('.saved-tender-card').length;
        setStatus(document.querySelector('[data-saved-tender-status]'), remaining ? `${remaining} saved notice${remaining === 1 ? '' : 's'} remaining.` : 'No live notices saved yet. Search for current tenders and choose “Save to account”.');
      }
    });
    document.dispatchEvent(new CustomEvent('tenderlens:auth-ready', { detail: { user: signedInUser, client: supabaseClient } }));
    return supabaseClient;
  }

  const ready = init();
  window.TenderLensAuth = {
    get client() { return supabaseClient; },
    get user() { return signedInUser; },
    get session() { return currentSession; },
    get profile() { return profileCache; },
    getAccessToken() { return currentSession?.access_token || null; },
    ready,
    saveProfile,
    saveTender,
    loadProfile,
    profileErrorMessage
  };
})();
