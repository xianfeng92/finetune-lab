import { useEffect, useState } from "react";
import { loadLabData, type LabData } from "./data-layer";
import { ALL_VIEWS, type View } from "./ui-types";
import { BeginnerGuideView } from "./views/BeginnerGuideView";
import { OverviewView } from "./views/OverviewView";
import { OnboardingView } from "./views/OnboardingView";
import { DataView } from "./views/DataView";
import { TrainingRunsView } from "./views/TrainingRunsView";
import { CompareView } from "./views/CompareView";

function readViewFromHash(): View | null {
  if (typeof window === "undefined") return null;
  const raw = window.location.hash;
  if (!raw.startsWith("#/")) return null;
  const h = raw.slice(2) as View;
  return ALL_VIEWS.includes(h) ? h : null;
}

const NAV_ITEMS: Array<[View, string]> = [
  ["beginner-guide", "Beginner Guide"],
  ["overview", "Overview"],
  ["onboarding", "Agent Handoff"],
  ["data", "Data Pipeline"],
  ["runs", "Training Runs"],
  ["compare", "Probe Compare"],
];

export default function App() {
  const [view, setViewState] = useState<View>(() => readViewFromHash() ?? "beginner-guide");
  const [labData, setLabData] = useState<LabData | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  const setView = (next: View) => {
    setViewState(next);
    window.history.replaceState(null, "", `#/${next}`);
  };

  useEffect(() => {
    loadLabData()
      .then((data) => {
        setLabData(data);
        setLoadError(null);
      })
      .catch((error: unknown) => {
        console.error(error);
        setLoadError(error instanceof Error ? error.message : "Unknown error");
      });
  }, []);

  useEffect(() => {
    const onHash = () => {
      const next = readViewFromHash();
      if (next) setViewState(next);
    };
    window.addEventListener("hashchange", onHash);
    return () => window.removeEventListener("hashchange", onHash);
  }, []);

  if (loadError) {
    return (
      <div className="state-screen">
        <h1>Failed to load lab data</h1>
        <p>{loadError}</p>
      </div>
    );
  }

  if (!labData) {
    return <div className="state-screen"><h1>Loading lab data…</h1></div>;
  }

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand"><span className="brand-mark">f</span><div><strong>finetune-lab</strong><p>AI-native lab</p></div></div>
        <nav className="nav">
          {NAV_ITEMS.map(([id, label]) => (
            <button key={id} type="button" className={`nav-item ${view === id ? "active" : ""}`} onClick={() => setView(id)}>
              <strong>{label}</strong>
            </button>
          ))}
        </nav>
        <div className="sidebar-footer">
          <span className="eyebrow">repo</span>
          <p>{labData.project.tagline}</p>
        </div>
      </aside>
      <main className="main">
        {view === "beginner-guide" ? <BeginnerGuideView data={labData} /> : null}
        {view === "overview" ? <OverviewView data={labData} onPick={setView} /> : null}
        {view === "onboarding" ? <OnboardingView data={labData} /> : null}
        {view === "data" ? <DataView data={labData} /> : null}
        {view === "runs" ? <TrainingRunsView runs={labData.runs} /> : null}
        {view === "compare" ? <CompareView runs={labData.runs} heldOutDatasetPath={labData.source.held_out_dataset} /> : null}
      </main>
    </div>
  );
}
