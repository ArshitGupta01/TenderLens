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
  let submittedTitle = '';
  let submittedPortal = '';

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
  const setStatus = (element, message, state = '') => {
    if (!element) return;
    element.textContent = message;
    if (state) element.dataset.state = state;
    else delete element.dataset.state;
  };
  const textNode = (tag, value) => {
    const node = document.createElement(tag);
    node.textContent = value == null ? '' : String(value);
    return node;
  };
  const formatMoney = (value) => value == null
    ? 'Not calculated'
    : new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(value);

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
        is_startup_recognized: field('is_startup_recognized').checked,
        turnover_year_1_lakhs: Number(field('turnover_year_1_lakhs').value),
        turnover_year_2_lakhs: Number(field('turnover_year_2_lakhs').value),
        turnover_year_3_lakhs: Number(field('turnover_year_3_lakhs').value),
        years_in_business: Number(field('years_in_business').value),
        local_content_percentage: Number(field('local_content_percentage').value),
        held_certifications: csvList('held_certifications'),
        past_similar_project_values_lakhs: [],
        available_emd_working_capital_inr: optionalNumber('available_emd_working_capital_inr'),
        active_simultaneous_bids_count: Number(field('active_simultaneous_bids_count').value || 1)
      },
      criteria: {
        min_annual_turnover_lakhs: Number(field('min_annual_turnover_lakhs').value),
        min_experience_years: Number(field('min_experience_years').value),
        estimated_bid_value_lakhs: optionalNumber('estimated_bid_value_lakhs'),
        emd_amount_inr: Number(field('emd_amount_inr').value),
        min_local_content_percentage: Number(field('min_local_content_percentage').value),
        mandatory_certifications: csvList('mandatory_certifications'),
        oem_authorization_mandatory: field('oem_authorization_mandatory').checked,
        emd_exemption_confirmed_by_tender: field('emd_exemption_confirmed_by_tender').checked ? true : null,
        msme_turnover_relaxation_allowed: field('msme_turnover_relaxation_allowed').checked ? true : null,
        msme_experience_relaxation_allowed: field('msme_experience_relaxation_allowed').checked ? true : null,
        is_turnover_exemption_revoked_by_atc: field('is_turnover_exemption_revoked_by_atc').checked,
        is_experience_exemption_revoked_by_atc: field('is_experience_exemption_revoked_by_atc').checked,
        proprietary_brand_lock_detected: field('proprietary_brand_lock_detected').checked,
        proprietary_brand_details: field('proprietary_brand_details').value.trim() || null,
        surety_bond_permitted_by_tender: suretyValue === '' ? null : suretyValue === 'true',
        estimated_emd_lockup_days: optionalNumber('estimated_emd_lockup_days'),
        annual_capital_cost_rate_pct: optionalNumber('annual_capital_cost_rate_pct')
      }
    };
  }

  function renderList(target, entries, emptyText) {
    target.replaceChildren();
    if (!entries?.length) {
      target.append(textNode('li', emptyText));
      return;
    }
    for (const entry of entries) target.append(textNode('li', entry));
  }

  function renderToolkit(data) {
    document.querySelector('#strategy-result-context').textContent = `${data.tender_title} · ${data.source_portal} · ${data.tender_id}`;
    document.querySelector('[data-limitations]').textContent = data.limitations_note;

    const prebid = data.prebid_legal_pack;
    renderList(
      document.querySelector('[data-prebid-list]'),
      prebid.representations.map((item) => `${item.clause_reference}: ${item.requested_corrigendum_amendment}`),
      'No review prompts were generated from the values entered. This is not a full tender review.'
    );
    document.querySelector('[data-prebid-letter]').textContent = prebid.formal_letter_markdown;

    const consortium = data.consortium_recommendation;
    document.querySelector('[data-consortium-summary]').textContent = consortium.actionable_summary;
    renderList(
      document.querySelector('[data-consortium-gaps]'),
      consortium.identified_gaps.map((gap) => `${gap.gate_name}: ${gap.bridging_strategy}`),
      'No possible gaps found from the entered values.'
    );

    const compliance = data.compliance_binder;
    document.querySelector('[data-compliance-note]').textContent = compliance.review_note;
    const tableBody = document.querySelector('[data-compliance-rows]');
    tableBody.replaceChildren();
    for (const row of compliance.compliance_rows) {
      const tr = document.createElement('tr');
      const requirement = row.page_number == null
        ? row.requirement_summary
        : `${row.requirement_summary} · p. ${row.page_number}`;
      [requirement, row.compliance_status.replaceAll('_', ' ').toLowerCase(), row.bidder_proof_and_datasheet_mapping].forEach((value) => {
        const td = document.createElement('td');
        td.textContent = value;
        tr.append(td);
      });
      tableBody.append(tr);
    }
    latestCsv = compliance.csv_export_string || '';
    document.querySelector('[data-download-csv]').disabled = !latestCsv;

    const emd = data.emd_capital_report;
    const metricList = document.querySelector('[data-emd-metrics]');
    metricList.replaceChildren();
    const metrics = [
      ['Entered EMD', formatMoney(emd.emd_required_inr)],
      ['Cash-lockup scenario', formatMoney(emd.effective_cash_lockup_inr)],
      ['Estimated capital cost', emd.estimated_opportunity_cost_inr == null ? 'Add a rate and duration to estimate' : formatMoney(emd.estimated_opportunity_cost_inr)],
      ['Instrument allowed', emd.surety_bond_permitted == null ? 'Not checked' : (emd.surety_bond_permitted ? 'Marked yes in your inputs' : 'Marked no in your inputs')]
    ];
    for (const [label, value] of metrics) {
      metricList.append(textNode('dt', label), textNode('dd', value));
    }
    document.querySelector('[data-emd-note]').textContent = emd.liquidity_advisory;

    document.querySelector('[data-forensics-advice]').textContent = data.competitor_forensics.strategic_bid_advice;
    document.querySelector('[data-forensics-results]').replaceChildren();
    setStatus(document.querySelector('[data-forensics-status]'), '');
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
    setStatus(status, 'Building your draft preview…', 'loading');
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
      setStatus(status, 'Preview ready. Review the notes and verify source documents before relying on any result.', 'success');
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
    link.download = 'tenderlens-review-checklist.csv';
    link.click();
    URL.revokeObjectURL(url);
  });

  document.querySelector('[data-forensics-search]')?.addEventListener('click', async (event) => {
    const button = event.currentTarget;
    const searchStatus = document.querySelector('[data-forensics-status]');
    const list = document.querySelector('[data-forensics-results]');
    if (!apiBase || !submittedTitle) return setStatus(searchStatus, 'Create the preview first.', 'error');
    button.disabled = true;
    list.replaceChildren();
    setStatus(searchStatus, 'Searching public sources…', 'loading');
    try {
      const query = new URLSearchParams({ tender_title: submittedTitle, source_portal: submittedPortal, live_search: 'true' });
      const response = await fetch(`${apiBase}/api/v1/strategy/forensics?${query}`, { headers: { Accept: 'application/json' } });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(typeof payload.detail === 'string' ? payload.detail : 'The public search is unavailable.');
      if (!payload.historical_patterns?.length) {
        setStatus(searchStatus, payload.strategic_bid_advice || 'No results were returned.', '');
      } else {
        for (const result of payload.historical_patterns) {
          const item = document.createElement('li');
          const title = textNode('strong', result.common_rejection_trigger);
          const link = document.createElement('a');
          if (result.reference_source?.startsWith('https://')) {
            link.href = result.reference_source;
            link.target = '_blank';
            link.rel = 'noopener noreferrer';
            link.textContent = 'Open source ↗';
          }
          item.append(title);
          if (link.href) item.append(link);
          list.append(item);
        }
        setStatus(searchStatus, payload.strategic_bid_advice, 'success');
      }
    } catch (error) {
      setStatus(searchStatus, error.message || 'The public search failed.', 'error');
    } finally {
      button.disabled = false;
    }
  });

  document.querySelector('[data-new-preview]')?.addEventListener('click', () => {
    results.hidden = true;
    form.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
})();
