const evidence = {
  turnover: {
    source: 'BIDDER PROFILE / FINANCIAL CAPACITY',
    title: 'The sample profile clears this threshold.',
    description: 'In this made-up example, the company’s average sales over three years are above the amount asked for. A simple number check marks the requirement as met.'
  },
  certification: {
    source: 'EXTRA BUYER TERMS / PAGE 18',
    title: 'No matching certificate appears in the sample profile.',
    description: 'The example asks for an ISO 9001 certificate, but the sample company details do not show one. A person should check whether a valid certificate is available.'
  },
  exemption: {
    source: 'OFFICIAL UPDATE 02 / PAGE 3 / CHANGED RULE',
    title: 'The amendment changes the earlier exemption language.',
    description: 'This example sends the small-business exemption for a closer check. Keep the earlier wording beside the latest change so a person can compare them.'
  },
  corrigendum: {
    source: 'OFFICIAL UPDATE 02 / LATEST CHANGE',
    title: 'Latest terms in the sample files.',
    description: 'An official update can replace an earlier tender rule. This example shows the newest wording while keeping the old wording available to compare.'
  },
  atc: {
    source: 'EXTRA BUYER TERMS / 24 PAGES',
    title: 'Specific eligibility terms from the buyer.',
    description: 'The buyer’s extra terms may add experience, certificates or product rules. A later official update may change some of these rules.'
  },
  main: {
    source: 'MAIN BID DOCUMENT / 42 PAGES',
    title: 'Baseline requirements for the opportunity.',
    description: 'The main bid contains the starting requirements, deposit and deadlines. A full TenderLens review is planned to compare it with the buyer’s extra terms and later updates.'
  }
};

const reportTabs = Array.from(document.querySelectorAll('.report-tab'));
const reportPanels = Array.from(document.querySelectorAll('.report-panel'));
const evidencePanel = document.getElementById('evidence-detail');
const evidenceRows = Array.from(document.querySelectorAll('[data-evidence]'));

function showEvidence(key, row) {
  const item = evidence[key];
  if (!item || !evidencePanel) return;
  document.getElementById('evidence-source').textContent = item.source;
  document.getElementById('evidence-title').textContent = item.title;
  document.getElementById('evidence-description').textContent = item.description;
  evidencePanel.hidden = false;
  evidenceRows.forEach((button) => button.setAttribute('aria-expanded', button === row ? 'true' : 'false'));
}

function selectReportTab(tab) {
  const panelId = tab.dataset.panel;
  reportTabs.forEach((item) => {
    const selected = item === tab;
    item.classList.toggle('is-active', selected);
    item.setAttribute('aria-selected', String(selected));
    item.tabIndex = selected ? 0 : -1;
  });
  reportPanels.forEach((panel) => {
    const active = panel.id === panelId;
    panel.classList.toggle('is-active', active);
    panel.hidden = !active;
  });
  if (evidencePanel) evidencePanel.hidden = true;
  evidenceRows.forEach((button) => button.setAttribute('aria-expanded', 'false'));
}

reportTabs.forEach((tab, index) => {
  tab.addEventListener('click', () => selectReportTab(tab));
  tab.addEventListener('keydown', (event) => {
    if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
    event.preventDefault();
    const delta = event.key === 'ArrowRight' ? 1 : -1;
    const next = reportTabs[(index + delta + reportTabs.length) % reportTabs.length];
    selectReportTab(next);
    next.focus();
  });
});

evidenceRows.forEach((button) => {
  button.addEventListener('click', () => {
    if (button.getAttribute('aria-expanded') === 'true') {
      evidencePanel.hidden = true;
      button.setAttribute('aria-expanded', 'false');
      return;
    }
    showEvidence(button.dataset.evidence, button);
  });
});

const closeDetail = document.querySelector('.detail-close');
if (closeDetail) {
  closeDetail.addEventListener('click', () => {
    evidencePanel.hidden = true;
    evidenceRows.forEach((button) => button.setAttribute('aria-expanded', 'false'));
  });
}

