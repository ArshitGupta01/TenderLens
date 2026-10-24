import * as React from "react"
import { createRoot } from "react-dom/client"
import DoodleCrewFooter, { CrewMember } from "./ui/doodle-crew-footer"

const TENDERLENS_CREW: CrewMember[] = [
  { kind: "yeti", letter: 0, seat: "front", offset: -0.35, name: "Bruno", says: "Deterministic audit: Zero hallucinations allowed!" },
  { kind: "bird", letter: 1, seat: "top", offset: 0.05, name: "Pip", says: "Addenda precedence active! Clause 4.2 overrides Section B." },
  { kind: "mushroom", letter: 2, seat: "front", offset: 0.15, scale: 0.95, name: "Morel", says: "Source-linked evidence verified in Exhibit C." },
  { kind: "kid", letter: 4, seat: "top", offset: -0.05, name: "Juno", says: "High vantage point! Evaluation score: 94/100." },
  { kind: "ghost", letter: 6, seat: "behind", offset: 0, name: "Boo", says: "Alert! Missing Bid Security Declaration." },
  { kind: "cat", letter: 9, seat: "front", offset: 0.4, flip: true, name: "Patch", says: "Audit passed. Ready for bid submission!" },
]

export function TenderLensHero() {
  return (
    <div className="w-full">
      <DoodleCrewFooter
        wordmark="TENDERLENS"
        wordmarkOnly={true}
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
