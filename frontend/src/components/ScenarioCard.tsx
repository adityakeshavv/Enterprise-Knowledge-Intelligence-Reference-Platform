import React from "react";
import type { ScenarioItem } from "../types";
import { ArrowRight, Activity } from "lucide-react";

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
  return (
    <div
      className="scenario-card"
      onClick={() => !disabled && onSelect(scenario.question)}
    >
      <div className="scenario-header">
        <span className="scenario-category">{scenario.category}</span>
        <span className="scenario-difficulty">{scenario.difficulty}</span>
      </div>
      <h3 className="scenario-title">{scenario.title}</h3>
      <p className="scenario-question">"{scenario.question}"</p>
      <div className="scenario-footer">
        <span className="scenario-agents">
          <Activity size={12} className="inline mr-1" />
          {scenario.expected_agents?.length || 4} Specialized Agents
        </span>
        <span className="scenario-action">
          Run Scenario <ArrowRight size={14} />
        </span>
      </div>
    </div>
  );
};