const audienceProfiles = {
  msme: {
    index: 'PROFILE / 01',
    type: 'INDIAN MSMEs',
    title: 'Bid with your credentials in view.',
    description: 'A future review can check MSME exemption language, certificate requirements and which conditions need a closer read.',
    focus: 'Turnover · exemptions · certifications'
  },
  epc: {
    index: 'PROFILE / 02',
    type: 'EPC CONTRACTORS',
    title: 'Put project history against the clause.',
    description: 'A future review can compare similar-work definitions, contract value bands and past-project evidence across the tender set.',
    focus: 'Experience · project value · scope'
  },
  it: {
    index: 'PROFILE / 03',
    type: 'IT SYSTEM INTEGRATORS',
    title: 'Surface the technical gates early.',
    description: 'The proposed workflow brings OEM authorizations, certification requirements and deployment conditions into one qualification view.',
    focus: 'OEM letters · certificates · capability'
  },
  consultants: {
    index: 'PROFILE / 04',
    type: 'BID CONSULTANTS',
    title: 'Make each client review traceable.',
    description: 'The planned workflow compares opportunities against a bidder profile and keeps clause references beside the recommendation.',
    focus: 'Client profiles · evidence · review trail'
  }
};

const audienceTabs = Array.from(document.querySelectorAll('.audience-tab'));
audienceTabs.forEach((tab) => {
  tab.addEventListener('click', () => {
    audienceTabs.forEach((item) => {
      const selected = item === tab;
      item.classList.toggle('is-active', selected);
      item.setAttribute('aria-selected', String(selected));
      item.tabIndex = selected ? 0 : -1;
    });
    const profile = audienceProfiles[tab.dataset.audience];
    if (!profile) return;
    document.getElementById('audience-index').textContent = profile.index;
    document.getElementById('audience-type').textContent = profile.type;
    document.getElementById('audience-title').textContent = profile.title;
    document.getElementById('audience-description').textContent = profile.description;
    document.getElementById('audience-focus').textContent = profile.focus;
  });
});

const menuToggle = document.querySelector('.menu-toggle');
const primaryNav = document.querySelector('.primary-nav');
if (menuToggle && primaryNav) {
  menuToggle.addEventListener('click', () => {
    const open = menuToggle.getAttribute('aria-expanded') !== 'true';
    menuToggle.setAttribute('aria-expanded', String(open));
    primaryNav.classList.toggle('is-open', open);
  });
  primaryNav.querySelectorAll('a').forEach((link) => {
    link.addEventListener('click', () => {
      menuToggle.setAttribute('aria-expanded', 'false');
      primaryNav.classList.remove('is-open');
    });
  });
}

const year = document.getElementById('current-year');
if (year) year.textContent = String(new Date().getFullYear());

const themeToggle = document.getElementById('theme-toggle');
const themeToggleLabel = document.getElementById('theme-toggle-label');
const themeToggleIcon = themeToggle?.querySelector('.theme-toggle-icon');
const themeColorMeta = document.querySelector('meta[name="theme-color"]');

function applyTheme(theme, save = false) {
  const isDark = theme === 'dark';
  document.documentElement.dataset.theme = isDark ? 'dark' : 'light';
  if (themeToggle) {
    themeToggle.setAttribute('aria-pressed', String(isDark));
    themeToggle.setAttribute('aria-label', `Switch to ${isDark ? 'light' : 'dark'} theme`);
    themeToggle.title = `Switch to ${isDark ? 'light' : 'dark'} theme`;
  }
  if (themeToggleLabel) themeToggleLabel.textContent = isDark ? 'Light mode' : 'Dark mode';
  if (themeToggleIcon) themeToggleIcon.textContent = isDark ? '☼' : '☾';
  if (themeColorMeta) themeColorMeta.content = isDark ? '#111b18' : '#f4f2e9';
  if (save) {
    try { window.localStorage.setItem('tenderlens-theme', isDark ? 'dark' : 'light'); } catch (error) { /* Theme still works for this page. */ }
  }
}

