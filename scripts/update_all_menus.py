import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

NEW_NAV = """        <nav class="primary-nav" id="primary-nav" data-lenis-prevent aria-label="Main navigation">
          <div class="menu-status-bar">
            <span class="menu-pulse" aria-hidden="true"></span>
            <span class="menu-status-text">TENDERLENS v2.0.2</span>
          </div>
          <div class="menu-group">
            <div class="menu-section-heading">EXPLORE &amp; STRATEGY</div>
            <a class="menu-item menu-item-featured" href="strategy.html">
              <span class="menu-item-lead">
                <span class="menu-item-icon" aria-hidden="true">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
                </span>
                <span class="menu-item-text">Strategy Studio</span>
              </span>
              <span class="menu-tag">5 Pillars</span>
            </a>
            <a class="menu-item" href="strategy.html#precedence-rag-workbench">
              <span class="menu-item-lead">
                <span class="menu-item-icon" aria-hidden="true">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>
                </span>
                <span class="menu-item-text">Precedence DAG Resolver</span>
              </span>
            </a>
            <a class="menu-item" href="guide.html">
              <span class="menu-item-lead">
                <span class="menu-item-icon" aria-hidden="true">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
                </span>
                <span class="menu-item-text">Statutory Exemption Hub</span>
              </span>
            </a>
            <a class="menu-item" href="index.html#opportunities">
              <span class="menu-item-lead">
                <span class="menu-item-icon" aria-hidden="true">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                </span>
                <span class="menu-item-text">Sample Tenders Desk</span>
              </span>
            </a>
            <a class="menu-item" href="account.html">
              <span class="menu-item-lead">
                <span class="menu-item-icon" aria-hidden="true">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>
                </span>
                <span class="menu-item-text">Bidder Profile</span>
              </span>
            </a>
            <a class="menu-item" href="saved-tenders.html">
              <span class="menu-item-lead">
                <span class="menu-item-icon" aria-hidden="true">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg>
                </span>
                <span class="menu-item-text">Saved Tenders</span>
              </span>
            </a>
          </div>
          <div class="menu-group menu-group-footer">
            <div class="menu-section-heading">WORKSPACE &amp; ACCOUNT</div>
            <div class="menu-actions">
              <a class="button button-dark menu-btn" data-auth-signin href="signin.html">Sign in</a>
              <a class="button menu-btn" data-auth-signup href="signup.html">Create account</a>
            </div>
            <div class="menu-legal-links">
              <a href="privacy.html">Privacy</a>
              <span>·</span>
              <a href="terms.html">Terms</a>
            </div>
          </div>
        </nav>"""

nav_pattern = re.compile(r'<nav class="primary-nav" id="primary-nav".*?</nav>', re.DOTALL)

updated_files = []
for html_file in list(ROOT.glob("*.html")) + list((ROOT / "frontend").glob("*.html")):
    content = html_file.read_text(encoding="utf-8")
    if nav_pattern.search(content):
        new_content = nav_pattern.sub(NEW_NAV.strip(), content)
        html_file.write_text(new_content, encoding="utf-8")
        updated_files.append(html_file.name)

print(f"[OK] Updated primary-nav with clean SVGs (0 emojis, 0 AI) across {len(updated_files)} files: {set(updated_files)}")
