(() => {
  const apiUrlFromMeta = document.querySelector('meta[name="tenderlens-api"]')?.content.trim();
  const isLocalPreview = ['localhost', '127.0.0.1'].includes(window.location.hostname);
  const apiBaseUrl = (apiUrlFromMeta || (isLocalPreview ? 'http://127.0.0.1:8000' : '')).replace(/\/$/, '');
  const currentPage = window.location.pathname.split('/').pop() || 'index.html';
  let supabaseClient = null;
  let signedInUser = null;
  let profileCache = null;

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
    return ['account.html', 'saved-tenders.html'].includes(requested) ? requested : 'account.html';
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
    document.dispatchEvent(new CustomEvent('tenderlens:auth-state', { detail: { user: signedInUser } }));
  }

  function setConfigState(available, message = '') {
    document.querySelectorAll('[data-auth-config-needed]').forEach((element) => { element.hidden = available; });
    if (!available) {
      setEveryStatus('[data-auth-status]', message || 'Account sign-in is not connected yet. Follow the setup steps in the easy guide.', 'unavailable');
      document.querySelectorAll('[data-auth-submit], [data-google-signin], [data-password-reset], [data-password-update]').forEach((button) => {
        button.disabled = true;
      });
    }
  }

  async function loadProfile() {
    if (!supabaseClient || !signedInUser) return { data: null, error: new Error('Sign in first.') };
    const { data, error } = await supabaseClient
      .from('profiles')
      .select('full_name, organization, bidder_type, years_active, region')
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
      full_name: String(profile.full_name || signedInUser.user_metadata?.full_name || '').trim().slice(0, 100),
      organization: String(profile.organization || '').trim().slice(0, 100),
      bidder_type: String(profile.bidder_type || profile.bidderType || '').trim().slice(0, 60),
      years_active: String(profile.years_active || profile.years || '').trim().slice(0, 40),
      region: String(profile.region || '').trim().slice(0, 60),
      updated_at: new Date().toISOString()
    };
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
      'account-region': profile?.region || ''
    };
    Object.entries(values).forEach(([id, value]) => {
      const field = document.getElementById(id);
      if (field && typeof value === 'string') field.value = value;
    });
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
    setStatus(status, result.data ? 'Your bidder profile is saved to your account and available on other devices.' : 'Add your business basics, then save them to your account.', '');
    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      const fields = new FormData(form);
      const button = form.querySelector('[type="submit"]');
      if (button) button.disabled = true;
      setStatus(status, 'Saving your account profile…', 'loading');
      const saved = await saveProfile({
        full_name: fields.get('full_name'),
        organization: fields.get('organization'),
        bidder_type: fields.get('bidder_type'),
        years_active: fields.get('years_active'),
        region: fields.get('region')
      });
      if (button) button.disabled = false;
      setStatus(status, saved.error ? profileErrorMessage(saved.error) : 'Profile saved. It will be here when you sign in on another device.', saved.error ? 'error' : 'success');
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
      setStatus(status, error.message, 'error');
      return;
    }
    if (data.session) {
      window.location.assign('account.html');
      return;
    }
    setStatus(status, 'Check your email for a confirmation link. After confirming, sign in to finish your profile.', 'success');
  }

  async function handleGoogleSignIn() {
    if (!supabaseClient) return;
    const { error } = await supabaseClient.auth.signInWithOAuth({
      provider: 'google',
      options: { redirectTo: new URL(accountRedirect(), window.location.href).href }
    });
    if (error) setEveryStatus('[data-auth-status]', error.message, 'error');
  }

  async function handlePasswordRecovery() {
    const form = document.querySelector('[data-password-recovery]');
    if (!form || !supabaseClient || form.dataset.recoveryBound === 'true') return;
    form.dataset.recoveryBound = 'true';
    form.hidden = false;
    document.querySelector('[data-signin-form]')?.setAttribute('hidden', '');
    document.querySelector('[data-auth-title]')?.replaceChildren(document.createTextNode('Choose a new password'));
    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      const fields = new FormData(form);
      const password = String(fields.get('password') || '');
      const confirm = String(fields.get('password_confirm') || '');
      const status = form.querySelector('[data-auth-status]');
      if (password !== confirm) return setStatus(status, 'Those passwords do not match.', 'error');
      const { error } = await supabaseClient.auth.updateUser({ password });
      if (error) return setStatus(status, error.message, 'error');
      setStatus(status, 'Password updated. You can continue to your account.', 'success');
      window.setTimeout(() => window.location.assign('account.html'), 800);
    }, { once: true });
  }

  async function init() {
    if (!apiBaseUrl || !window.supabase?.createClient) {
      setConfigState(false, 'Account sign-in needs the TenderLens API and Supabase settings. Follow the account setup in the easy guide.');
      return null;
    }
    let config;
    try {
      const response = await fetch(`${apiBaseUrl}/api/v1/auth/config`, { headers: { Accept: 'application/json' } });
      if (!response.ok) throw new Error('The TenderLens API could not load account settings.');
      config = await response.json();
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
    signedInUser = data?.session?.user || null;
    setConfigState(true);
    updateHeader();
    supabaseClient.auth.onAuthStateChange((event, session) => {
      signedInUser = session?.user || null;
      updateHeader();
      if (event === 'PASSWORD_RECOVERY') handlePasswordRecovery();
    });
    document.querySelectorAll('[data-signin-form]').forEach((form) => form.addEventListener('submit', handleSignIn));
    document.querySelectorAll('[data-signup-form]').forEach((form) => form.addEventListener('submit', handleSignUp));
    document.querySelectorAll('[data-google-signin]').forEach((button) => button.addEventListener('click', handleGoogleSignIn));
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
    await initAccountProfile();
    await initSavedTenders();
    if (signedInUser && ['signin.html', 'signup.html'].includes(currentPage) && new URLSearchParams(window.location.search).get('mode') !== 'reset') {
      window.location.replace('account.html');
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
    get profile() { return profileCache; },
    ready,
    saveProfile,
    saveTender,
    loadProfile,
    profileErrorMessage
  };
})();
