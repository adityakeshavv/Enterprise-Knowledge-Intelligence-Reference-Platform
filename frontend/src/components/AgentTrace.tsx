import React, { useState } from "react";
import type { TraceStep } from "../types";
import { CheckCircle2, ChevronDown, ChevronRight, Cpu, Clock, AlertTriangle, Loader2 } from "lucide-react";

interface AgentTraceProps {
  steps: TraceStep[];
  totalLatencyMs: number;
}

export const AgentTrace: React.FC<AgentTraceProps> = ({ steps, totalLatencyMs }) => {
  const [expanded, setExpanded] = useState<boolean>(true);
  const [activeStepId, setActiveStepId] = useState<number | null>(null);

  return (
    <div className="trace-container">
      <div
        className="trace-header"
        role="button"
        tabIndex={0}
        onClick={() => setExpanded(!expanded)}
        aria-expanded={expanded}
        aria-controls="agent-trace-details"
        onKeyDown={(event) => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); setExpanded(!expanded); } }}
      >
        <div className="trace-title">
          <Cpu size={16} className="text-accent" />
          <span>Multi-Agent Reasoning Trace</span>
          <span className="badge-count">{steps.length} Agents Executed</span>
        </div>
        <div className="trace-meta">
          <Clock size={14} className="text-muted" />
          <span>{(totalLatencyMs / 1000).toFixed(2)}s total</span>
          {expanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
        </div>
      </div>

      {expanded && (
        <div className="trace-body" id="agent-trace-details">
          {steps.map((step) => {
            const isSelected = activeStepId === step.step_id;
            return (
              <div
                key={step.step_id}
                className={`trace-step ${isSelected ? "step-selected" : ""}`}
                role="button"
                tabIndex={0}
                onClick={() => setActiveStepId(isSelected ? null : step.step_id)}
                aria-expanded={isSelected}
                aria-label={`${isSelected ? "Hide" : "Show"} details for ${step.agent_label}`}
                onKeyDown={(event) => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); setActiveStepId(isSelected ? null : step.step_id); } }}
              >
                <div className="step-indicator">
                  {step.status === "completed" ? <CheckCircle2 size={16} className="icon-success" /> : step.status === "warning" ? <AlertTriangle size={16} className="text-warning" /> : <Loader2 size={16} className="animate-spin text-accent" />}
                  <div className="step-connector" />
                </div>
                <div className="step-content">
                  <div className="step-top">
                    <span className="agent-badge">{step.agent_label}</span>
                    <span className="step-duration">{step.duration_ms.toFixed(1)}ms</span>
                  </div>
                  <p className="step-message">{step.business_message}</p>
                  {step.technical_detail && isSelected && (
                    <div className="step-technical">
                      <span className="tech-label">Technical Trace:</span>
                      <code>{step.technical_detail}</code>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
