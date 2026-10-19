import React, { useState } from 'react';
import { Smile, Meh, Frown, Bookmark } from 'lucide-react';

/**
 * FeedbackButtons component.
 * Allows caregivers to record the elder's emotional reaction to each recommendation.
 */
export default function FeedbackButtons({ itemId }) {
  const [reaction, setReaction] = useState(null);
  const [saved, setSaved] = useState(false);

  return (
    <div className="mt-3 pt-2.5 border-t border-slate-100 flex flex-wrap items-center justify-between gap-2 text-xs">
      <div className="flex items-center space-x-1.5 text-slate-500">
        <span className="text-[11px] font-medium mr-1">Elder Reaction:</span>
        <button
          type="button"
          onClick={() => setReaction('soothing')}
          className={`flex items-center space-x-1 px-2 py-1 rounded-md transition-all ${
            reaction === 'soothing'
              ? 'bg-emerald-100 text-emerald-800 font-medium'
              : 'hover:bg-slate-100 text-slate-600'
          }`}
          title="Brought smile or positive engagement"
        >
          <Smile className="w-3.5 h-3.5 text-emerald-600" />
          <span className="text-[11px]">Soothing</span>
        </button>

        <button
          type="button"
          onClick={() => setReaction('neutral')}
          className={`flex items-center space-x-1 px-2 py-1 rounded-md transition-all ${
            reaction === 'neutral'
              ? 'bg-amber-100 text-amber-800 font-medium'
              : 'hover:bg-slate-100 text-slate-600'
          }`}
          title="Mild or neutral response"
        >
          <Meh className="w-3.5 h-3.5 text-amber-600" />
          <span className="text-[11px]">Neutral</span>
        </button>

        <button
          type="button"
          onClick={() => setReaction('agitated')}
          className={`flex items-center space-x-1 px-2 py-1 rounded-md transition-all ${
            reaction === 'agitated'
              ? 'bg-rose-100 text-rose-800 font-medium'
              : 'hover:bg-slate-100 text-slate-600'
          }`}
          title="Caused restlessness or sensory discomfort"
        >
          <Frown className="w-3.5 h-3.5 text-rose-600" />
          <span className="text-[11px]">Disliked</span>
        </button>
      </div>

      <button
        type="button"
        onClick={() => setSaved(!saved)}
        className={`flex items-center space-x-1 px-2 py-1 rounded-md border text-[11px] transition-all ${
          saved
            ? 'border-teal-500 bg-teal-50 text-teal-700 font-medium'
            : 'border-slate-200 hover:bg-slate-50 text-slate-600'
        }`}
      >
        <Bookmark className="w-3 h-3" />
        <span>{saved ? 'Saved to Diary' : 'Save'}</span>
      </button>
    </div>
  );
}
