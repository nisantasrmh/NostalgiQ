'use client';

import React, { useState } from 'react';
import { User, Calendar, MapPin, Sparkles, AlertCircle, HeartPulse } from 'lucide-react';
import { ElderProfileInput } from '@/lib/api';

interface IntakeFormProps {
  onSubmit: (data: ElderProfileInput) => void;
  isLoading: boolean;
}

export default function IntakeForm({ onSubmit, isLoading }: IntakeFormProps) {
  const [formData, setFormData] = useState<ElderProfileInput>({
    name: 'Aaji',
    age: 75,
    birth_year: 1948,
    current_residence: 'Pune, Maharashtra, India',
    formative_years_decade: '1960s',
    formative_region: 'Pune, Maharashtra, India',
    favorite_genres: ['Hindustani Classical', 'Natyasangeet'],
    health_conditions: ['Dysphagia', 'Diabetes'],
  });

  const [genresInput, setGenresInput] = useState('Hindustani Classical, Natyasangeet');
  const [healthInput, setHealthInput] = useState('Dysphagia, Diabetes');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'age' || name === 'birth_year' ? Number(value) : value,
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const parsedGenres = genresInput
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean);
    const parsedHealth = healthInput
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean);

    onSubmit({
      ...formData,
      favorite_genres: parsedGenres,
      health_conditions: parsedHealth,
    });
  };

  const loadPreset = (preset: 'aaji' | 'arthur') => {
    if (preset === 'aaji') {
      setFormData({
        name: 'Aaji (Sharada)',
        age: 78,
        birth_year: 1948,
        current_residence: 'Pune, Maharashtra, India',
        formative_years_decade: '1960s',
        formative_region: 'Pune, Maharashtra, India',
        favorite_genres: ['Hindustani Classical', 'Natyasangeet'],
        health_conditions: ['Dysphagia', 'Diabetes'],
      });
      setGenresInput('Hindustani Classical, Natyasangeet');
      setHealthInput('Dysphagia, Diabetes');
    } else {
      setFormData({
        name: 'Arthur Miller',
        age: 82,
        birth_year: 1944,
        current_residence: 'Evanston, Illinois, USA',
        formative_years_decade: '1960s',
        formative_region: 'South Side Chicago, Illinois',
        favorite_genres: ['Chicago Blues', 'Soul Jazz'],
        health_conditions: ['Low Sodium', 'Cardiac Friendly'],
      });
      setGenresInput('Chicago Blues, Soul Jazz');
      setHealthInput('Low Sodium, Cardiac Friendly');
    }
  };

  return (
    <div className="bg-white/90 backdrop-blur-md rounded-2xl p-6 sm:p-8 shadow-sm border border-amber-100">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-6 border-b border-amber-100 gap-4">
        <div>
          <h2 className="text-xl font-bold text-amber-950 flex items-center gap-2">
            <User className="w-5 h-5 text-amber-600" />
            Elder Profile & Preferences
          </h2>
          <p className="text-sm text-stone-500 mt-0.5">
            Personalize cultural taste anchors and clinical safety adaptations.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-stone-500 uppercase tracking-wider">Presets:</span>
          <button
            type="button"
            onClick={() => loadPreset('aaji')}
            className="text-xs px-2.5 py-1.5 rounded-lg bg-amber-50 hover:bg-amber-100 text-amber-800 font-medium border border-amber-200 transition-colors"
          >
            Aaji (Pune)
          </button>
          <button
            type="button"
            onClick={() => loadPreset('arthur')}
            className="text-xs px-2.5 py-1.5 rounded-lg bg-stone-100 hover:bg-stone-200 text-stone-800 font-medium border border-stone-200 transition-colors"
          >
            Arthur (Chicago)
          </button>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="mt-6 space-y-6">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="sm:col-span-1">
            <label className="block text-xs font-bold uppercase tracking-wider text-stone-600 mb-1.5">
              Full Name / Nickname
            </label>
            <input
              type="text"
              name="name"
              required
              value={formData.name}
              onChange={handleChange}
              placeholder="e.g. Aaji"
              className="w-full px-3.5 py-2.5 rounded-xl border border-stone-200 bg-stone-50/50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-amber-500/20 focus:border-amber-500 text-stone-900 text-sm font-medium transition"
            />
          </div>
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-stone-600 mb-1.5">
              Age
            </label>
            <input
              type="number"
              name="age"
              required
              value={formData.age}
              onChange={handleChange}
              className="w-full px-3.5 py-2.5 rounded-xl border border-stone-200 bg-stone-50/50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-amber-500/20 focus:border-amber-500 text-stone-900 text-sm font-medium transition"
            />
          </div>
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-stone-600 mb-1.5">
              Birth Year
            </label>
            <input
              type="number"
              name="birth_year"
              required
              value={formData.birth_year}
              onChange={handleChange}
              className="w-full px-3.5 py-2.5 rounded-xl border border-stone-200 bg-stone-50/50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-amber-500/20 focus:border-amber-500 text-stone-900 text-sm font-medium transition"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-stone-600 mb-1.5 flex items-center gap-1">
              <Calendar className="w-3.5 h-3.5 text-stone-400" /> Formative Decade
            </label>
            <select
              name="formative_years_decade"
              value={formData.formative_years_decade}
              onChange={handleChange}
              className="w-full px-3.5 py-2.5 rounded-xl border border-stone-200 bg-stone-50/50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-amber-500/20 focus:border-amber-500 text-stone-900 text-sm font-medium transition"
            >
              <option value="1950s">1950s</option>
              <option value="1960s">1960s</option>
              <option value="1970s">1970s</option>
              <option value="1980s">1980s</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-stone-600 mb-1.5 flex items-center gap-1">
              <MapPin className="w-3.5 h-3.5 text-stone-400" /> Formative Youth Region
            </label>
            <input
              type="text"
              name="formative_region"
              required
              value={formData.formative_region}
              onChange={handleChange}
              placeholder="e.g. Pune, Maharashtra, India"
              className="w-full px-3.5 py-2.5 rounded-xl border border-stone-200 bg-stone-50/50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-amber-500/20 focus:border-amber-500 text-stone-900 text-sm font-medium transition"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-bold uppercase tracking-wider text-stone-600 mb-1.5 flex items-center gap-1">
            <MapPin className="w-3.5 h-3.5 text-stone-400" /> Current Residence
          </label>
          <input
            type="text"
            name="current_residence"
            required
            value={formData.current_residence}
            onChange={handleChange}
            placeholder="e.g. Pune, Maharashtra, India"
            className="w-full px-3.5 py-2.5 rounded-xl border border-stone-200 bg-stone-50/50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-amber-500/20 focus:border-amber-500 text-stone-900 text-sm font-medium transition"
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-stone-600 mb-1.5 flex items-center gap-1">
              <Sparkles className="w-3.5 h-3.5 text-amber-500" /> Favorite Music Genres / Anchors
            </label>
            <input
              type="text"
              value={genresInput}
              onChange={(e) => setGenresInput(e.target.value)}
              placeholder="Comma separated: Hindustani Classical, Natyasangeet"
              className="w-full px-3.5 py-2.5 rounded-xl border border-stone-200 bg-stone-50/50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-amber-500/20 focus:border-amber-500 text-stone-900 text-sm font-medium transition"
            />
            <p className="text-[11px] text-stone-400 mt-1">Separate with commas</p>
          </div>
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-stone-600 mb-1.5 flex items-center gap-1">
              <HeartPulse className="w-3.5 h-3.5 text-rose-500" /> Health Conditions & Texture Needs
            </label>
            <input
              type="text"
              value={healthInput}
              onChange={(e) => setHealthInput(e.target.value)}
              placeholder="e.g. Dysphagia, Diabetes, Low Sodium"
              className="w-full px-3.5 py-2.5 rounded-xl border border-stone-200 bg-stone-50/50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-amber-500/20 focus:border-amber-500 text-stone-900 text-sm font-medium transition"
            />
            <p className="text-[11px] text-stone-400 mt-1">
              Dietary adaptations will automatically adjust meals safely.
            </p>
          </div>
        </div>

        <div className="pt-2">
          <button
            type="submit"
            disabled={isLoading}
            className="w-full sm:w-auto px-6 py-3 rounded-xl bg-amber-600 hover:bg-amber-700 text-white font-semibold text-sm shadow-md hover:shadow-lg transition-all duration-200 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Synthesizing Grounded Care Plan...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                Generate Reminiscence Plan
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
