import React, { useState, useEffect } from 'react';
import IntakeForm from '../components/IntakeForm';
import PlanView from '../components/PlanView';
import ComparisonPanel from '../components/ComparisonPanel';
import ReasoningTrail from '../components/ReasoningTrail';
import { Layers, ShieldCheck, HeartHandshake } from 'lucide-react';

const FALLBACK_PERSONAS = [
  {
    id: "persona_sharada_pune",
    name: "Sharada Kulkarni",
    age: 79,
    birth_year: 1947,
    current_residence: "Pune, Maharashtra, India",
    formative_years_decade: "1960s",
    formative_region: "Pune / Deccan Gymkhana, Maharashtra",
    primary_language: "Marathi",
    favorites: {
      music_artists: ["Pandit Bhimsen Joshi", "Lata Mangeshkar", "Sudhir Phadke"],
      films_and_shows: ["Pinjra (1972)", "Jagte Raho (1956)", "Sant Tukaram (1936)"],
      favorite_dishes: ["Puran Poli", "Kande Pohe", "Varan Bhaat with ghee"]
    },
    health_constraints: {
      texture_requirement: "soft_food",
      texture_details: "Mild dysphagia; needs soft fork-tender preparation",
      dietary_restrictions: ["diabetic_friendly", "low_sodium"],
      allergies: ["peanuts"],
      spiciness_tolerance: "mild"
    }
  },
  {
    id: "persona_arthur_chicago",
    name: "Arthur Miller",
    age: 82,
    birth_year: 1944,
    current_residence: "Evanston, Illinois, USA",
    formative_years_decade: "1960s",
    formative_region: "South Side Chicago, Illinois",
    primary_language: "English",
    favorites: {
      music_artists: ["Miles Davis", "Sam Cooke", "Muddy Waters"],
      films_and_shows: ["The Sound of Music (1965)", "In the Heat of the Night (1967)"],
      favorite_dishes: ["Braised pot roast with root vegetables", "Apple pie"]
    },
    health_constraints: {
      texture_requirement: "soft_food",
      texture_details: "Fork-tender meat and softened vegetables",
      dietary_restrictions: ["low_sodium", "cardiac_friendly"],
      allergies: ["shellfish"],
      spiciness_tolerance: "mild"
    }
  }
];

const rawBaseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_BASE_URL = rawBaseUrl.replace(/\/+$/, '').replace(/\/api$/, '');

export default function Home() {
  const [personas, setPersonas] = useState(FALLBACK_PERSONAS);
  const [selectedPersona, setSelectedPersona] = useState(FALLBACK_PERSONAS[0]);
  const [plan, setPlan] = useState(null);
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(false);
  const [comparing, setComparing] = useState(false);
  const [error, setError] = useState(null);

  // Fetch personas from backend on mount
  useEffect(() => {
    fetch(`${API_BASE_URL}/api/personas`)
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data && data.length > 0) {
          setPersonas(data);
          setSelectedPersona(data[0]);
        }
      })
      .catch(() => {
        // Use fallback personas if backend is not yet started
      });
  }, []);

  const handleGeneratePlan = async () => {
    if (!selectedPersona) return;
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/api/plan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(selectedPersona),
      });
      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.error || 'Backend plan generation failed.');
      }
      const data = await response.json();
      setPlan(data);
    } catch (err) {
      setError(err.message || `Could not connect to backend at ${API_BASE_URL}. Ensure backend is running.`);
    } finally {
      setLoading(false);
    }
  };

  const handleCompare = async () => {
    if (!selectedPersona) return;
    setComparing(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/api/compare`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(selectedPersona),
      });
      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.error || 'Backend comparison failed.');
      }
      const data = await response.json();
      setComparison(data);
      if (data.qloo_grounded_plan) {
        setPlan(data.qloo_grounded_plan);
      }
    } catch (err) {
      setError(err.message || 'Could not connect to backend for comparison.');
    } finally {
      setComparing(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      {/* Top Navigation */}
      <header className="bg-white border-b border-slate-200/80 sticky top-0 z-20">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-xl bg-teal-600 text-white flex items-center justify-center shadow-sm">
              <HeartHandshake className="w-5 h-5" />
            </div>
            <div>
              <span className="font-bold text-slate-800 text-base">NostalgiQ</span>
              <span className="hidden sm:inline-block ml-2 text-xs text-teal-700 bg-teal-50 px-2 py-0.5 rounded-full font-medium">
                Powered by Qloo Taste Graph
              </span>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              type="button"
              onClick={handleCompare}
              disabled={comparing || !selectedPersona}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg border border-purple-200 bg-purple-50 hover:bg-purple-100 text-purple-700 text-xs font-medium transition-colors"
            >
              <Layers className="w-3.5 h-3.5" />
              <span>{comparing ? 'Evaluating...' : 'Why Qloo? Compare'}</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="max-w-6xl mx-auto px-4 sm:px-6 py-8 flex-1 w-full space-y-6">
        {error && (
          <div className="p-3.5 rounded-xl bg-amber-50 border border-amber-200 text-amber-800 text-xs flex items-center justify-between">
            <span>{error}</span>
            <button onClick={() => setError(null)} className="text-amber-900 font-bold ml-2">×</button>
          </div>
        )}

        {/* Comparison Modal / Panel */}
        {comparison && (
          <ComparisonPanel
            comparison={comparison}
            onClose={() => setComparison(null)}
          />
        )}

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Left Column: Intake & Persona Selection */}
          <div className="lg:col-span-5 space-y-6">
            <IntakeForm
              personas={personas}
              selectedPersona={selectedPersona}
              onSelectPersona={(p) => {
                setSelectedPersona(p);
                setPlan(null);
                setComparison(null);
              }}
              onSubmit={handleGeneratePlan}
              loading={loading}
            />

            {/* Audit Trail */}
            {plan?.reasoning_trail && (
              <ReasoningTrail steps={plan.reasoning_trail} />
            )}
          </div>

          {/* Right Column: Memory Plan View */}
          <div className="lg:col-span-7">
            <PlanView plan={plan} />
          </div>
        </div>
      </main>

      {/* Footer & Medical Disclaimer */}
      <footer className="border-t border-slate-200 bg-white py-6">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 text-center text-xs text-slate-500 space-y-2">
          <div className="flex items-center justify-center space-x-1 text-slate-600">
            <ShieldCheck className="w-4 h-4 text-teal-600" />
            <span className="font-semibold">Caregiver Supportive Aid Disclaimer</span>
          </div>
          <p className="max-w-2xl mx-auto text-[11px] text-slate-400">
            NostalgiQ provides cultural reminiscence and culinary lifestyle ideas for caregivers.
            It is not a diagnostic device or clinical medical treatment. Always consult speech therapists and physicians
            for clinical dysphagia and medical dietary regimens.
          </p>
          <div className="text-[10px] text-slate-400">
            Powered by Qloo Taste Graph (Mock Mode Active) • NostalgiQ Hackathon Edition
          </div>
        </div>
      </footer>
    </div>
  );
}