applyTheme(document.documentElement.dataset.theme === 'dark' ? 'dark' : 'light');
if (themeToggle) themeToggle.addEventListener('click', () => {
  applyTheme(document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark', true);
});

const liveSearchForm = document.getElementById('live-search-form');
const liveSearchInput = document.getElementById('live-search-query');
const liveSearchPortal = document.getElementById('live-search-portal');
const liveSearchStatus = document.getElementById('live-search-status');
const liveSearchResults = document.getElementById('live-search-results');
const liveSearchButton = liveSearchForm?.querySelector('button[type="submit"]');
const liveSearchButtonLabel = liveSearchForm?.querySelector('.live-search-button-label');
const configuredApiBase = document.querySelector('meta[name="tenderlens-api"]')?.content.trim();
const isLocalPreview = ['localhost', '127.0.0.1'].includes(window.location.hostname);
const apiBaseUrl = (configuredApiBase || (isLocalPreview ? 'http://127.0.0.1:8000' : '')).replace(/\/$/, '');

function showLiveSearchStatus(message, state = '') {
  if (!liveSearchStatus) return;
  liveSearchStatus.textContent = message;
  liveSearchStatus.dataset.state = state;
}

function makeLiveSearchResult(tender) {
  const card = document.createElement('article');
  card.className = 'live-result-card';

  const source = document.createElement('p');
  source.className = 'live-result-source';
  source.textContent = [tender.source_portal || 'Tender portal', tender.published_date].filter(Boolean).join(' · ');

  const title = document.createElement('h3');
  title.textContent = tender.title || 'Tender notice';

  const snippet = document.createElement('p');
  snippet.textContent = tender.snippet || 'Open the official notice to review its details.';

  card.append(source, title, snippet);
  if (tender.url) {
    try {
      const linkUrl = new URL(tender.url);
      if (linkUrl.protocol === 'https:' || linkUrl.protocol === 'http:') {
        const link = document.createElement('a');
        link.href = linkUrl.href;
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        link.textContent = 'Open official notice';
        card.append(link);
        const saveButton = document.createElement('button');
        saveButton.type = 'button';
        saveButton.className = 'live-save-button';
        saveButton.dataset.liveSave = JSON.stringify({
          title: tender.title || 'Tender notice',
          url: linkUrl.href,
          source_portal: tender.source_portal || 'Tender portal',
          snippet: tender.snippet || ''
        });
        saveButton.textContent = 'Save to account';
        const saveStatus = document.createElement('span');
        saveStatus.dataset.liveSaveStatus = '';
        saveStatus.className = 'live-save-status';
        saveStatus.setAttribute('role', 'status');
        saveStatus.setAttribute('aria-live', 'polite');
        card.append(saveButton, saveStatus);
      }
    } catch (error) { /* Ignore malformed result links. */ }
  }
  return card;
}

if (liveSearchForm) {
  liveSearchForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const keywords = liveSearchInput?.value.trim();
    if (!keywords) {
      liveSearchInput?.focus();
      return;
    }
    if (!apiBaseUrl) {
      showLiveSearchStatus('Live search is not connected on this website yet. Use the sample tenders or check the easy guide.', 'unavailable');
      return;
    }

    if (liveSearchButton) liveSearchButton.disabled = true;
    if (liveSearchButtonLabel) liveSearchButtonLabel.textContent = 'Searching…';
    liveSearchResults?.replaceChildren();
    showLiveSearchStatus('Connecting to the TenderLens service…', 'loading');

    try {
      const healthResponse = await fetch(`${apiBaseUrl}/healthz`, { headers: { Accept: 'application/json' } });
      if (!healthResponse.ok) throw new Error('service-unavailable');
      const health = await healthResponse.json();
      if (!health.tinyfish_configured) {
        showLiveSearchStatus('The service is running, but live search needs a TinyFish key. Follow the setup guide. Your search was not sent.', 'needs-key');
        return;
      }

      showLiveSearchStatus('Searching supported public tender portals…', 'loading');
      const searchResponse = await fetch(`${apiBaseUrl}/api/v1/tenders/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({ keywords, portal: liveSearchPortal?.value || null, limit: 8 })
      });
      if (!searchResponse.ok) throw new Error('search-failed');
      const tenders = await searchResponse.json();
      if (!Array.isArray(tenders) || !tenders.length) {
        showLiveSearchStatus('No notices came back for that search. Try broader words, or explore the sample tenders.', 'empty');
        return;
      }

      tenders.slice(0, 8).forEach((tender) => liveSearchResults?.append(makeLiveSearchResult(tender)));
      showLiveSearchStatus(`${Math.min(tenders.length, 8)} notice${tenders.length === 1 ? '' : 's'} found. Open each official notice and check its latest terms before acting.`, 'success');
    } catch (error) {
      showLiveSearchStatus('The live search service could not be reached. Start it using the easy guide. The sample explorer is still available.', 'unavailable');
    } finally {
      if (liveSearchButton) liveSearchButton.disabled = false;
      if (liveSearchButtonLabel) liveSearchButtonLabel.textContent = 'Search live tenders';
    }
  });
}

const printButton = document.querySelector('.print-report');
if (printButton) printButton.addEventListener('click', () => window.print());

const motionPreference = window.matchMedia('(prefers-reduced-motion: reduce)');
const lenis = window.Lenis && !motionPreference.matches
  ? new window.Lenis({ autoRaf: true, anchors: true, duration: 0.9 })
  : null;

const progressBar = document.getElementById('scroll-progress-bar');
const backToTop = document.getElementById('back-to-top');
const siteHeader = document.querySelector('.site-header');
const siteFooter = document.querySelector('.site-footer');

if (backToTop && siteFooter && 'IntersectionObserver' in window) {
  const footerObserver = new IntersectionObserver((entries) => {
    backToTop.classList.toggle('is-over-footer', entries.some((entry) => entry.isIntersecting));
  });
  footerObserver.observe(siteFooter);
}

function updateScrollChrome() {
  const scrollTop = lenis ? lenis.scroll : window.scrollY;
  const scrollableHeight = document.documentElement.scrollHeight - window.innerHeight;
  const progress = scrollableHeight > 0 ? Math.min(1, Math.max(0, scrollTop / scrollableHeight)) : 0;
  if (progressBar) progressBar.style.transform = `scaleX(${progress})`;
  if (siteHeader) siteHeader.classList.toggle('is-scrolled', scrollTop > 8);
  if (backToTop) {
    if (scrollTop > 700) backToTop.removeAttribute('hidden');
    backToTop.classList.toggle('is-visible', scrollTop > 700);
  }
}

const parallaxItems = Array.from(document.querySelectorAll('[data-parallax]'));
let parallaxFrame = 0;
function updateParallax() {
  if (!parallaxItems.length || motionPreference.matches || parallaxFrame) return;
  parallaxFrame = window.requestAnimationFrame(() => {
    parallaxItems.forEach((item) => {
      const speed = Math.max(-0.25, Math.min(0.25, Number(item.dataset.parallax) || 0.12));
      const rect = item.getBoundingClientRect();
      const offset = (rect.top + rect.height / 2 - window.innerHeight / 2) * speed;
      item.style.setProperty('--parallax-offset', `${Math.max(-72, Math.min(72, -offset))}px`);
    });
    parallaxFrame = 0;
  });
}

const handleScrollChrome = () => { updateScrollChrome(); updateParallax(); };
if (lenis) lenis.on('scroll', handleScrollChrome);
window.addEventListener('scroll', handleScrollChrome, { passive: true });
window.addEventListener('resize', updateScrollChrome, { passive: true });
updateScrollChrome();
updateParallax();

if (backToTop) {
  backToTop.addEventListener('click', () => {
    if (lenis) lenis.scrollTo(0, { duration: 0.85 });
    else window.scrollTo({ top: 0, behavior: motionPreference.matches ? 'instant' : 'smooth' });
  });
}

const revealItems = Array.from(document.querySelectorAll('[data-reveal]'));
if ('IntersectionObserver' in window && !motionPreference.matches && revealItems.length) {
  document.documentElement.classList.add('motion-ready');
  const revealObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('is-revealed');
      observer.unobserve(entry.target);
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -5% 0px' });
  revealItems.forEach((item) => revealObserver.observe(item));
}

const navLinks = Array.from(document.querySelectorAll('.primary-nav a[href^="#"]'));
if ('IntersectionObserver' in window && navLinks.length) {
  const navTargets = navLinks
    .map((link) => document.querySelector(link.getAttribute('href')))
    .filter(Boolean);
  const navObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      navLinks.forEach((link) => {
        const active = link.hash === `#${entry.target.id}`;
        if (active) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      });
    });
  }, { rootMargin: '-22% 0px -67% 0px', threshold: 0 });
  navTargets.forEach((target) => navObserver.observe(target));
}

