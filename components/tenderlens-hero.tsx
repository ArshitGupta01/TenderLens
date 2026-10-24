import * as React from "react"
import { createRoot } from "react-dom/client"
import DoodleCrewFooter from "./ui/doodle-crew-footer"

export function TenderLensHero({ wordmarkOnly = true }: { wordmarkOnly?: boolean } = {}) {
  return (
    <div className="w-full">
      <DoodleCrewFooter
        wordmark="TENDERLENS"
        wordmarkOnly={wordmarkOnly}
        crew={[]}
        doodles={[]}
        tracking={-0.025}
        backToTop={false}
        palette={{
          background: "#090e17",
          ink: "#f8fafc",
          accent: "#38bdf8",
        }}
      />
    </div>
  )
}

export default TenderLensHero

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
