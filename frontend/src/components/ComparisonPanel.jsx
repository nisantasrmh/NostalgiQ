import React from 'react';
import { Layers, ShieldAlert, Sparkles, Check, X } from 'lucide-react';

/**
 * ComparisonPanel component.
 * Visualizes the side-by-side contrast between Qloo Taste Graph Grounding vs Generic LLM.
 */
export default function ComparisonPanel({ comparison, onClose }) {
  if (!comparison) return null;

  const { qloo_grounded_plan, generic_llm_plan, comparison_summary } = comparison;

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-200/80 p-6 space-y-6">
      <div className="flex items-center justify-between pb-4 border-b border-slate-100">
        <div className="flex items-center space-x-2.5">
          <div className="w-9 h-9 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-slate-800">Why Qloo Taste Graph Matters</h2>
            <p className="text-xs text-slate-500">Side-by-side comparison: Qloo-grounded agent vs ungrounded generic LLM</p>
          </div>
        </div>
        {onClose && (
          <button
            type="button"
            onClick={onClose}
            className="text-xs text-slate-400 hover:text-slate-600 px-2 py-1 rounded"
          >
            Close
          </button>
        )}
      </div>

      {/* Summary Matrix */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Qloo Column */}
        <div className="p-4 rounded-xl bg-teal-50/60 border border-teal-200/80 space-y-3">
          <div className="flex items-center space-x-2 text-teal-900 font-bold text-sm">
            <Sparkles className="w-4 h-4 text-teal-600" />
            <span>Memory Lane (Qloo Graph + Health Rules)</span>
          </div>

          <ul className="text-xs space-y-2 text-teal-950">
            <li className="flex items-start space-x-2">
              <Check className="w-4 h-4 text-teal-600 shrink-0 mt-0.5" />
              <span><strong>Culturally Authentic:</strong> Precise regional matches (e.g. Bhimsen Joshi, Natyasangeet).</span>
            </li>
            <li className="flex items-start space-x-2">
              <Check className="w-4 h-4 text-teal-600 shrink-0 mt-0.5" />
              <span><strong>Zero Hallucinations:</strong> Every song and dish exists in verified Qloo graph nodes.</span>
            </li>
            <li className="flex items-start space-x-2">
              <Check className="w-4 h-4 text-teal-600 shrink-0 mt-0.5" />
              <span><strong>Clinical Guardrails:</strong> Deterministic texture adaptations for dysphagia & diabetic safety.</span>
            </li>
          </ul>

          <div className="mt-4 pt-3 border-t border-teal-200/50 text-[11px] text-teal-800 font-medium">
            Sample Music: {qloo_grounded_plan.music_recommendations?.[0]?.title} ({qloo_grounded_plan.music_recommendations?.[0]?.creator_or_artist})
          </div>
        </div>

        {/* Generic LLM Column */}
        <div className="p-4 rounded-xl bg-rose-50/60 border border-rose-200/80 space-y-3">
          <div className="flex items-center space-x-2 text-rose-900 font-bold text-sm">
            <ShieldAlert className="w-4 h-4 text-rose-600" />
            <span>Generic LLM Only (Ungrounded Baseline)</span>
          </div>

          <ul className="text-xs space-y-2 text-rose-950">
            <li className="flex items-start space-x-2">
              <X className="w-4 h-4 text-rose-500 shrink-0 mt-0.5" />
              <span><strong>Generic Stereotypes:</strong> Defaults to Western pop (Beatles) or unspecific top hits.</span>
            </li>
            <li className="flex items-start space-x-2">
              <X className="w-4 h-4 text-rose-500 shrink-0 mt-0.5" />
              <span><strong>Hallucination Risk:</strong> Attributes songs to wrong eras or fictional soundtracks.</span>
            </li>
            <li className="flex items-start space-x-2">
              <X className="w-4 h-4 text-rose-500 shrink-0 mt-0.5" />
              <span><strong>Safety Hazard:</strong> Suggests crispy or sugary dishes without dysphagia modifications.</span>
            </li>
          </ul>

          <div className="mt-4 pt-3 border-t border-rose-200/50 text-[11px] text-rose-800 font-medium">
            Sample Music: {generic_llm_plan.music_recommendations?.[0]?.title}
          </div>
        </div>
      </div>

      {/* Narrative Breakdown */}
      {comparison_summary && (
        <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/60 text-xs space-y-2 text-slate-700">
          <h4 className="font-semibold text-slate-800">Caregiver Clinical Analysis:</h4>
          <p>{comparison_summary.grounding_differences}</p>
          <p>{comparison_summary.safety_differences}</p>
        </div>
      )}
    </div>
  );
}