const tenderSearch = document.getElementById('tender-search');
const tenderCards = Array.from(document.querySelectorAll('[data-tender-card]'));
const filterButtons = Array.from(document.querySelectorAll('[data-filter]'));
const resultCount = document.getElementById('tender-result-count');
const emptyState = document.getElementById('tender-empty');
let activeTenderFilter = 'all';

function filterTenders() {
  const query = tenderSearch ? tenderSearch.value.trim().toLowerCase() : '';
  let visibleCount = 0;
  tenderCards.forEach((card) => {
    const matchesFilter = activeTenderFilter === 'all' || card.dataset.category === activeTenderFilter;
    const matchesQuery = !query || `${card.dataset.search} ${card.textContent}`.toLowerCase().includes(query);
    const visible = matchesFilter && matchesQuery;
    card.hidden = !visible;
    if (visible) visibleCount += 1;
  });
  if (resultCount) resultCount.textContent = `${visibleCount} ${visibleCount === 1 ? 'example' : 'examples'} shown`;
  if (emptyState) emptyState.hidden = visibleCount !== 0;
}

filterButtons.forEach((button) => {
  button.addEventListener('click', () => {
    activeTenderFilter = button.dataset.filter;
    filterButtons.forEach((item) => {
      const selected = item === button;
      item.classList.toggle('is-active', selected);
      item.setAttribute('aria-pressed', String(selected));
    });
    filterTenders();
  });
});

