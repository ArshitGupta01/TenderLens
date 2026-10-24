import * as React from "react"
import { createRoot } from "react-dom/client"
import DoodleCrewFooter, { CrewMember, FooterAction, FooterColumn } from "./ui/doodle-crew-footer"

const TENDERLENS_CREW: CrewMember[] = [
  { kind: "yeti", letter: 0, seat: "front", offset: -0.35, name: "Bruno", says: "Deterministic audit: Zero hallucinations allowed!" },
  { kind: "bird", letter: 1, seat: "top", offset: 0.05, name: "Pip", says: "Addenda precedence active! Clause 4.2 overrides Section B." },
  { kind: "mushroom", letter: 2, seat: "front", offset: 0.15, scale: 0.95, name: "Morel", says: "Source-linked evidence verified in Exhibit C." },
  { kind: "kid", letter: 4, seat: "top", offset: -0.05, name: "Juno", says: "High vantage point! Evaluation score: 94/100." },
  { kind: "ghost", letter: 6, seat: "behind", offset: 0, name: "Boo", says: "Alert! Missing Bid Security Declaration." },
  { kind: "cat", letter: 9, seat: "front", offset: 0.4, flip: true, name: "Patch", says: "Audit passed. Ready for bid submission!" },
]

const TENDERLENS_ACTIONS: FooterAction[] = [
  { label: "Explore Opportunities", href: "#opportunities", icon: "bolt", variant: "solid" },
  { label: "Open Strategy Studio", href: "strategy.html", icon: "sparkle", variant: "outline" },
]

const TENDERLENS_COLUMNS: FooterColumn[] = [
  {
    title: "Analysis Desk",
    links: [
      { label: "Live Compliance DAG", href: "#demo" },
      { label: "Deterministic Engine", href: "#precedence" },
      { label: "Bidder Matrix", href: "#contractor" },
      { label: "Criteria Matrix", href: "#checklist" },
    ],
  },
  {
    title: "Strategy Studio",
    links: [
      { label: "5 Core Pillars", href: "strategy.html#pillars" },
      { label: "Pricing Guard", href: "strategy.html#pricing" },
      { label: "Risk Matrix", href: "strategy.html#risks" },
      { label: "Competitor Analysis", href: "strategy.html#competition" },
    ],
  },
  {
    title: "Resources & Rules",
    links: [
      { label: "Zero-Assumption Guide", href: "guide.html" },
      { label: "Precedence Protocol", href: "#precedence" },
      { label: "Saved Tenders", href: "saved-tenders.html" },
      { label: "Account Settings", href: "account.html" },
    ],
  },
  {
    title: "Compliance Trust",
    links: [
      { label: "Supabase Live Auth", href: "signin.html" },
      { label: "Terms of Submission", href: "terms.html" },
      { label: "Privacy Policy", href: "privacy.html" },
      { label: "System Health v1.0.3", href: "#" },
    ],
  },
]

export function TenderLensHero() {
  return (
    <div className="w-full">
      <DoodleCrewFooter
        wordmark="TENDERLENS"
        brand="TenderLens"
        blurb="Deterministic tender compliance intelligence. Real document hierarchy, verifiable criteria audits, and instant risk matrices."
        tagline="Every clause cited. Every ambiguity flagged. Ready for human review & submission."
        columns={TENDERLENS_COLUMNS}
        actions={TENDERLENS_ACTIONS}
        copyright="© 2026 TenderLens Compliance Intelligence. All rights reserved."
        legal={[
          { label: "Privacy Policy", href: "privacy.html" },
          { label: "Terms of Service", href: "terms.html" },
          { label: "Security & RLS", href: "guide.html" },
        ]}
        socials={[
          { label: "GitHub", href: "https://github.com/ArshitGupta01/TenderLens" },
          { label: "Strategy Studio", href: "strategy.html" },
          { label: "Account", href: "account.html" },
        ]}
        backToTop={false}
        crew={TENDERLENS_CREW}
        palette={{
          background: "#090e17",
          ink: "#f8fafc",
          accent: "#38bdf8",
        }}
      />
    </div>
  )
}

if (typeof window !== "undefined") {
  const mountHero = () => {
    const mountTarget = document.getElementById("tenderlens-doodle-root")
    if (mountTarget && !mountTarget.hasAttribute("data-mounted")) {
      mountTarget.setAttribute("data-mounted", "true")
      const root = createRoot(mountTarget)
      root.render(<TenderLensHero />)
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mountHero)
  } else {
    mountHero()
  }
}
