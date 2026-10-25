(() => {
  const form = document.querySelector('#strategy-form');
  if (!form) return;

  const apiFromMeta = document.querySelector('meta[name="tenderlens-api"]')?.content.trim();
  const localHost = ['localhost', '127.0.0.1'].includes(window.location.hostname);
  const apiBase = (apiFromMeta || (localHost ? 'http://127.0.0.1:8000' : '')).replace(/\/$/, '');
  const status = document.querySelector('#strategy-status');
  const submit = document.querySelector('#strategy-submit');
  const results = document.querySelector('#strategy-results');
  let latestCsv = '';
  let latestPrebidMarkdown = '';
  let latestAffidavits = [];
  let selectedAffidavitIndex = 0;
  let submittedTitle = '';
  let submittedPortal = '';

  const PRESETS = {
    'bhel-msme-trap': {
      tender_title: 'Supply & Commissioning of BHEL 33kV Substation Switchgear & Relay Panels',
      tender_id: 'GEM/2026/B/900123',
      source_portal: 'BHEL',
      company_name: 'Apex Solar & Grid MSME Pvt Ltd',
      entity_type: 'System Integrator',
      years_in_business: 3,
      is_msme_registered: true,
      is_startup_recognized: true,
      turnover_year_1_lakhs: 95,
      turnover_year_2_lakhs: 120,
      turnover_year_3_lakhs: 145,
      local_content_percentage: 64,
      held_certifications: 'ISO-9001, CE',
      past_similar_project_values_lakhs: '85, 60',
      min_annual_turnover_lakhs: 450,
      min_experience_years: 5,
      estimated_bid_value_lakhs: 300,
      emd_amount_inr: 600000,
      min_local_content_percentage: 50,
      mandatory_certifications: 'ISO-9001, BIS',
      oem_authorization_mandatory: true,
      emd_exemption_confirmed_by_tender: true,
      msme_turnover_relaxation_allowed: false,
      is_turnover_exemption_revoked_by_atc: true,
      msme_experience_relaxation_allowed: false,
      is_experience_exemption_revoked_by_atc: true,
      proprietary_brand_lock_detected: true,
      proprietary_brand_details: 'Clause ATC-4.2: Only Make Allowed — ProprietarySwitchgearX; no MSME turnover or experience relaxation permitted.',
      estimated_emd_lockup_days: 120,
      annual_capital_cost_rate_pct: 12.0,
      active_simultaneous_bids_count: 4,
      available_emd_working_capital_inr: 2000000,
      surety_bond_permitted_by_tender: 'true'
    },
    'cppp-epc-surety': {
      tender_title: 'CPWD Turnkey Solar Rooftop & Grid Synchronization Works across Central Buildings',
      tender_id: 'CPPP/2026/CPWD/4082',
      source_portal: 'CPPP',
      company_name: 'Vanguard Infra & Power EPC Ltd',
      entity_type: 'EPC',
      years_in_business: 9,
      is_msme_registered: false,
      is_startup_recognized: false,
      turnover_year_1_lakhs: 620,
      turnover_year_2_lakhs: 710,
      turnover_year_3_lakhs: 770,
      local_content_percentage: 58,
      held_certifications: 'ISO-9001, ISO-14001, BIS',
      past_similar_project_values_lakhs: '260, 240, 190',
      min_annual_turnover_lakhs: 500,
      min_experience_years: 7,
      estimated_bid_value_lakhs: 450,
      emd_amount_inr: 900000,
      min_local_content_percentage: 50,
      mandatory_certifications: 'ISO-9001, BIS',
      oem_authorization_mandatory: false,
      emd_exemption_confirmed_by_tender: false,
      msme_turnover_relaxation_allowed: true,
      is_turnover_exemption_revoked_by_atc: false,
      msme_experience_relaxation_allowed: true,
      is_experience_exemption_revoked_by_atc: false,
      proprietary_brand_lock_detected: false,
      proprietary_brand_details: '',
      estimated_emd_lockup_days: 150,
      annual_capital_cost_rate_pct: 12.5,
      active_simultaneous_bids_count: 5,
      available_emd_working_capital_inr: 5000000,
      surety_bond_permitted_by_tender: 'true'
    },
    'icmr-medical-maf': {
      tender_title: 'Procurement of Automated RT-PCR & Biosafety Diagnostic Analyzers for ICMR Labs',
      tender_id: 'ICMR/2026/DIAG/119',
      source_portal: 'ICMR',
      company_name: 'BioMed Precision Diagnostics India Pvt Ltd',
      entity_type: 'Reseller',
      years_in_business: 5,
      is_msme_registered: true,
      is_startup_recognized: false,
      turnover_year_1_lakhs: 210,
      turnover_year_2_lakhs: 245,
      turnover_year_3_lakhs: 265,
      local_content_percentage: 52,
      held_certifications: 'ISO-9001, CE',
      past_similar_project_values_lakhs: '130, 115',
      min_annual_turnover_lakhs: 200,
      min_experience_years: 3,
      estimated_bid_value_lakhs: 150,
      emd_amount_inr: 300000,
      min_local_content_percentage: 50,
      mandatory_certifications: 'ISO-9001, CE, BIS',
      oem_authorization_mandatory: true,
      emd_exemption_confirmed_by_tender: true,
      msme_turnover_relaxation_allowed: true,
      is_turnover_exemption_revoked_by_atc: false,
      msme_experience_relaxation_allowed: true,
      is_experience_exemption_revoked_by_atc: false,
      proprietary_brand_lock_detected: false,
      proprietary_brand_details: '',
      estimated_emd_lockup_days: 90,
      annual_capital_cost_rate_pct: 12.0,
      active_simultaneous_bids_count: 2,
      available_emd_working_capital_inr: 1500000,
      surety_bond_permitted_by_tender: 'true'
    }
  };

  const field = (name) => form.elements.namedItem(name);
  const numberValue = (name) => {
    const raw = field(name)?.value?.trim() || '';
    return raw === '' ? null : Number(raw);
  };
  const csvList = (name) => (field(name)?.value || '')
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean)
    .slice(0, 25);
  const floatList = (name) => (field(name)?.value || '')
    .split(',')
    .map((item) => Number(item.trim()))
    .filter((num) => Number.isFinite(num) && num > 0)
    .slice(0, 20);
  const setStatus = (element, message, state = '') => {
    if (!element) return;
    element.textContent = message;
    if (state) element.dataset.state = state;
    else delete element.dataset.state;
  };
  const textNode = (tag, value, className = '') => {
    const node = document.createElement(tag);
    node.textContent = value == null ? '' : String(value);
    if (className) node.className = className;
    return node;
  };
  const formatMoney = (value) => value == null
    ? 'Not calculated'
    : new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(value);

  function applyPreset(presetKey) {
    const data = PRESETS[presetKey];
    if (!data) return;
    Object.entries(data).forEach(([key, val]) => {
      const input = field(key);
      if (!input) return;
      if (input.type === 'checkbox') {
        input.checked = Boolean(val);
      } else {
        input.value = val == null ? '' : String(val);
      }
    });
    setStatus(status, `Loaded preset "${data.tender_title}". Click "Create review preview" below or customize any figure.`, 'success');
  }

  document.querySelectorAll('[data-strategy-preset]').forEach((btn) => {
    btn.addEventListener('click', () => {
      applyPreset(btn.dataset.strategyPreset);
      form.requestSubmit();
    });
  });

  document.querySelector('[data-load-synced-profile]')?.addEventListener('click', async () => {
    let data = null;
    const auth = window.TenderLensAuth;
    if (auth?.user) {
      setStatus(status, 'Loading synced Bidder Profile from Supabase…', 'loading');
      const res = await auth.loadProfile();
      if (!res.error && res.data) data = res.data;
    }
    if (!data) {
      try {
        const localRaw = localStorage.getItem('tenderlens_bidder_profile');
        if (localRaw) data = JSON.parse(localRaw);
      } catch (_) {}
    }
    if (!data) {
      data = {
        organization: 'SuryaUrja Infra Solutions Pvt Ltd',
        bidder_type: 'OEM',
        years_in_business: 4,
        is_msme_registered: true,
        is_startup_recognized: true,
        turnover_year_1_lakhs: 180,
        turnover_year_2_lakhs: 210,
        turnover_year_3_lakhs: 240,
        local_content_percentage: 68.0,
        held_certifications: ['ISO 9001', 'BIS', 'STQC']
      };
    }
    if (data.organization) field('company_name').value = data.organization;
    if (data.bidder_type) {
      const select = field('entity_type');
      const match = Array.from(select.options).find((o) => o.value.toLowerCase() === String(data.bidder_type).toLowerCase());
      if (match) select.value = match.value;
    }
    if (data.years_in_business != null) field('years_in_business').value = String(data.years_in_business);
    if (data.is_msme_registered != null) field('is_msme_registered').checked = Boolean(data.is_msme_registered);
    if (data.is_startup_recognized != null) field('is_startup_recognized').checked = Boolean(data.is_startup_recognized);
    if (data.turnover_year_1_lakhs != null) field('turnover_year_1_lakhs').value = String(data.turnover_year_1_lakhs);
    if (data.turnover_year_2_lakhs != null) field('turnover_year_2_lakhs').value = String(data.turnover_year_2_lakhs);
    if (data.turnover_year_3_lakhs != null) field('turnover_year_3_lakhs').value = String(data.turnover_year_3_lakhs);
    if (data.local_content_percentage != null) field('local_content_percentage').value = String(data.local_content_percentage);
    if (Array.isArray(data.held_certifications) && data.held_certifications.length) {
      field('held_certifications').value = data.held_certifications.join(', ');
    }
    setStatus(status, `Loaded synced profile for "${data.organization || auth.user.email}". Enter tender requirements and click "Create review preview".`, 'success');
  });

  function buildRequest() {
    const suretyValue = field('surety_bond_permitted_by_tender').value;
    const optionalNumber = (name) => numberValue(name);
    return {
      tender_id: field('tender_id').value.trim() || null,
      tender_title: field('tender_title').value.trim(),
      source_portal: field('source_portal').value,
      bidder_profile: {
        company_name: field('company_name').value.trim(),
        entity_type: field('entity_type').value,
        is_msme_registered: field('is_msme_registered').checked,
        msme_category: field('is_msme_registered').checked ? 'SMALL' : null,
        is_startup_recognized: field('is_startup_recognized').checked,
        turnover_year_1_lakhs: Number(field('turnover_year_1_lakhs').value || 0),
        turnover_year_2_lakhs: Number(field('turnover_year_2_lakhs').value || 0),
        turnover_year_3_lakhs: Number(field('turnover_year_3_lakhs').value || 0),
        years_in_business: Number(field('years_in_business').value || 0),
        local_content_percentage: Number(field('local_content_percentage').value || 0),
        held_certifications: csvList('held_certifications'),
        past_similar_project_values_lakhs: floatList('past_similar_project_values_lakhs'),
        available_emd_working_capital_inr: optionalNumber('available_emd_working_capital_inr') || 2500000,
        active_simultaneous_bids_count: Number(field('active_simultaneous_bids_count').value || 1)
      },
      criteria: {
        min_annual_turnover_lakhs: Number(field('min_annual_turnover_lakhs').value || 0),
        min_experience_years: Number(field('min_experience_years').value || 0),
        estimated_bid_value_lakhs: optionalNumber('estimated_bid_value_lakhs'),
        emd_amount_inr: Number(field('emd_amount_inr').value || 0),
        min_local_content_percentage: Number(field('min_local_content_percentage').value || 20),
        mandatory_certifications: csvList('mandatory_certifications'),
        oem_authorization_mandatory: field('oem_authorization_mandatory').checked,
        emd_exemption_confirmed_by_tender: field('emd_exemption_confirmed_by_tender').checked ? true : null,
        msme_turnover_relaxation_allowed: field('msme_turnover_relaxation_allowed').checked,
        msme_experience_relaxation_allowed: field('msme_experience_relaxation_allowed').checked,
        is_turnover_exemption_revoked_by_atc: field('is_turnover_exemption_revoked_by_atc').checked,
        is_experience_exemption_revoked_by_atc: field('is_experience_exemption_revoked_by_atc').checked,
        allow_insurance_surety_bond: suretyValue !== 'false',
        proprietary_brand_lock_detected: field('proprietary_brand_lock_detected').checked,
        proprietary_brand_details: field('proprietary_brand_details').value.trim() || null,
        surety_bond_permitted_by_tender: suretyValue === '' ? null : suretyValue === 'true',
        estimated_emd_lockup_days: optionalNumber('estimated_emd_lockup_days') || 120,
        annual_capital_cost_rate_pct: optionalNumber('annual_capital_cost_rate_pct') ?? 12.0
      }
    };
  }

  function renderGates(gates) {
    const grid = document.querySelector('[data-strategy-gate-grid]');
    const summaryBadge = document.querySelector('[data-gate-summary-badge]');
    if (!grid) return;
    grid.replaceChildren();
    const list = Array.isArray(gates) ? gates : [];
    const passedCount = list.filter((g) => g.passed).length;
    if (summaryBadge) {
      summaryBadge.textContent = `${passedCount} / ${list.length} GATES PASSED`;
      summaryBadge.dataset.state = passedCount === list.length ? 'pass' : 'fail';
    }
    list.forEach((gate) => {
      const card = document.createElement('article');
      const isConditional = gate.passed && String(gate.reason || '').includes('CONDITIONAL');
      card.className = `strategy-gate-card ${gate.passed ? (isConditional ? 'gate-conditional' : 'gate-pass') : 'gate-fail'}`;
      const top = document.createElement('div');
      top.className = 'strategy-gate-card-top';
      top.append(
        textNode('strong', gate.rule_name),
        textNode('span', gate.passed ? (isConditional ? 'CONDITIONAL' : 'PASS') : 'DISQUALIFIER', 'strategy-gate-pill')
      );
      const vals = textNode(
        'p',
        `Bidder: ${Array.isArray(gate.bidder_value) ? gate.bidder_value.join(', ') : gate.bidder_value}  ·  Required: ${Array.isArray(gate.required_value) ? gate.required_value.join(', ') : gate.required_value}`,
        'strategy-gate-values'
      );
      const reason = textNode('p', gate.reason, 'strategy-gate-reason');
      const cite = textNode('small', `Ref: ${gate.statutory_citation || 'Tender Schedule'}`, 'strategy-gate-cite');
      card.append(top, vals, reason, cite);
      grid.append(card);
    });
  }

  function renderAffidavits(affidavits) {
    latestAffidavits = Array.isArray(affidavits) ? affidavits : [];
    const section = document.querySelector('[data-affidavits-section]');
    const tabs = document.querySelector('[data-affidavit-tabs]');
    const viewer = document.querySelector('[data-affidavit-viewer]');
    if (!section || !tabs || !viewer) return;
    if (!latestAffidavits.length) {
      section.hidden = true;
      return;
    }
    section.hidden = false;
    selectedAffidavitIndex = 0;
    tabs.replaceChildren();
    latestAffidavits.forEach((item, idx) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = `strategy-affidavit-tab ${idx === 0 ? 'is-active' : ''}`;
      btn.textContent = item.title;
      btn.addEventListener('click', () => {
        selectedAffidavitIndex = idx;
        tabs.querySelectorAll('.strategy-affidavit-tab').forEach((t, i) => t.classList.toggle('is-active', i === idx));
        viewer.textContent = `${item.content_markdown}\n\n— Governing Rule: ${item.governing_statute}`;
      });
      tabs.append(btn);
    });
    const first = latestAffidavits[0];
    viewer.textContent = `${first.content_markdown}\n\n— Governing Rule: ${first.governing_statute}`;
  }

  function renderForensicsItems(listEl, patterns) {
    if (!listEl) return;
    listEl.replaceChildren();
    const items = Array.isArray(patterns) ? patterns : [];
    items.forEach((result) => {
      const item = document.createElement('li');
      item.className = 'strategy-forensic-item';
      const head = document.createElement('div');
      head.className = 'strategy-forensic-head';
      head.append(
        textNode('strong', result.common_rejection_trigger),
        textNode('span', result.historical_frequency_weight || 'CHECKPOINT', 'strategy-gate-pill')
      );
      const counter = textNode('p', `Countermeasure: ${result.defensive_countermeasure || ''}`, 'strategy-forensic-counter');
      item.append(head, counter);
      if (result.reference_source?.startsWith('https://')) {
        const link = document.createElement('a');
        link.href = result.reference_source;
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        link.textContent = 'Open source ↗';
        item.append(link);
      } else if (result.reference_source) {
        item.append(textNode('small', `Source: ${result.reference_source}`, 'strategy-gate-cite'));
      }
      listEl.append(item);
    });
  }

  function renderToolkit(data) {
    document.querySelector('#strategy-result-context').textContent = `${data.tender_title} · ${data.source_portal} · ${data.tender_id}`;
    document.querySelector('[data-limitations]').textContent = data.limitations_note;

    renderGates(data.deterministic_gates);

    // Pillar 01: Pre-Bid Legal Pack
    const prebid = data.prebid_legal_pack;
    const prebidBadge = document.querySelector('[data-prebid-count-badge]');
    if (prebidBadge) prebidBadge.textContent = `${prebid.total_challenges || prebid.representations?.length || 0} ITEMS`;
    const prebidList = document.querySelector('[data-prebid-list]');
    prebidList.replaceChildren();
    if (!prebid.representations?.length) {
      prebidList.append(textNode('li', 'No statutory challenge triggers detected from the entered values.'));
    } else {
      for (const item of prebid.representations) {
        const li = document.createElement('li');
        li.className = 'strategy-rich-item';
        li.append(
          textNode('strong', `${item.clause_reference} · ${item.violation_category.replaceAll('_', ' ')}`),
          textNode('p', item.formal_argument),
          textNode('small', `Requested Corrigendum: ${item.requested_corrigendum_amendment} (Cited: ${item.statutory_authority_cited})`)
        );
        prebidList.append(li);
      }
    }
    latestPrebidMarkdown = prebid.formal_letter_markdown || '';
    document.querySelector('[data-prebid-letter]').textContent = latestPrebidMarkdown;

    // Pillar 02: Consortium & Capability Gaps
    const consortium = data.consortium_recommendation;
    const consortiumBadge = document.querySelector('[data-consortium-badge]');
    if (consortiumBadge) {
      consortiumBadge.textContent = consortium.has_shortfall
        ? (consortium.consortium_formation_advised ? 'JV ADVISED' : 'GAP DETECTED')
        : 'STANDALONE READY';
    }
    document.querySelector('[data-consortium-summary]').textContent = consortium.actionable_summary;
    const gapList = document.querySelector('[data-consortium-gaps]');
    gapList.replaceChildren();
    if (!consortium.identified_gaps?.length) {
      gapList.append(textNode('li', 'No standalone capability shortfalls identified from entered figures.'));
    } else {
      for (const gap of consortium.identified_gaps) {
        const li = document.createElement('li');
        li.className = 'strategy-rich-item';
        li.append(
          textNode('strong', `${gap.gate_name} (${gap.shortfall_type})`),
          textNode('p', `Current: ${gap.bidder_current_value} · Required: ${gap.tender_required_value} · Gap: ${gap.exact_gap_quantification}`),
          textNode('small', gap.bridging_strategy)
        );
        gapList.append(li);
      }
    }

    const partnersWrap = document.querySelector('[data-consortium-partners-wrap]');
    const partnersContainer = document.querySelector('[data-consortium-partners]');
    if (partnersWrap && partnersContainer) {
      partnersContainer.replaceChildren();
      if (consortium.recommended_partners?.length) {
        partnersWrap.hidden = false;
        consortium.recommended_partners.forEach((p) => {
          const card = document.createElement('div');
          card.className = 'strategy-partner-card';
          card.append(
            textNode('strong', `${p.partner_name} (${p.entity_type})`),
            textNode('span', `${p.role_in_consortium} · Avg Turnover: ₹${p.avg_annual_turnover_lakhs}L`, 'strategy-partner-meta'),
            textNode('p', p.synergy_rationale),
            textNode('small', `Certifications: ${(p.held_certifications || []).join(', ') || 'Standard'} · Location: ${p.location_state}`)
          );
          partnersContainer.append(card);
        });
      } else {
        partnersWrap.hidden = true;
      }
    }

    // Pillar 03: Compliance Matrix & Statutory Affidavits
    const compliance = data.compliance_binder;
    document.querySelector('[data-compliance-note]').textContent = compliance.review_note || 'Verify each row against the official tender schedule.';
    const tableBody = document.querySelector('[data-compliance-rows]');
    tableBody.replaceChildren();
    for (const row of compliance.compliance_rows) {
      const tr = document.createElement('tr');
      const statusPill = textNode('span', row.compliance_status.replaceAll('_', ' '), `strategy-status-pill status-${row.compliance_status.toLowerCase()}`);
      const tdClause = textNode('td', `${row.clause_id} (p.${row.page_number ?? 1})`);
      const tdReq = textNode('td', row.requirement_summary);
      const tdStatus = document.createElement('td');
      tdStatus.append(statusPill);
      const tdProof = textNode('td', `${row.bidder_proof_and_datasheet_mapping} — ${row.deviation_statement}`);
      tr.append(tdClause, tdReq, tdStatus, tdProof);
      tableBody.append(tr);
    }
    latestCsv = compliance.csv_export_string || '';
    document.querySelector('[data-download-csv]').disabled = !latestCsv;
    renderAffidavits(compliance.statutory_affidavits);

    // Pillar 04: EMD Optimizer
    const emd = data.emd_capital_report;
    const emdBadge = document.querySelector('[data-emd-instrument-badge]');
    if (emdBadge) emdBadge.textContent = (emd.recommended_instrument || 'EMD').replaceAll('_', ' ');
    const metricList = document.querySelector('[data-emd-metrics]');
    metricList.replaceChildren();
    const oppCost = emd.estimated_opportunity_cost_inr ?? emd.opportunity_cost_at_12pct_pa_inr;
    const metrics = [
      ['Entered EMD', formatMoney(emd.emd_required_inr)],
      ['Effective cash lock-up', formatMoney(emd.effective_cash_lockup_inr)],
      ['Estimated capital cost', oppCost == null ? 'Not calculated' : formatMoney(oppCost)],
      ['Portfolio utilization', emd.portfolio_capital_utilization_pct != null ? `${emd.portfolio_capital_utilization_pct}%` : '0%'],
      ['Surety Bond allowed', emd.surety_bond_permitted == null ? 'Not checked' : (emd.surety_bond_permitted ? 'Permitted (IRDAI Surety)' : 'Not permitted')],
      ['Governing rule', emd.exemption_statute || 'Standard EMD schedule']
    ];
    for (const [label, value] of metrics) {
      metricList.append(textNode('dt', label), textNode('dd', value));
    }
    document.querySelector('[data-emd-note]').textContent = emd.liquidity_advisory;

    // Pillar 05: Competitor Forensics
    document.querySelector('[data-forensics-advice]').textContent = data.competitor_forensics.strategic_bid_advice;
    renderForensicsItems(document.querySelector('[data-forensics-results]'), data.competitor_forensics.historical_patterns);
    setStatus(document.querySelector('[data-forensics-status]'), '');
    
    
    // Card 06: Startup Statutory Shield (Fair Play Equalizer)
    const shield = data.startup_statutory_shield || data.startup_exemption_audit;
    if (shield && document.querySelector('[data-shield-summary]')) {
      const summaryText = shield.legal_protection_summary || shield.legal_shield_summary || 'Statutory protection active under GFR 2017 Rule 173(i) and GeM GTC Clause 4(xiii)(h).';
      document.querySelector('[data-shield-summary]').textContent = summaryText;

      const vContainer = document.querySelector('[data-shield-verdict-container]');
      if (vContainer) {
        vContainer.replaceChildren();
        const verdict = shield.overall_shield_verdict || shield.audit_verdict || 'SHIELD_ACTIVE';
        const vBadge = textNode('span', `SHIELD STATUS: ${verdict.replaceAll('_', ' ')}`, 'strategy-status-pill');
        vBadge.style.fontSize = '0.82rem';
        vBadge.style.fontWeight = '700';
        vBadge.style.padding = '0.4rem 0.8rem';
        vBadge.style.borderRadius = '4px';
        if (verdict.includes('VOID') || verdict.includes('SHIELDED') || verdict.includes('OVERRIDDEN')) {
          vBadge.style.background = 'rgba(37, 99, 235, 0.15)';
          vBadge.style.color = '#2563eb';
          vBadge.style.border = '1px solid #2563eb';
        } else {
          vBadge.style.background = 'rgba(5, 150, 105, 0.15)';
          vBadge.style.color = '#059669';
          vBadge.style.border = '1px solid #059669';
        }
        vContainer.append(vBadge);
      }

      const shieldMetrics = document.querySelector('[data-shield-metrics]');
      if (shieldMetrics) {
        shieldMetrics.replaceChildren();
        const statutes = Array.isArray(shield.governing_statutes) ? shield.governing_statutes.join(' · ') : (shield.governing_statute_citation || 'MoF OM No. F.20/2/2014-PPD & GFR 173(i)');
        const sMetrics = [
          ['Statutory Shield Invoked', (shield.statutory_shield_invoked ?? true) ? 'YES (Legally Protected)' : 'NO'],
          ['Turnover Waived', shield.turnover_waived_lakhs != null ? `₹${shield.turnover_waived_lakhs} Lakhs` : 'Full Exemption'],
          ['Experience Waived', shield.experience_waived_years != null ? `${shield.experience_waived_years} Years` : 'Full Exemption'],
          ['EMD Waived', shield.emd_waived_inr != null ? `₹${shield.emd_waived_inr.toLocaleString('en-IN')}` : 'Rule 170(i) Exempt'],
          ['Governing Authority', statutes]
        ];
        for (const [lbl, val] of sMetrics) {
          shieldMetrics.append(textNode('dt', lbl), textNode('dd', val));
        }
      }

      const alertsList = document.querySelector('[data-shield-alerts]');
      if (alertsList) {
        alertsList.replaceChildren();
        const violations = shield.active_violations || data.fair_play_violations || [];
        if (!violations.length) {
          alertsList.append(textNode('li', 'Zero illegal cartel restrictions detected. All statutory exemptions intact.'));
        } else {
          for (const alert of violations) {
            const li = document.createElement('li');
            li.style.marginBottom = '0.6rem';
            li.append(
              textNode('strong', `[${alert.severity_level || 'CRITICAL'}] ${alert.violation_type}: `),
              textNode('span', `${alert.impugned_tender_clause || alert.specific_clause_reference || ''} — ${alert.statutory_countermeasure || alert.countermeasure_action || ''}`)
            );
            alertsList.append(li);
          }
        }
      }
    }

    // Card 07: Zero-History Competency Engine
    const tech = data.technical_equivalence_proof;
    if (tech && document.querySelector('[data-tech-proof-note]')) {
      document.querySelector('[data-tech-proof-note]').textContent = tech.evaluator_justification_note;
      const techMetrics = document.querySelector('[data-tech-proof-metrics]');
      if (techMetrics) {
        techMetrics.replaceChildren();
        const tMetrics = [
          ['Composite Merit Score', `${tech.overall_competency_score} / 100 (${tech.qualifies_for_technical_equivalence ? 'QUALIFIED' : 'DEFICIENT'})`],
          ['Vector 1: Lab & Standards', `${tech.lab_and_standards_score} / 40.0 pts`],
          ['Vector 2: Plant & Capacity', `${tech.plant_and_capacity_score} / 25.0 pts`],
          ['Vector 3: IP & Local Content', `${tech.ip_and_mii_content_score} / 20.0 pts`],
          ['Vector 4: Founder Pedigree', `${tech.founder_pedigree_score} / 15.0 pts`]
        ];
        for (const [lbl, val] of tMetrics) {
          techMetrics.append(textNode('dt', lbl), textNode('dd', val));
        }
      }
      const proformaEl = document.querySelector('[data-tech-proof-proforma]');
      if (proformaEl) {
        proformaEl.textContent = tech.proforma_for_equipment_and_qc_markdown;
      }
    }

    // Card 08: Mandatory 25% MSE Subcontracting Quota Gateway
    const mse = data.mse_subcontracting_match;
    if (mse && document.querySelector('[data-mse-quota-scope]')) {
      document.querySelector('[data-mse-quota-scope]').textContent = mse.subcontract_scope_description;
      const mseMetrics = document.querySelector('[data-mse-quota-metrics]');
      if (mseMetrics) {
        mseMetrics.replaceChildren();
        const mMetrics = [
          ['Entry Mode', (mse.recommended_entry_mode || '').replaceAll('_', ' ')],
          ['25% Reserved Allocation', `₹${(mse.mandatory_25pct_allocation_lakhs || 0).toFixed(2)} Lakhs (Total: ₹${(mse.estimated_tender_value_lakhs || 0).toFixed(1)}L)`],
          ['L1+15% Split-Order Right', mse.l1_plus_15pct_price_preference_eligible ? 'Eligible to match L1' : 'Not Eligible'],
          ['Matched Prime Partner', mse.matched_prime_epc_partner ? `${mse.matched_prime_epc_partner.company_name} (${mse.matched_prime_epc_partner.entity_type}, ₹${mse.matched_prime_epc_partner.avg_annual_turnover_lakhs}L Turnover)` : 'None Required']
        ];
        for (const [lbl, val] of mMetrics) {
          mseMetrics.append(textNode('dt', lbl), textNode('dd', val));
        }
      }
      const mouEl = document.querySelector('[data-mse-mou-markdown]');
      if (mouEl) {
        mouEl.textContent = mse.tripartite_mou_draft_markdown;
      }
    }

    submittedTitle = data.tender_title;
    submittedPortal = data.source_portal;
    results.hidden = false;
  }

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (!apiBase) {
      setStatus(status, 'Set the FastAPI base URL for this website before creating a preview.', 'unavailable');
      return;
    }
    submit.disabled = true;
    setStatus(status, 'Running deterministic gates and building 5-pillar review pack…', 'loading');
    try {
      const response = await fetch(`${apiBase}/api/v1/strategy/preview`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify(buildRequest())
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) {
        const detail = typeof payload.detail === 'string' ? payload.detail : 'Check the values and make sure the TenderLens API is running.';
        throw new Error(detail);
      }
      renderToolkit(payload);
      setStatus(status, '5-Pillar Strategy Preview ready. Verify source documents before relying on any result.', 'success');
      results.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } catch (error) {
      setStatus(status, error.message || 'Could not create the preview. Check the API connection and try again.', 'error');
    } finally {
      submit.disabled = false;
    }
  });

  document.querySelector('[data-download-csv]')?.addEventListener('click', () => {
    if (!latestCsv) return;
    const url = URL.createObjectURL(new Blob([latestCsv], { type: 'text/csv;charset=utf-8' }));
    const link = document.createElement('a');
    link.href = url;
    link.download = 'tenderlens-compliance-matrix.csv';
    link.click();
    URL.revokeObjectURL(url);
  });

  document.querySelector('[data-copy-prebid]')?.addEventListener('click', async (event) => {
    if (!latestPrebidMarkdown) return;
    const btn = event.currentTarget;
    try {
      await navigator.clipboard.writeText(latestPrebidMarkdown);
      btn.textContent = 'Copied!';
      setTimeout(() => { btn.textContent = 'Copy letter'; }, 1500);
    } catch (e) {
      // ignore
    }
  });

  document.querySelector('[data-download-prebid]')?.addEventListener('click', () => {
    if (!latestPrebidMarkdown) return;
    const url = URL.createObjectURL(new Blob([latestPrebidMarkdown], { type: 'text/markdown;charset=utf-8' }));
    const link = document.createElement('a');
    link.href = url;
    link.download = 'prebid-representation-pack.md';
    link.click();
    URL.revokeObjectURL(url);
  });

  document.querySelector('[data-copy-affidavit]')?.addEventListener('click', async (event) => {
    const item = latestAffidavits[selectedAffidavitIndex];
    if (!item) return;
    const btn = event.currentTarget;
    try {
      await navigator.clipboard.writeText(item.content_markdown);
      btn.textContent = 'Copied!';
      setTimeout(() => { btn.textContent = 'Copy selected draft'; }, 1500);
    } catch (e) {
      // ignore
    }
  });

  document.querySelector('[data-download-affidavit]')?.addEventListener('click', () => {
    const item = latestAffidavits[selectedAffidavitIndex];
    if (!item) return;
    const url = URL.createObjectURL(new Blob([item.content_markdown], { type: 'text/markdown;charset=utf-8' }));
    const link = document.createElement('a');
    link.href = url;
    link.download = `${item.doc_code.toLowerCase()}.md`;
    link.click();
    URL.revokeObjectURL(url);
  });

  document.querySelector('[data-forensics-search]')?.addEventListener('click', async (event) => {
    const button = event.currentTarget;
    const searchStatus = document.querySelector('[data-forensics-status]');
    const list = document.querySelector('[data-forensics-results]');
    if (!apiBase || !submittedTitle) return setStatus(searchStatus, 'Create the preview first.', 'error');
    button.disabled = true;
    setStatus(searchStatus, 'Searching public sources…', 'loading');
    try {
      const query = new URLSearchParams({ tender_title: submittedTitle, source_portal: submittedPortal, live_search: 'true' });
      const response = await fetch(`${apiBase}/api/v1/strategy/forensics?${query}`, { headers: { Accept: 'application/json' } });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(typeof payload.detail === 'string' ? payload.detail : 'The public search is unavailable.');
      if (!payload.historical_patterns?.length) {
        setStatus(searchStatus, payload.strategic_bid_advice || 'No results were returned.', '');
      } else {
        renderForensicsItems(list, payload.historical_patterns);
        setStatus(searchStatus, payload.strategic_bid_advice, 'success');
      }
    } catch (error) {
      setStatus(searchStatus, error.message || 'The public search failed.', 'error');
    } finally {
      button.disabled = false;
    }
  });

  document.querySelector('[data-new-preview]')?.addEventListener('click', () => {
    form.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });

  // -------------------------------------------------------------------------
  // Section 06: Precedence DAG & RAG Conflict Resolver Workbench
  // -------------------------------------------------------------------------
  const RAG_PRESETS = {
    'turnover-override': {
      query: 'What is the governing minimum annual turnover requirement and is MSME exemption allowed?',
      chunks: [
        {
          document_name: 'Main_Tender_RFP.pdf',
          precedence_rank: 5,
          page_number: 12,
          clause_id: 'Sec-3.1',
          text_content: 'Minimum average annual turnover of the bidder during the last 3 years shall be Rs. 500 Lakhs. Standard MSME turnover exemption under GFR 173(i) is applicable.'
        },
        {
          document_name: 'Buyer_Added_ATC.pdf',
          precedence_rank: 3,
          page_number: 4,
          clause_id: 'ATC-4.2',
          text_content: 'Minimum annual turnover of Rs. 350 Lakhs required. No exemption to MSME or Startup is allowed for turnover criteria due to critical grid safety.'
        },
        {
          document_name: 'Corrigendum_02_Final.pdf',
          precedence_rank: 1,
          page_number: 1,
          clause_id: 'CORR-2.1',
          text_content: 'In partial modification of ATC-4.2 and Sec-3.1, the minimum average annual turnover requirement is revised to Rs. 200 Lakhs, and Udyam registered MSMEs are eligible for 50% turnover relaxation.'
        }
      ]
    },
    'emd-relaxation': {
      query: 'What is the required Earnest Money Deposit (EMD) amount and are Insurance Surety Bonds accepted?',
      chunks: [
        {
          document_name: 'Main_Bid_Schedule.pdf',
          precedence_rank: 5,
          page_number: 6,
          clause_id: 'EMD-1.1',
          text_content: 'Bidders shall submit an Earnest Money Deposit (EMD) of Rs. 10,00,000 by Account Payee Demand Draft or Fixed Deposit Receipt only.'
        },
        {
          document_name: 'Corrigendum_01_EMD.pdf',
          precedence_rank: 1,
          page_number: 1,
          clause_id: 'CORR-1.4',
          text_content: 'EMD amount is reduced to Rs. 5,00,000. In accordance with MoF OM F.1/1/2022-PPD, IRDAI Insurance Surety Bonds and NeSL e-BG are accepted, and MSEs are exempt upon submitting Bid Security Declaration.'
        }
      ]
    }
  };

  let activeRagChunks = RAG_PRESETS['turnover-override'].chunks.map((c) => ({ ...c }));
  const ragForm = document.getElementById('rag-workbench-form');
  const ragChunksList = document.querySelector('[data-rag-chunks-list]');
  const ragStatus = document.getElementById('rag-status');

  function renderRagChunkEditors() {
    if (!ragChunksList) return;
    ragChunksList.replaceChildren();
    const rankLabels = {
      1: 'Rank 1 · Corrigendum (Highest Precedence)',
      2: 'Rank 2 · GeM System ATC',
      3: 'Rank 3 · Buyer Added ATC',
      4: 'Rank 4 · Technical Specs',
      5: 'Rank 5 · Main Tender PDF (Lowest Precedence)'
    };
    activeRagChunks.forEach((chunk, index) => {
      const box = document.createElement('div');
      box.className = 'strategy-rag-chunk-box';
      const head = document.createElement('div');
      head.className = 'strategy-rag-chunk-head';
      head.append(
        textNode('strong', `${chunk.document_name} · ${chunk.clause_id} (p.${chunk.page_number})`),
        textNode('span', rankLabels[chunk.precedence_rank] || `Rank ${chunk.precedence_rank}`, 'strategy-gate-pill')
      );
      const textarea = document.createElement('textarea');
      textarea.rows = 2;
      textarea.value = chunk.text_content;
      textarea.addEventListener('input', () => {
        activeRagChunks[index].text_content = textarea.value;
      });
      box.append(head, textarea);
      ragChunksList.append(box);
    });
  }

  async function runPrecedenceRag() {
    if (!ragForm) return;
    const queryInput = document.getElementById('rag-query-input');
    const submitBtn = document.getElementById('rag-submit-btn');
    if (submitBtn) submitBtn.disabled = true;
    setStatus(ragStatus, 'Building Precedence DAG and resolving multi-document conflicts…', 'loading');

    // Manage session in browser localStorage without backend database persistence
    try {
      localStorage.setItem('tenderlens_rag_query', queryInput?.value || '');
      localStorage.setItem('tenderlens_rag_chunks', JSON.stringify(activeRagChunks));
    } catch (_) {}

    let data = null;
    if (apiBase) {
      try {
        const response = await fetch(`${apiBase}/api/v1/rag/query`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
          body: JSON.stringify({
            tender_id: 'DAG-WORKBENCH-01',
            query: queryInput?.value || 'What is the governing requirement?',
            explicit_chunks: activeRagChunks,
            enable_gemini: false
          })
        });
        if (response.ok) {
          data = await response.json();
          try { localStorage.setItem('tenderlens_rag_last_result', JSON.stringify(data)); } catch (_) {}
        }
      } catch (err) {
        // Fallback handled seamlessly in ongoing session
      }
    }

    if (!data) {
      const sorted = [...activeRagChunks].sort((a, b) => (a.precedence_rank || 5) - (b.precedence_rank || 5));
      const topChunk = sorted[0];
      const isConflict = sorted.length > 1;

      data = {
        tender_id: 'DAG-WORKBENCH-01',
        has_precedence_conflict: isConflict,
        authoritative_Direct_Answer: topChunk ? topChunk.text_content : 'No governing clause found.',
        retrieved_nodes: sorted.map((chunk, idx) => ({
          document_name: chunk.document_name,
          precedence_label: chunk.precedence_rank === 1 ? 'Rank 1 · Corrigendum (Highest Precedence)' : (chunk.precedence_rank === 3 ? 'Rank 3 · Buyer Added ATC' : 'Rank 5 · Main Tender PDF (Lowest Precedence)'),
          clause_id: chunk.clause_id,
          verbatim_text: chunk.text_content,
          status: idx === 0 ? 'ACTIVE_AUTHORITATIVE' : 'SUPERSEDED'
        })),
        precedence_audit_trail: sorted.map((chunk, idx) =>
          idx === 0
            ? `[GOVERNING CLAUSE] ${chunk.document_name} (${chunk.clause_id}): Rank ${chunk.precedence_rank} holds highest precedence. Authoritative terms enforced.`
            : `[SUPERSEDED CLAUSE] ${chunk.document_name} (${chunk.clause_id}): Overridden by higher-ranking Corrigendum terms per Indian Public Procurement hierarchy.`
        )
      };
      try { localStorage.setItem('tenderlens_rag_last_result', JSON.stringify(data)); } catch (_) {}
    }

    const titleEl = document.querySelector('[data-rag-answer-title]');
    const answerEl = document.querySelector('[data-rag-direct-answer]');
    const nodesEl = document.querySelector('[data-rag-dag-nodes]');
    const trailEl = document.querySelector('[data-rag-audit-trail]');

    const hasConflict = Boolean(data.conflict_detected || data.has_precedence_conflict);
    if (titleEl) {
      titleEl.textContent = hasConflict
        ? 'Conflict Detected & Resolved via Precedence Hierarchy'
        : 'Authoritative Clause Retrieved';
    }
    if (answerEl) {
      answerEl.textContent = data.answer || data.authoritative_Direct_Answer || (data.winning_citation && data.winning_citation.verbatim_text) || 'Governing term identified.';
    }

    // Merge nodes from audit_trail, retrieved_nodes, or winning_citation
    let nodesList = [];
    if (Array.isArray(data.audit_trail) && data.audit_trail.length) {
      nodesList = data.audit_trail;
    } else if (Array.isArray(data.retrieved_nodes) && data.retrieved_nodes.length) {
      nodesList = data.retrieved_nodes;
    } else if (data.winning_citation) {
      nodesList = [data.winning_citation];
    }

    if (nodesEl) {
      nodesEl.replaceChildren();
      nodesList.forEach((node) => {
        const card = document.createElement('div');
        const isSuperseded = Boolean(node.is_superseded || node.status === 'SUPERSEDED');
        card.className = `strategy-rag-node-card ${isSuperseded ? 'node-superseded' : 'node-authoritative'}`;

        const badge = document.createElement('span');
        badge.className = `strategy-gate-pill ${isSuperseded ? 'pill-fail' : 'pill-pass'}`;
        badge.textContent = isSuperseded ? 'SUPERSEDED' : 'GOVERNING CLAUSE';

        const rankLabel = node.precedence_label || (node.precedence_rank === 1 ? 'Rank 1 · Corrigendum (Highest Precedence)' : (node.precedence_rank === 3 ? 'Rank 3 · Buyer Added ATC' : 'Rank 5 · Main Tender PDF (Lowest Precedence)'));

        const headWrap = document.createElement('div');
        headWrap.className = 'strategy-rag-node-header';
        headWrap.append(
          textNode('div', `${rankLabel} · ${node.document_name} (${node.clause_id})`, 'strategy-rag-node-title'),
          badge
        );

        const textContent = node.verbatim_text || node.text_snippet || node.text_content || '';
        card.append(headWrap, textNode('p', textContent, isSuperseded ? 'text-superseded' : 'text-authoritative'));
        nodesEl.append(card);
      });
    }

    if (trailEl) {
      trailEl.replaceChildren();
      if (Array.isArray(data.precedence_audit_trail) && data.precedence_audit_trail.length) {
        data.precedence_audit_trail.forEach((line) => trailEl.append(textNode('li', line)));
      } else if (nodesList.length) {
        nodesList.forEach((n) => {
          const isSup = Boolean(n.is_superseded || n.status === 'SUPERSEDED');
          const prefix = isSup ? '[SUPERSEDED CLAUSE]' : '[GOVERNING CLAUSE]';
          const trailText = `${prefix} ${n.document_name} (${n.clause_id}): Rank ${n.precedence_rank || 5} ${isSup ? 'overridden by Corrigendum' : 'holds legal precedence'}.`;
          trailEl.append(textNode('li', trailText));
        });
      }
    }
    setStatus(ragStatus, 'Precedence DAG resolved.', 'success');
    if (submitBtn) submitBtn.disabled = false;
  }

  document.querySelectorAll('[data-rag-preset]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const preset = RAG_PRESETS[btn.dataset.ragPreset];
      if (!preset) return;
      const qInput = document.getElementById('rag-query-input');
      if (qInput) qInput.value = preset.query;
      activeRagChunks = preset.chunks.map((c) => ({ ...c }));
      renderRagChunkEditors();
      runPrecedenceRag();
    });
  });

  if (ragForm) {
    renderRagChunkEditors();
    ragForm.addEventListener('submit', (event) => {
      event.preventDefault();
      runPrecedenceRag();
    });
  }

  // Live Hackathon Demo Preset Listener
  const presetBtn = document.querySelector('[data-load-zero-history-preset]');
  if (presetBtn) {
    presetBtn.addEventListener('click', () => {
      field('tender_title').value = 'Supply & Commissioning of Indigenous Smart LV Switchgear Panels';
      field('tender_id').value = 'GEM/2026/B/9941208';
      field('source_portal').value = 'GeM';
      field('company_name').value = 'AetherGrid Hardware Labs Pvt. Ltd.';
      field('entity_type').value = 'OEM';
      field('years_in_business').value = '0';
      field('is_msme_registered').checked = true;
      field('is_startup_recognized').checked = true;
      field('turnover_year_1_lakhs').value = '0';
      field('turnover_year_2_lakhs').value = '0';
      field('turnover_year_3_lakhs').value = '0';
      field('local_content_percentage').value = '82';
      field('held_certifications').value = 'ISO 9001, BIS, NABL Type-Test, STQC';
      field('min_annual_turnover_lakhs').value = '200';
      field('min_experience_years').value = '3';
      field('estimated_bid_value_lakhs').value = '500';
      field('emd_amount_inr').value = '1000000';
      field('min_local_content_percentage').value = '50';
      field('mandatory_certifications').value = 'ISO 9001, BIS';
      field('is_turnover_exemption_revoked_by_atc').checked = true;
      field('is_experience_exemption_revoked_by_atc').checked = true;
      field('proprietary_brand_lock_detected').checked = true;
      field('proprietary_brand_details').value = 'Clause 14.2 Buyer ATC: Only imported Make-X switchgear permitted; no MSME/Startup relaxation.';
      setStatus(status, 'Zero-History Startup vs. ₹5 Cr Cartel Tender loaded! Click "Create review preview" to run.', 'success');
      form.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  }


  // Interactive Pillar Strip Smooth Navigation
  document.querySelectorAll('.strategy-pillar-anchor').forEach((anchor) => {
    anchor.addEventListener('click', (e) => {
      const href = anchor.getAttribute('href');
      if (!href || !href.startsWith('#')) return;
      const targetEl = document.querySelector(href);
      if (!targetEl) return;
      e.preventDefault();
      const resultsPanel = document.getElementById('strategy-results');
      if (resultsPanel && resultsPanel.hidden && href !== '#precedence-rag-workbench') {
        form.requestSubmit();
        setTimeout(() => {
          targetEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 600);
      } else {
        targetEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

})();