if (tenderSearch) tenderSearch.addEventListener('input', filterTenders);
document.addEventListener('keydown', (event) => {
  const target = event.target;
  const isTyping = target instanceof HTMLElement && (target.isContentEditable || ['INPUT', 'TEXTAREA', 'SELECT'].includes(target.tagName));
  if (event.key === '/' && !isTyping && tenderSearch) {
    event.preventDefault();
    tenderSearch.focus();
  }
  if (event.key === 'Escape' && tenderSearch && document.activeElement === tenderSearch) {
    tenderSearch.value = '';
    filterTenders();
    tenderSearch.blur();
  }
});

const saveButtons = Array.from(document.querySelectorAll('[data-save-tender]'));
const savedCount = document.getElementById('saved-count');
const saveStatus = document.getElementById('save-status');
function updateSavedCount() {
  const count = saveButtons.filter((button) => button.getAttribute('aria-pressed') === 'true').length;
  if (savedCount) savedCount.textContent = String(count);
}

saveButtons.forEach((button) => {
  button.addEventListener('click', () => {
    const saved = button.getAttribute('aria-pressed') !== 'true';
    const baseLabel = button.dataset.saveLabel || button.getAttribute('aria-label');
    button.dataset.saveLabel = baseLabel;
    button.setAttribute('aria-pressed', String(saved));
    button.setAttribute('aria-label', saved ? baseLabel.replace(/^Save /, 'Remove ').replace(/ sample$/, ' sample from saved examples') : baseLabel);
    button.textContent = saved ? '★' : '☆';
    if (saveStatus) saveStatus.textContent = saved ? 'Sample saved for this visit.' : 'Sample removed from this visit.';
    updateSavedCount();
  });
});

