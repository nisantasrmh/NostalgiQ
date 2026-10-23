import React from 'react';
import { User, Heart, Sparkles, ShieldCheck } from 'lucide-react';

/**
 * IntakeForm component.
 * Allows caregivers to select a demo persona or configure custom elder parameters.
 */
export default function IntakeForm({
  personas = [],
  selectedPersona,
  onSelectPersona,
  onSubmit,
  loading,
}) {
  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-200/80 p-6">
      <div className="flex items-center justify-between pb-4 border-b border-slate-100">
        <div className="flex items-center space-x-2.5">
          <div className="w-9 h-9 rounded-xl bg-teal-50 flex items-center justify-center text-teal-600">
            <User className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-slate-800">Elder Profile & Preferences</h2>
            <p className="text-xs text-slate-500">Select a pre-configured persona or review health guidelines</p>
          </div>
        </div>
        <span className="text-xs font-medium px-2.5 py-1 rounded-full bg-slate-100 text-slate-600">
          Step 1 of 3
        </span>
      </div>

      {/* Preset Persona Selector */}
      <div className="mt-5">
        <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">
          Demo Persona Presets
        </label>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {personas.map((p) => {
            const isSelected = selectedPersona?.id === p.id;
            return (
              <button
                key={p.id}
                type="button"
                onClick={() => onSelectPersona(p)}
                className={`text-left p-3.5 rounded-xl border transition-all ${
                  isSelected
                    ? 'border-teal-500 bg-teal-50/50 ring-2 ring-teal-500/20'
                    : 'border-slate-200 hover:border-slate-300 bg-white'
                }`}
              >
                <div className="flex justify-between items-start">
                  <span className="font-semibold text-sm text-slate-800">{p.name}</span>
                  <span className="text-xs text-teal-700 font-medium bg-teal-100/70 px-2 py-0.5 rounded-md">
                    {p.age} yrs
                  </span>
                </div>
                <p className="text-xs text-slate-600 mt-1 line-clamp-1">{p.formative_region}</p>
                <div className="flex items-center gap-1.5 mt-2.5">
                  <span className="text-[11px] bg-slate-100 text-slate-600 px-2 py-0.5 rounded">
                    Era: {p.formative_years_decade}
                  </span>
                  <span className="text-[11px] bg-amber-50 text-amber-700 px-2 py-0.5 rounded border border-amber-200/50">
                    {p.health_constraints?.texture_requirement?.replace('_', ' ')}
                  </span>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Current Persona Summary Card */}
      {selectedPersona && (
        <div className="mt-5 p-4 rounded-xl bg-slate-50 border border-slate-200/60 text-xs space-y-2.5">
          <div className="flex items-center justify-between text-slate-700">
            <span className="font-medium text-slate-500">Cultural Anchors:</span>
            <span className="font-semibold text-slate-800">
              {selectedPersona.favorites?.music_artists?.slice(0, 2).join(', ')}
            </span>
          </div>
          <div className="flex items-center justify-between text-slate-700">
            <span className="font-medium text-slate-500">Formative Region:</span>
            <span className="text-slate-800">{selectedPersona.formative_region}</span>
          </div>
          <div className="flex items-start justify-between text-slate-700 gap-2">
            <span className="font-medium text-slate-500 shrink-0">Health Guardrails:</span>
            <div className="flex flex-wrap justify-end gap-1">
              {selectedPersona.health_constraints?.dietary_restrictions?.map((r, i) => (
                <span key={i} className="bg-emerald-50 text-emerald-700 border border-emerald-200/60 px-1.5 py-0.5 rounded text-[10px]">
                  {r.replace('_', ' ')}
                </span>
              ))}
              {selectedPersona.health_constraints?.allergies?.map((a, i) => (
                <span key={i} className="bg-rose-50 text-rose-700 border border-rose-200/60 px-1.5 py-0.5 rounded text-[10px]">
                  No {a}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Action Button */}
      <div className="mt-6">
        <button
          type="button"
          onClick={onSubmit}
          disabled={loading || !selectedPersona}
          className="w-full py-3 px-4 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-medium text-sm transition-colors flex items-center justify-center space-x-2 shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <>
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              <span>Querying Qloo Taste Graph & Health Rules...</span>
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" />
              <span>Generate NostalgiQ Plan</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}
