'use client';

import React, { useState } from 'react';
import { HeartHandshake, Sparkles, Layers, ShieldCheck, AlertCircle } from 'lucide-react';
import IntakeForm from '@/components/IntakeForm';
import Dashboard from '@/components/Dashboard';
import { ElderProfileInput, generateMemoryPlan, MemoryPlan } from '@/lib/api';

export default function Home() {
  const [plan, setPlan] = useState<MemoryPlan | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleGeneratePlan = async (profileData: ElderProfileInput) => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const generatedPlan = await generateMemoryPlan(profileData);
      setPlan(generatedPlan);
    } catch (err: any) {
      setErrorMessage(
        err.message ||
          'Failed to connect to FastAPI backend at http://localhost:8000. Ensure backend is running.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-[#fbf9f5] text-stone-800 pb-16 selection:bg-amber-100">
      {/* Top Navbar */}
      <header className="border-b border-amber-200/60 bg-white/70 backdrop-blur-md sticky top-0 z-20">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <span className="p-2 rounded-xl bg-amber-600 text-white shadow-sm shadow-amber-600/20">
              <HeartHandshake className="w-5 h-5" />
            </span>
            <div>
              <h1 className="text-lg font-extrabold tracking-tight text-amber-950 flex items-center gap-1.5">
                NostalgiQ
                <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 border border-amber-200">
                  The Nostalgia Graph
                </span>
              </h1>
              <p className="text-[11px] text-stone-500 font-medium">
                Powered by Qloo Taste Graph
              </p>
            </div>
          </div>

          <div className="hidden sm:flex items-center gap-4 text-xs font-semibold text-stone-600">
            <span className="flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5 text-amber-600" />
              Qloo Taste Graph
            </span>
            <span className="flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
              Clinical Adaptation
            </span>
          </div>
        </div>
      </header>

      {/* Main Content Container */}
      <div className="max-w-6xl mx-auto px-4 sm:px-6 pt-8 sm:pt-10">
        {/* Hero Title */}
        <div className="mb-8 max-w-2xl">
          <h2 className="text-3xl sm:text-4xl font-extrabold text-stone-900 tracking-tight leading-tight">
            Personalized Reminiscence Therapy for Loved Ones.
          </h2>
          <p className="mt-2.5 text-sm sm:text-base text-stone-600 leading-relaxed font-normal">
            Ground musical, cinematic, and culinary memories in authentic cultural roots, safely adapted for dysphagia and chronic dietary needs.
          </p>
        </div>

        {/* Error Banner */}
        {errorMessage && (
          <div className="mb-8 p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 flex items-start gap-3 text-sm">
            <AlertCircle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold">Backend Connection Notice</p>
              <p className="text-xs text-rose-700 mt-0.5">{errorMessage}</p>
            </div>
          </div>
        )}

        {/* Intake Form */}
        <IntakeForm onSubmit={handleGeneratePlan} isLoading={isLoading} />

        {/* Generated Care Plan & Playlist Dashboard */}
        {plan && <Dashboard plan={plan} />}
      </div>
    </main>
  );
}