const tenderExamples = {
  switchgear: {
    kicker: 'GEM · ELECTRICAL GOODS',
    title: 'Supply of industrial switchgear',
    buyer: 'Sample buyer · Haryana · fictional example',
    value: '₹48 lakh · example value',
    window: '12 days · example timeline',
    prompts: ['Compare the latest update with the original sales and exemption rules.', 'Find certificate requirements in the buyer’s extra terms.']
  },
  solar: {
    kicker: 'CPPP · RENEWABLE ENERGY WORKS',
    title: 'Solar rooftop EPC package',
    buyer: 'Sample municipal authority · Jaipur · fictional example',
    value: '₹1.8 crore · example value',
    window: '8 days · example timeline',
    prompts: ['Compare similar-work rules with the company’s project history.', 'Check local-content and deposit rules across the tender files.', 'See whether later notices changed the delivery work.']
  },
  security: {
    kicker: 'PSU · IT SERVICES',
    title: 'Endpoint security subscription',
    buyer: 'Sample public sector buyer · Delhi · fictional example',
    value: '₹26 lakh · example value',
    window: '19 days · example timeline',
    prompts: ['Find required manufacturer letters and product certificates.', 'Review support, setup conditions and service levels.', 'Check what extra rules the buyer added to the main bid.']
  }
};

const tenderDialog = document.getElementById('tender-dialog');
const dialogTitle = document.getElementById('tender-dialog-title');
const dialogKicker = document.getElementById('tender-dialog-kicker');
const dialogBuyer = document.getElementById('tender-dialog-buyer');
const dialogFacts = document.getElementById('tender-dialog-facts');
const dialogPrompts = document.getElementById('tender-dialog-prompts');
let previewTrigger = null;

function openTenderPreview(key, trigger) {
  const example = tenderExamples[key];
  if (!example || !tenderDialog) return;
  previewTrigger = trigger;
  dialogTitle.textContent = example.title;
  dialogKicker.textContent = example.kicker;
  dialogBuyer.textContent = example.buyer;
  dialogFacts.replaceChildren();
  [
    ['EXAMPLE VALUE', example.value],
    ['EXAMPLE WINDOW', example.window]
  ].forEach(([label, value]) => {
    const fact = document.createElement('div');
    fact.className = 'dialog-fact';
    const factLabel = document.createElement('small');
    factLabel.textContent = label;
    const factValue = document.createElement('strong');
    factValue.textContent = value;
    fact.append(factLabel, factValue);
    dialogFacts.append(fact);
  });
  dialogPrompts.replaceChildren(...example.prompts.map((prompt) => {
    const item = document.createElement('li');
    item.textContent = prompt;
    return item;
  }));
  if (typeof tenderDialog.showModal === 'function') tenderDialog.showModal();
  else tenderDialog.setAttribute('open', '');
}

document.querySelectorAll('[data-preview-tender]').forEach((button) => {
  button.addEventListener('click', () => openTenderPreview(button.dataset.previewTender, button));
});

const dialogClose = document.querySelector('.dialog-close');
if (dialogClose && tenderDialog) dialogClose.addEventListener('click', () => tenderDialog.close());
if (tenderDialog) {
  tenderDialog.addEventListener('click', (event) => {
    if (event.target === tenderDialog) tenderDialog.close();
  });
  tenderDialog.addEventListener('close', () => {
    if (previewTrigger) previewTrigger.focus();
  });
}

const dialogReportLink = document.getElementById('dialog-report-link');
if (dialogReportLink && tenderDialog) dialogReportLink.addEventListener('click', () => tenderDialog.close());

const precedenceContent = {
  latest: {
    rank: 'FILE 1 OF 5 · NEWEST',
    title: 'Latest official update',
    description: 'The newest official notice may change a tender requirement. Check its date and compare the new wording with earlier files.',
    cue: 'Keep both the new wording and the earlier source in the review notes.'
  },
  prior: {
    rank: 'FILE 2 OF 5 · OLDER UPDATE',
    title: 'Earlier official updates',
    description: 'Older notices help explain how a rule changed. A newer notice may replace part of an earlier one.',
    cue: 'Compare dates and wording so the change is clear.'
  },
  uploaded: {
    rank: 'FILE 3 OF 5 · BUYER FILE',
    title: 'Buyer’s extra file',
    description: 'The buyer may link another file with extra experience, certificate, product or service rules.',
    cue: 'Open the file and note the page and section for each requirement.'
  },
  text: {
    rank: 'FILE 4 OF 5 · EXTRA TERMS',
    title: 'Extra terms inside the bid',
    description: 'The main file can include extra buyer rules. These can add to or change the basic tender requirements.',
    cue: 'If two rules disagree, ask a reviewer to check the original documents.'
  },
  main: {
    rank: 'FILE 5 OF 5 · MAIN FILE',
    title: 'Main tender document',
    description: 'The main tender sets the starting rules, deadlines, deposit and standard requirements.',
    cue: 'Keep it nearby so you can see what later files changed.'
  }
};

