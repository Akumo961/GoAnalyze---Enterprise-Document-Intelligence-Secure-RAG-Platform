"use client";

import { useMemo, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";

const steps = [
  "Secure intake",
  "Document classification",
  "Completeness",
  "Evidence search",
  "AI answer + citations",
  "Regulatory mapping",
  "Priority assessment",
  "Analyst assignment",
  "Human decision",
  "Audit trail",
];

const documents = [
  ["01_application_form.pdf", "Application form"],
  ["02_site_plan.pdf", "Site plan"],
  ["03_effluent_characterization.pdf", "Effluent characterization"],
  ["04_mitigation_plan.pdf", "Mitigation plan"],
  ["05_public_consultation_record.pdf", "Consultation record"],
  ["06_impact_assessment.pdf", "Impact assessment"],
  ["07_monitoring_plan.pdf", "Monitoring plan"],
  ["08_technical_memo.pdf", "Technical memo"],
  ["09_communications.pdf", "Correspondence"],
  ["10_appendix.pdf", "Appendix"],
];

export default function Phase1Page() {
  const [step, setStep] = useState(0);
  const progress = useMemo(() => Math.round(((step + 1) / steps.length) * 100), [step]);

  return (
    <AppShell>
      <div className="pageHeading">
        <div>
          <h1>Phase 1 Pilot — Environmental Case</h1>
          <p>Synthetic demonstration only. No real regulatory decision is made.</p>
        </div>
        <div className="badge">DEMO DATA</div>
      </div>

      <div className="card" style={{ marginBottom: 16 }}>
        <div style={{ display: "flex", justifyContent: "space-between", gap: 16 }}>
          <div>
            <strong>North River Synthetic Industrial Facility</strong>
            <div className="muted">Demo Industries Inc. · Synthetic Region · Industrial discharge</div>
          </div>
          <div><strong>{progress}%</strong><div className="muted">pilot workflow</div></div>
        </div>
        <div style={{ marginTop: 12, height: 8, borderRadius: 4, background: "var(--surface-muted, #eee)" }}>
          <div style={{ width: `${progress}%`, height: "100%", borderRadius: 4, background: "currentColor" }} />
        </div>
      </div>

      <div className="grid2">
        <div className="card">
          <h2>Workflow</h2>
          <ol>
            {steps.map((name, index) => (
              <li key={name} style={{ marginBottom: 8 }}>
                <button className={index === step ? "btn btnPrimary" : "btn"} onClick={() => setStep(index)}>
                  {index + 1}. {name}
                </button>
              </li>
            ))}
          </ol>
        </div>

        <div className="card">
          {step === 0 && <><h2>Secure intake</h2><p>10 synthetic documents loaded into the demo tenant. Production malware scanning and external object storage are not exercised by this screen.</p></>}
          {step === 1 && <><h2>Classification</h2><p>Deterministic synthetic classifier assigns document types for the pilot.</p><ul>{documents.map(([file, type]) => <li key={file}>{file} — {type}</li>)}</ul></>}
          {step === 2 && <><h2>Completeness</h2><p><strong>Complete for the synthetic pilot checklist.</strong> Required demonstration document types are present.</p></>}
          {step === 3 && <><h2>Evidence search</h2><p>Search is restricted to evidence supplied by the synthetic case. Cross-tenant retrieval is not represented by the demo UI.</p></>}
          {step === 4 && <><h2>AI answer</h2><div className="card"><strong>Question:</strong> What monitoring locations are described?<br /><br /><strong>Answer:</strong> The synthetic case references monitoring location M-01 and discharge point D-01.<br /><br /><span className="badge">FACTUAL EVIDENCE</span><p className="muted">Source: 02_site_plan.pdf, page 1. Synthetic evidence only.</p></div></>}
          {step === 5 && <><h2>Regulatory mapping</h2><p>Two synthetic obligations are mapped. Authority: <strong>DEMO</strong>. No Québec legal requirement is asserted.</p><ul><li>DEMO-ENV-001 — synthetic submission evidence</li><li>DEMO-ENV-002 — synthetic mitigation evidence</li></ul></>}
          {step === 6 && <><h2>Priority assessment</h2><p><strong>Medium priority</strong></p><p>Method: synthetic demonstration heuristic. This is not a regulatory risk determination.</p></>}
          {step === 7 && <><h2>Analyst queue</h2><p>Assigned to <strong>analyst.demo</strong> in <strong>environmental-technical-review</strong>.</p><p>Human review remains mandatory.</p></>}
          {step === 8 && <><h2>Human decision</h2><p><strong>Accept for further review</strong></p><p>Note: Synthetic analyst review completed; continue technical assessment.</p></>}
          {step === 9 && <><h2>Audit trail</h2><p>Case creation, classification, completeness, AI question, regulatory mapping, priority, assignment and analyst decision are represented as ordered audit events.</p><span className="badge">DECISION SUPPORT ONLY</span></>}
        </div>
      </div>

      <div style={{ display: "flex", justifyContent: "space-between", marginTop: 16 }}>
        <button className="btn" disabled={step === 0} onClick={() => setStep((value) => Math.max(0, value - 1))}>Previous</button>
        <button className="btn btnPrimary" disabled={step === steps.length - 1} onClick={() => setStep((value) => Math.min(steps.length - 1, value + 1))}>Next</button>
      </div>
    </AppShell>
  );
}
