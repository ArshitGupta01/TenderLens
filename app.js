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
    description: 'The main bid provides the initial thresholds, EMD and timelines. TenderLens checks it alongside linked terms and later amendments.'
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
    description: 'Check whether MSME exemptions apply, whether the right certificates are on file, and which conditions need a closer read.',
    focus: 'Turnover · exemptions · certifications'
  },
  epc: {
    index: 'PROFILE / 02',
    type: 'EPC CONTRACTORS',
    title: 'Put project history against the clause.',
    description: 'Review similar-work definitions, contract value bands and past-project evidence across the tender set.',
    focus: 'Experience · project value · scope'
  },
  it: {
    index: 'PROFILE / 03',
    type: 'IT SYSTEM INTEGRATORS',
    title: 'Surface the technical gates early.',
    description: 'Bring OEM authorizations, certification requirements and deployment conditions into the same qualification view.',
    focus: 'OEM letters · certificates · capability'
  },
  consultants: {
    index: 'PROFILE / 04',
    type: 'BID CONSULTANTS',
    title: 'Make each client review traceable.',
    description: 'Compare opportunities against a bidder profile and keep the clause references beside the recommendation.',
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