const precedenceButtons = Array.from(document.querySelectorAll('[data-layer]'));
precedenceButtons.forEach((button) => {
  button.addEventListener('click', () => {
    const content = precedenceContent[button.dataset.layer];
    if (!content) return;
    precedenceButtons.forEach((item) => {
      const selected = item === button;
      item.classList.toggle('is-active', selected);
      item.setAttribute('aria-pressed', String(selected));
    });
    document.getElementById('precedence-rank').textContent = content.rank;
    document.getElementById('precedence-title').textContent = content.title;
    document.getElementById('precedence-description').textContent = content.description;
    document.getElementById('precedence-cue').textContent = content.cue;
  });
});

const profileItems = Array.from(document.querySelectorAll('[data-profile-item]'));
const profileProgress = document.getElementById('profile-progress');
const profileCount = document.getElementById('profile-count');
const profilePercent = document.getElementById('profile-percent');
const profileBadge = document.getElementById('profile-badge');
const profileGuidance = document.getElementById('profile-guidance');

function updateProfileReadiness() {
  const count = profileItems.filter((item) => item.checked).length;
  const percent = Math.round((count / Math.max(profileItems.length, 1)) * 100);
  if (profileProgress) profileProgress.value = count;
  if (profileProgress) profileProgress.setAttribute('aria-valuenow', String(count));
  if (profileCount) profileCount.textContent = String(count);
  if (profilePercent) profilePercent.textContent = `${percent}%`;
  if (profileBadge) {
    profileBadge.textContent = count === profileItems.length ? 'DEMO CHECKLIST READY' : 'IN PROGRESS';
    profileBadge.classList.toggle('is-complete', count === profileItems.length);
  }
  profileItems.forEach((item) => {
    const row = item.closest('.profile-check');
    if (!row) return;
    row.classList.toggle('is-checked', item.checked);
    const state = row.querySelector('.check-state');
    if (state) state.textContent = item.checked ? 'READY' : 'ADD';
  });
  if (profileGuidance) {
    const remaining = profileItems.length - count;
    profileGuidance.textContent = remaining === 0
      ? 'All six evidence groups are staged in this demo. A complete checklist does not establish eligibility.'
      : `${count} of 6 evidence groups staged. ${remaining} ${remaining === 1 ? 'group remains' : 'groups remain'} in this demo. This is not an eligibility score.`;
  }
}

profileItems.forEach((item) => item.addEventListener('change', updateProfileReadiness));
const resetProfile = document.getElementById('reset-profile');
if (resetProfile) {
  resetProfile.addEventListener('click', () => {
    profileItems.forEach((item, index) => { item.checked = index < 3; });
    updateProfileReadiness();
    profileItems[0]?.focus();
  });
}
updateProfileReadiness();

