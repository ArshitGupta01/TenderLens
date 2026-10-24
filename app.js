const evidence = {
  turnover: {
    source: 'BIDDER PROFILE / FINANCIAL CAPACITY',
    title: 'The sample profile clears this threshold.',
    description: 'In this illustrative case, the bidder profile contains a three-year average above the requirement extracted from the tender set. A deterministic comparison marks the check as met.'
  },
  certification: {
    source: 'BUYER-ADDED ATC / PAGE 18 / CLAUSE 7.2',
    title: 'No matching certificate appears in the sample profile.',
    description: 'The sample ATC asks for ISO 9001 evidence. TenderLens links the requirement to the bidder profile so a reviewer can confirm whether a valid certificate should be added.'
  },
  exemption: {
    source: 'CORRIGENDUM 02 / PAGE 3 / AMENDED CONDITION',
    title: 'The amendment changes the earlier exemption language.',
    description: 'This simulated source relationship routes the MSME exemption to human review. The earlier clause stays in the audit trail while the latest wording is checked.'
  },
  corrigendum: {
    source: 'CORRIGENDUM 02 / LATEST AMENDMENT',
    title: 'Latest terms in the illustrative document set.',
    description: 'A corrigendum can supersede an earlier bid or ATC clause. This sample marks the latest amendment as current while keeping the replaced language available for review.'
  },
  atc: {
    source: 'BUYER-ADDED ATC / 24 PAGES',
    title: 'Specific eligibility terms from the buyer.',
    description: 'The buyer-added terms may contain experience, certification, OEM authorization or local service requirements. A later corrigendum can override part of this document.'
  },
  main: {
    source: 'MAIN BID DOCUMENT / 42 PAGES',
    title: 'Baseline requirements for the opportunity.',
    description: 'The main bid provides baseline thresholds, EMD and timelines. The proposed workflow would compare it with linked terms and later amendments.'
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

const printButton = document.querySelector('.print-report');
if (printButton) printButton.addEventListener('click', () => window.print());

const motionPreference = window.matchMedia('(prefers-reduced-motion: reduce)');
const lenis = window.Lenis && !motionPreference.matches
  ? new window.Lenis({ autoRaf: true, anchors: true, duration: 0.9 })
  : null;

const progressBar = document.getElementById('scroll-progress-bar');
const backToTop = document.getElementById('back-to-top');
const siteHeader = document.querySelector('.site-header');

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

if (lenis) lenis.on('scroll', updateScrollChrome);
window.addEventListener('scroll', updateScrollChrome, { passive: true });
window.addEventListener('resize', updateScrollChrome, { passive: true });
updateScrollChrome();

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
    prompts: ['Check the latest amendment against the original turnover and exemption language.', 'Locate certification requirements in the buyer-added ATC.']
  },
  solar: {
    kicker: 'CPPP · RENEWABLE ENERGY WORKS',
    title: 'Solar rooftop EPC package',
    buyer: 'Sample municipal authority · Jaipur · fictional example',
    value: '₹1.8 crore · example value',
    window: '8 days · example timeline',
    prompts: ['Compare similar-work definitions with the bidder’s project references.', 'Check local-content and EMD terms across the tender set.', 'Review whether later notices changed the delivery scope.']
  },
  security: {
    kicker: 'PSU · IT SERVICES',
    title: 'Endpoint security subscription',
    buyer: 'Sample public sector buyer · Delhi · fictional example',
    value: '₹26 lakh · example value',
    window: '19 days · example timeline',
    prompts: ['Find mandatory OEM authorization and product certifications.', 'Review support coverage, deployment conditions and service levels.', 'Check whether the ATC adds terms beyond the main bid.']
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
    rank: 'RANK 01 / HIGHEST',
    title: 'Latest corrigendum',
    description: 'The most recent corrigendum can supersede earlier terms in the tender set. Its publication and clause references should remain attached to the changed requirement.',
    cue: 'Compare changed thresholds with prior language and retain both sources in the audit trail.'
  },
  prior: {
    rank: 'RANK 02 / PRIOR AMENDMENTS',
    title: 'Earlier corrigenda',
    description: 'Earlier amendments remain part of the history. A later corrigendum may revise them, so the sequence and publication dates matter.',
    cue: 'Keep each version visible and check whether a newer notice replaced the clause.'
  },
  uploaded: {
    rank: 'RANK 03 / BUYER DOCUMENT',
    title: 'Uploaded ATC or RFP',
    description: 'A linked buyer document may add specific technical, experience, certification or OEM requirements beyond the standard bid template.',
    cue: 'Follow the link, identify the exact page and clause, and check for later amendments or governing terms.'
  },
  text: {
    rank: 'RANK 04 / EMBEDDED ATC',
    title: 'Text-based buyer ATC',
    description: 'Buyer-added clauses inside the main bid can change baseline parameters. The project model checks them alongside uploaded terms and corrigenda.',
    cue: 'Compare overlapping clauses and surface same-rank or legal conflicts for human review.'
  },
  main: {
    rank: 'RANK 05 / BASELINE',
    title: 'Main tender document',
    description: 'The main bid provides the baseline thresholds, EMD, timelines and standard terms when higher-priority documents do not amend them.',
    cue: 'Keep baseline language available so reviewers can see what later documents changed.'
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
