import React, { useState } from 'react';
import { ChevronDown, ChevronRight, Terminal, Cpu } from 'lucide-react';

/**
 * ReasoningTrail component.
 * Displays transparent tool-calling steps executed by the agent to ensure accountability.
 */
export default function ReasoningTrail({ steps = [] }) {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!steps || steps.length === 0) {
    return null;
  }

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-200/80 overflow-hidden">
      <button
        type="button"
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full p-4 flex items-center justify-between text-left hover:bg-slate-50 transition-colors"
      >
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center">
            <Cpu className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-slate-800">Agent Reasoning & Audit Trail</h3>
            <p className="text-xs text-slate-500">{steps.length} tool executions logged for this plan</p>
          </div>
        </div>
        <div className="flex items-center space-x-1.5 text-slate-400 text-xs">
          <span>{isExpanded ? 'Hide' : 'Inspect'}</span>
          {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
        </div>
      </button>

      {isExpanded && (
        <div className="p-4 pt-0 border-t border-slate-100 bg-slate-900 text-slate-200 font-mono text-xs space-y-3">
          {steps.map((step) => (
            <div key={step.step_number} className="p-3 rounded-lg bg-slate-800/80 border border-slate-700/60 space-y-1.5">
              <div className="flex items-center justify-between text-indigo-400">
                <span className="font-bold">Step {step.step_number}: {step.action}</span>
                <span className="text-[10px] bg-indigo-950 text-indigo-300 px-1.5 py-0.5 rounded">
                  tool_call
                </span>
              </div>
              <p className="text-slate-300 font-sans text-xs">{step.rationale}</p>
              <div className="text-[11px] text-teal-400 bg-slate-950/60 p-2 rounded border border-slate-800">
                <span className="text-slate-500">Output: </span>{step.output_summary}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