const bidderProfileForm = document.getElementById('bidder-profile-form');
if (bidderProfileForm) {
  const bidderProfileKey = 'tenderlens-bidder-profile-v1';
  const bidderProfileFields = {
    organization: document.getElementById('bidder-profile-name'),
    bidderType: document.getElementById('bidder-profile-type'),
    years: document.getElementById('bidder-profile-years'),
    region: document.getElementById('bidder-profile-region')
  };
  const bidderProfileStatus = document.getElementById('profile-save-status');
  const saveBidderProfile = document.getElementById('save-bidder-profile');
  const clearBidderProfile = document.getElementById('clear-bidder-profile');
  const setBidderProfileStatus = (message, state = '') => {
    if (!bidderProfileStatus) return;
    bidderProfileStatus.textContent = message;
    if (state) bidderProfileStatus.dataset.state = state;
    else delete bidderProfileStatus.dataset.state;
  };

  try {
    const savedProfile = JSON.parse(window.localStorage.getItem(bidderProfileKey) || 'null');
    if (savedProfile && typeof savedProfile === 'object' && !Array.isArray(savedProfile)) {
      Object.entries(bidderProfileFields).forEach(([key, field]) => {
        if (field && typeof savedProfile[key] === 'string') field.value = savedProfile[key];
      });
      setBidderProfileStatus('Your profile is saved in this browser on this device. It is not sent with searches.', 'success');
    }
  } catch (error) {
    setBidderProfileStatus('Browser storage is unavailable. The form still works for this visit, but it cannot save a profile.', 'error');
  }

  const saveLocalBidderProfile = async () => {
    const profile = Object.fromEntries(Object.entries(bidderProfileFields).map(([key, field]) => [key, field?.value.trim() || '']));
    if (!profile.organization) {
      setBidderProfileStatus('Enter an organization name to save this profile.', 'error');
      bidderProfileFields.organization?.focus();
      return;
    }
    try {
      window.localStorage.setItem(bidderProfileKey, JSON.stringify(profile));
      setBidderProfileStatus('Profile saved in this browser on this device. It is not sent with searches.', 'success');
      const account = window.TenderLensAuth;
      if (account) {
        await account.ready;
        if (account.user) {
          setBidderProfileStatus('Saving your profile to your account…', 'loading');
          const { error } = await account.saveProfile({
            organization: profile.organization,
            bidder_type: profile.bidderType,
            years_active: profile.years,
            region: profile.region
          });
          setBidderProfileStatus(error
            ? `Saved on this device. Account sync failed: ${account.profileErrorMessage(error)}`
            : 'Profile saved to your account and available on your other devices.', error ? 'error' : 'success');
          const label = document.querySelector('.profile-storage-label');
          if (!error && label) label.textContent = 'ACCOUNT SYNC';
        }
      }
    } catch (error) {
      setBidderProfileStatus('Could not save in this browser. Check your storage settings and try again.', 'error');
    }
  };

  saveBidderProfile?.addEventListener('click', saveLocalBidderProfile);
  bidderProfileForm.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' && event.target instanceof HTMLInputElement) {
      event.preventDefault();
      saveLocalBidderProfile();
    }
  });

  if (clearBidderProfile) {
    clearBidderProfile.addEventListener('click', () => {
      try {
        window.localStorage.removeItem(bidderProfileKey);
        Object.values(bidderProfileFields).forEach((field) => { if (field) field.value = ''; });
        setBidderProfileStatus('Local profile cleared from this browser.', 'success');
      } catch (error) {
        setBidderProfileStatus('Could not clear browser storage. Remove this site’s saved data in your browser settings.', 'error');
      }
    });
  }
}

// Floating Navigation Drawer Handler
(() => {
  const menuToggle = document.getElementById('floating-menu-toggle');
  const navDrawer = document.getElementById('floating-nav-drawer');
  const drawerClose = document.getElementById('drawer-close-btn');
  const drawerBackdrop = document.getElementById('drawer-backdrop');

  if (menuToggle && navDrawer) {
    const openDrawer = () => {
      navDrawer.classList.add('is-open');
      navDrawer.setAttribute('aria-hidden', 'false');
      menuToggle.setAttribute('aria-expanded', 'true');
      document.body.style.overflow = 'hidden';
    };

    const closeDrawer = () => {
      navDrawer.classList.remove('is-open');
      navDrawer.setAttribute('aria-hidden', 'true');
      menuToggle.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
    };

    menuToggle.addEventListener('click', () => {
      const isOpen = navDrawer.classList.contains('is-open');
      if (isOpen) closeDrawer();
      else openDrawer();
    });

    if (drawerClose) drawerClose.addEventListener('click', closeDrawer);
    if (drawerBackdrop) drawerBackdrop.addEventListener('click', closeDrawer);

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && navDrawer.classList.contains('is-open')) {
        closeDrawer();
      }
    });

    navDrawer.querySelectorAll('.drawer-nav-item').forEach((item) => {
      item.addEventListener('click', closeDrawer);
    });
  }
})();

