import React, { useEffect, useRef, useState } from "react";
import type { ScenarioItem } from "../types";
import { ArrowRight, Activity, X } from "lucide-react";

interface ScenarioCardProps {
  scenario: ScenarioItem;
  onSelect: (question: string) => void;
  disabled: boolean;
}

export const ScenarioCard: React.FC<ScenarioCardProps> = ({
  scenario,
  onSelect,
  disabled,
}) => {
  const [previewOpen, setPreviewOpen] = useState(false);
  const closeRef = useRef<HTMLButtonElement>(null);
  const cardRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!previewOpen) return;
    closeRef.current?.focus();
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") setPreviewOpen(false);
      if (event.key === "Tab") {
        const controls = document.querySelectorAll<HTMLElement>(".scenario-modal button");
        if (controls.length < 2) return;
        if (event.shiftKey && document.activeElement === controls[0]) { event.preventDefault(); controls[controls.length - 1].focus(); }
        else if (!event.shiftKey && document.activeElement === controls[controls.length - 1]) { event.preventDefault(); controls[0].focus(); }
      }
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => { document.removeEventListener("keydown", handleKeyDown); cardRef.current?.focus(); };
  }, [previewOpen]);

  return (
    <>
      <div ref={cardRef} className="scenario-card" role="button" tabIndex={disabled ? -1 : 0} aria-disabled={disabled}
        onClick={() => !disabled && setPreviewOpen(true)}
        onKeyDown={(event) => { if (!disabled && (event.key === "Enter" || event.key === " ")) { event.preventDefault(); setPreviewOpen(true); } }}>
        <div className="scenario-header"><span className="scenario-category">{scenario.category}</span><span className="scenario-difficulty">{scenario.difficulty}</span></div>
        <h3 className="scenario-title">{scenario.title}</h3>
        <p className="scenario-question">{scenario.question}</p>
        <div className="scenario-footer">
          {scenario.expected_agents?.length ? <span className="scenario-agents"><Activity size={12} className="inline mr-1" />{scenario.expected_agents.length} planned agents</span> : <span className="scenario-agents">Suggested inquiry</span>}
          <span className="scenario-action">Review question <ArrowRight size={14} /></span>
        </div>
      </div>
      {previewOpen && (
        <div className="scenario-modal-backdrop" onMouseDown={(event) => { if (event.target === event.currentTarget) setPreviewOpen(false); }}>
          <section className="scenario-modal" role="dialog" aria-modal="true" aria-labelledby={`scenario-title-${scenario.id}`} aria-describedby={`scenario-question-${scenario.id}`}>
            <button ref={closeRef} type="button" className="scenario-modal-close" onClick={() => setPreviewOpen(false)} aria-label="Close scenario preview"><X size={17} /></button>
            <span className="scenario-category">{scenario.category}</span>
            <h2 id={`scenario-title-${scenario.id}`}>{scenario.title}</h2>
            <p className="scenario-modal-question" id={`scenario-question-${scenario.id}`}>{scenario.question}</p>
            {scenario.description && <p>{scenario.description}</p>}
            <div className="scenario-modal-actions">
              <button type="button" className="btn-secondary-action" onClick={() => setPreviewOpen(false)}>Cancel</button>
              <button type="button" className="btn-primary-action" onClick={() => { setPreviewOpen(false); onSelect(scenario.question); }}><ArrowRight size={15} /> Use this question</button>
            </div>
          </section>
        </div>
      )}
    </>
  );
};
