import React, { useState } from 'react';
import { Music, Film, Utensils, Heart, Info, CheckCircle2, AlertCircle } from 'lucide-react';
import FeedbackButtons from './FeedbackButtons';

/**
 * PlanView component.
 * Displays the synthesized reminiscence plan across Music, Film/TV, and Culinary Comforts.
 */
export default function PlanView({ plan }) {
  const [activeTab, setActiveTab] = useState('music');

  if (!plan) {
    return (
      <div className="bg-white rounded-2xl border border-dashed border-slate-200 p-12 text-center text-slate-400">
        <Heart className="w-10 h-10 mx-auto text-slate-300 stroke-[1.5] mb-3" />
        <p className="text-sm font-medium">Select a persona and click "Generate NostalgiQ Plan"</p>
        <p className="text-xs text-slate-400 mt-1">Grounded cultural recommendations will appear here.</p>
      </div>
    );
  }

  const tabs = [
    { id: 'music', label: 'Music Therapy', icon: Music, count: plan.music_recommendations?.length || 0 },
    { id: 'film', label: 'Classic Cinema', icon: Film, count: plan.film_recommendations?.length || 0 },
    { id: 'dining', label: 'Culinary Comforts', icon: Utensils, count: plan.meal_recommendations?.length || 0 },
  ];

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-200/80 overflow-hidden">
      {/* Header */}
      <div className="p-6 bg-gradient-to-r from-teal-700 to-teal-900 text-white">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xs font-semibold uppercase tracking-wider text-teal-200">
                Reminiscence Care Plan
              </span>
              <span className="text-[10px] bg-amber-400/20 text-amber-200 border border-amber-400/30 px-2 py-0.5 rounded-full font-mono">
                source: MOCK data
              </span>
            </div>
            <h2 className="text-xl font-bold mt-1">Prepared for {plan.persona_name}</h2>
          </div>
          <div className="text-right text-xs text-teal-100">
            <div>Plan ID: <span className="font-mono">{plan.plan_id}</span></div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex space-x-2 mt-6">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-white text-teal-900 shadow-sm'
                    : 'text-teal-100 hover:bg-teal-800/60'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
                <span className={`text-[10px] px-1.5 py-0.2 rounded-full ${isActive ? 'bg-teal-100 text-teal-800' : 'bg-teal-800 text-teal-200'}`}>
                  {tab.count}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Tab Content */}
      <div className="p-6 space-y-4">
        {activeTab === 'music' && (
          <div className="space-y-3">
            {plan.music_recommendations?.map((item) => (
              <div key={item.id} className="p-4 rounded-xl border border-slate-200/80 hover:border-teal-200 transition-all bg-white">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-semibold text-slate-800 text-sm">{item.title}</h3>
                    <p className="text-xs text-teal-700 font-medium">{item.creator_or_artist} {item.era && `• ${item.era}`}</p>
                  </div>
                  <span className="text-[10px] font-mono bg-slate-100 text-slate-600 px-2 py-0.5 rounded border border-slate-200">
                    {item.source}
                  </span>
                </div>
                <p className="text-xs text-slate-600 mt-2">{item.description}</p>
                <div className="mt-3 p-2.5 rounded-lg bg-teal-50/60 border border-teal-100 text-[11px] text-teal-900 flex items-start space-x-2">
                  <Info className="w-3.5 h-3.5 text-teal-600 shrink-0 mt-0.5" />
                  <div>
                    <span className="font-semibold">Nostalgic Connection: </span>
                    {item.reminiscence_connection}
                  </div>
                </div>
                <FeedbackButtons itemId={item.id} />
              </div>
            ))}
          </div>
        )}

        {activeTab === 'film' && (
          <div className="space-y-3">
            {plan.film_recommendations?.map((item) => (
              <div key={item.id} className="p-4 rounded-xl border border-slate-200/80 hover:border-teal-200 transition-all bg-white">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-semibold text-slate-800 text-sm">{item.title}</h3>
                    <p className="text-xs text-teal-700 font-medium">{item.creator_or_artist} {item.era && `• ${item.era}`}</p>
                  </div>
                  <span className="text-[10px] font-mono bg-slate-100 text-slate-600 px-2 py-0.5 rounded border border-slate-200">
                    {item.source}
                  </span>
                </div>
                <p className="text-xs text-slate-600 mt-2">{item.description}</p>
                <div className="mt-3 p-2.5 rounded-lg bg-teal-50/60 border border-teal-100 text-[11px] text-teal-900 flex items-start space-x-2">
                  <Info className="w-3.5 h-3.5 text-teal-600 shrink-0 mt-0.5" />
                  <div>
                    <span className="font-semibold">Nostalgic Connection: </span>
                    {item.reminiscence_connection}
                  </div>
                </div>
                <FeedbackButtons itemId={item.id} />
              </div>
            ))}
          </div>
        )}

        {activeTab === 'dining' && (
          <div className="space-y-4">
            {plan.meal_recommendations?.map((item) => (
              <div key={item.id} className="p-4 rounded-xl border border-slate-200/80 hover:border-teal-200 transition-all bg-white">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-semibold text-slate-800 text-sm">{item.title}</h3>
                    <p className="text-xs text-teal-700 font-medium">{item.creator_or_artist} {item.era && `• ${item.era}`}</p>
                  </div>
                  <span className="text-[10px] font-mono bg-slate-100 text-slate-600 px-2 py-0.5 rounded border border-slate-200">
                    {item.source}
                  </span>
                </div>

                <p className="text-xs text-slate-600 mt-2">{item.description}</p>

                {/* Health Adaptation Box */}
                {item.health_adaptation && item.health_adaptation.is_adapted && (
                  <div className="mt-3 p-3 rounded-xl bg-amber-50/70 border border-amber-200/70 space-y-2 text-xs">
                    <div className="flex items-center space-x-1.5 font-semibold text-amber-900">
                      <AlertCircle className="w-3.5 h-3.5 text-amber-600" />
                      <span>Clinical Dietary Adaptation Applied</span>
                    </div>
                    <div className="text-[11px] text-amber-800">
                      <span className="font-medium">Texture Guidelines: </span>
                      {item.health_adaptation.texture_instructions}
                    </div>
                    {item.health_adaptation.substitutions?.length > 0 && (
                      <div className="text-[11px] text-amber-800">
                        <span className="font-medium">Safe Substitutions: </span>
                        <ul className="list-disc list-inside mt-0.5 space-y-0.5">
                          {item.health_adaptation.substitutions.map((sub, sIdx) => (
                            <li key={sIdx}>{sub}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}

                <FeedbackButtons itemId={item.id} />
              </div>
            ))}
          </div>
        )}

        {/* Caregiver Guidance Section */}
        {plan.caregiver_tips?.length > 0 && (
          <div className="mt-6 pt-4 border-t border-slate-100">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-700 mb-2.5">
              Caregiver Presentation Guidance
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs text-slate-600">
              {plan.caregiver_tips.map((tip, idx) => (
                <div key={idx} className="flex items-start space-x-2 p-2.5 rounded-lg bg-slate-50 border border-slate-100">
                  <CheckCircle2 className="w-3.5 h-3.5 text-teal-600 shrink-0 mt-0.5" />
                  <span>{tip}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
