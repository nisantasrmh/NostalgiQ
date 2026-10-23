'use client';

import React from 'react';
import {
  Film,
  Utensils,
  Lightbulb,
  ShieldAlert,
  Sparkles,
} from 'lucide-react';
import { MemoryPlan } from '@/lib/api';
import CaregiverPlaylistSection from './CaregiverPlaylistSection';

interface DashboardProps {
  plan: MemoryPlan;
}

export default function Dashboard({ plan }: DashboardProps) {
  return (
    <div className="space-y-8 mt-10">
      {/* Plan Header Summary */}
      <div className="bg-white/90 backdrop-blur-md rounded-2xl p-6 sm:p-8 border border-stone-200/80 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-bold text-amber-700 uppercase tracking-widest bg-amber-50 px-2.5 py-1 rounded-md border border-amber-200">
            Active Care Plan
          </span>
          <h2 className="text-2xl font-extrabold text-stone-900 mt-2">
            Reminiscence Plan for {plan.persona_name}
          </h2>
          <p className="text-sm text-stone-500 mt-1">
            Grounded through Qloo Taste Graph correlations & clinical nutritional adaptations.
          </p>
        </div>
        <div className="text-left sm:text-right">
          <span className="text-xs text-stone-400 block">Plan ID: {plan.plan_id}</span>
          <span className="text-xs text-stone-400 block mt-0.5">
            Generated: {new Date(plan.created_at).toLocaleDateString()}
          </span>
        </div>
      </div>

      {/* Caregiver Sensory Audio Playlist Section */}
      <CaregiverPlaylistSection
        elderName={plan.persona_name}
        musicRecommendations={plan.music_recommendations || []}
      />

      {/* Film & Visual Prompts */}
      <div className="bg-white/90 backdrop-blur-md rounded-2xl p-6 sm:p-8 border border-stone-200/80 shadow-sm">
        <div className="flex items-center gap-2 pb-5 border-b border-stone-100">
          <span className="p-2 rounded-xl bg-indigo-50 text-indigo-700">
            <Film className="w-5 h-5" />
          </span>
          <div>
            <h3 className="text-lg font-bold text-stone-900">
              Formative Film & Visual Anchors
            </h3>
            <p className="text-xs text-stone-500">
              Cinema, broadcasts, and visual cues from the elder's formative era.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-6">
          {(plan.film_recommendations || []).map((film, idx) => (
            <div
              key={film.id || idx}
              className="p-4 rounded-xl border border-stone-100 bg-stone-50/50 hover:bg-stone-50 transition flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between gap-2">
                  <h4 className="text-sm font-bold text-stone-900">
                    {film.title}
                  </h4>
                  {film.era && (
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-stone-200 text-stone-700 font-medium">
                      {film.era}
                    </span>
                  )}
                </div>
                {film.creator_or_artist && (
                  <p className="text-xs text-stone-500 mt-0.5">
                    Dir: {film.creator_or_artist}
                  </p>
                )}
                <p className="text-xs text-stone-600 mt-2 line-clamp-3">
                  {film.description}
                </p>
              </div>

              {film.reminiscence_connection && (
                <div className="mt-3 pt-2.5 border-t border-stone-200/60">
                  <p className="text-[11px] text-indigo-900/80 italic">
                    "{film.reminiscence_connection}"
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Culinary & Dietary Safe Adaptations */}
      <div className="bg-white/90 backdrop-blur-md rounded-2xl p-6 sm:p-8 border border-stone-200/80 shadow-sm">
        <div className="flex items-center gap-2 pb-5 border-b border-stone-100">
          <span className="p-2 rounded-xl bg-emerald-50 text-emerald-700">
            <Utensils className="w-5 h-5" />
          </span>
          <div>
            <h3 className="text-lg font-bold text-stone-900">
              Comfort Foods & Clinical Dietary Adaptations
            </h3>
            <p className="text-xs text-stone-500">
              Traditional regional flavours adapted safely for texture and chronic conditions.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-6">
          {(plan.meal_recommendations || []).map((meal, idx) => {
            const adapt = meal.health_adaptation;
            return (
              <div
                key={meal.id || idx}
                className="p-4 rounded-xl border border-stone-100 bg-stone-50/50 hover:bg-stone-50 transition flex flex-col justify-between"
              >
                <div>
                  <h4 className="text-sm font-bold text-stone-900">
                    {meal.title}
                  </h4>
                  <p className="text-xs text-stone-600 mt-1.5">
                    {meal.description}
                  </p>

                  {adapt && adapt.is_adapted && (
                    <div className="mt-3 p-2.5 rounded-lg bg-emerald-50/80 border border-emerald-200/70 text-xs">
                      <div className="flex items-center gap-1.5 font-bold text-emerald-800">
                        <ShieldAlert className="w-3.5 h-3.5" />
                        Clinical Modification:
                      </div>
                      <p className="text-emerald-950 mt-1 font-semibold">
                        {adapt.adapted_dish}
                      </p>
                      <p className="text-emerald-800 text-[11px] mt-0.5">
                        {adapt.texture_instructions}
                      </p>
                      {adapt.substitutions?.length > 0 && (
                        <div className="mt-1 flex flex-wrap gap-1">
                          {adapt.substitutions.map((sub, sIdx) => (
                            <span
                              key={sIdx}
                              className="text-[10px] bg-white px-1.5 py-0.5 rounded text-emerald-700 border border-emerald-200"
                            >
                              {sub}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {meal.reminiscence_connection && (
                  <div className="mt-3 pt-2.5 border-t border-stone-200/60">
                    <p className="text-[11px] text-emerald-900/80 italic">
                      "{meal.reminiscence_connection}"
                    </p>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Caregiver Facilitation Tips */}
      {plan.caregiver_tips && plan.caregiver_tips.length > 0 && (
        <div className="bg-gradient-to-r from-amber-50/60 via-stone-50 to-amber-50/40 rounded-2xl p-6 sm:p-8 border border-amber-200/70 shadow-sm">
          <div className="flex items-center gap-2 pb-4 border-b border-amber-200/50">
            <span className="p-2 rounded-xl bg-amber-500/10 text-amber-700">
              <Lightbulb className="w-5 h-5" />
            </span>
            <h3 className="text-lg font-bold text-stone-900">
              Caregiver Delivery & Sensory Guidance
            </h3>
          </div>
          <ul className="mt-5 space-y-2.5">
            {plan.caregiver_tips.map((tip, idx) => (
              <li
                key={idx}
                className="flex items-start gap-2.5 text-xs text-stone-700 font-medium leading-relaxed"
              >
                <Sparkles className="w-3.5 h-3.5 text-amber-600 mt-0.5 shrink-0" />
                <span>{tip}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Baseline Gemini vs NostalgiQ Engine Comparison Section */}
      <div className="mt-8 p-6 bg-slate-900 text-white rounded-xl border border-slate-800 shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-amber-400 flex items-center gap-2">
            ⚡ Baseline Gemini vs NostalgiQ Engine
          </h3>
          <span className="text-xs bg-amber-400/20 text-amber-300 px-3 py-1 rounded-full border border-amber-400/30">
            Qloo Taste AI Intelligence
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Generic LLM Card */}
          <div className="p-4 bg-slate-800/60 rounded-lg border border-slate-700">
            <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
              Standard LLM (Generic Output)
            </div>
            <ul className="text-sm text-slate-300 space-y-2 list-disc list-inside">
              <li>Generates generic top-chart songs from the decade.</li>
              <li>Basic keyword matching for movies and dining.</li>
              <li>No cross-domain affinity analysis.</li>
              <li>Ignores dietary & medical safety constraints.</li>
            </ul>
          </div>

          {/* NostalgiQ Engine Card */}
          <div className="p-4 bg-gradient-to-br from-amber-950/40 to-slate-800 rounded-lg border border-amber-500/40">
            <div className="text-xs font-semibold text-amber-400 uppercase tracking-wider mb-2">
              NostalgiQ (Gemini + Qloo Taste AI)
            </div>
            <ul className="text-sm text-amber-100 space-y-2 list-disc list-inside">
              <li><strong>Cross-Domain Affinities:</strong> Maps 70s rock taste directly to retro dining & classic literature.</li>
              <li><strong>Hyper-Personalized:</strong> Deeper cultural nuances, not just obvious hit lists.</li>
              <li><strong>Safety Adapted:</strong> Auto-filters menus for low-sodium, diabetic, or soft food needs.</li>
              <li><strong>Agentic Reasoning:</strong> Transparent step-by-step logic trail.</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}