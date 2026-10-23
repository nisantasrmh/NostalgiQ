'use client';

import React, { useState } from 'react';
import {
  Music,
  Download,
  ExternalLink,
  Video,
  Radio,
  FileCode,
  Check,
} from 'lucide-react';
import { exportPlaylist, Recommendation } from '@/lib/api';

interface CaregiverPlaylistSectionProps {
  elderName: string;
  musicRecommendations: Recommendation[];
}

export default function CaregiverPlaylistSection({
  elderName,
  musicRecommendations,
}: CaregiverPlaylistSectionProps) {
  const [downloadingCsv, setDownloadingCsv] = useState(false);
  const [exportingJson, setExportingJson] = useState(false);
  const [jsonExportSuccess, setJsonExportSuccess] = useState(false);

  const tracksForExport = musicRecommendations.map((r) => ({
    title: r.title,
    creator_or_artist: r.creator_or_artist,
    era: r.era,
  }));

  const handleDownloadCsv = async () => {
    try {
      setDownloadingCsv(true);
      await exportPlaylist(elderName, tracksForExport, 'csv');
    } catch (err: any) {
      alert(err.message || 'Failed to download CSV playlist.');
    } finally {
      setDownloadingCsv(false);
    }
  };

  const handleExportJson = async () => {
    try {
      setExportingJson(true);
      const res = await exportPlaylist(elderName, tracksForExport, 'json');
      if (res) {
        // Trigger client download of JSON format
        const blob = new Blob([JSON.stringify(res, null, 2)], {
          type: 'application/json',
        });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        const sanitized =
          elderName.replace(/[^a-zA-Z0-9_-]/g, '') || 'caregiver';
        link.download = `${sanitized}_playlist.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        setJsonExportSuccess(true);
        setTimeout(() => setJsonExportSuccess(false), 3000);
      }
    } catch (err: any) {
      alert(err.message || 'Failed to export JSON playlist.');
    } finally {
      setExportingJson(false);
    }
  };

  return (
    <div className="bg-gradient-to-br from-amber-50 to-orange-50/40 rounded-2xl p-6 sm:p-8 border border-amber-200/80 shadow-sm mt-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-6 border-b border-amber-200/60 gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-2 rounded-xl bg-amber-500/10 text-amber-700">
              <Music className="w-5 h-5" />
            </span>
            <h3 className="text-xl font-bold text-amber-950">
              Caregiver Sensory Audio Playlist
            </h3>
          </div>
          <p className="text-sm text-stone-600 mt-1">
            Grounded musical cues tailored for {elderName}. One-click links for direct streaming or caregiver archives.
          </p>
        </div>

        <div className="flex items-center gap-2.5 flex-wrap">
          <button
            onClick={handleExportJson}
            disabled={exportingJson || musicRecommendations.length === 0}
            className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl bg-white hover:bg-stone-50 border border-stone-200 text-stone-700 font-medium text-xs shadow-sm transition disabled:opacity-50"
          >
            {jsonExportSuccess ? (
              <Check className="w-3.5 h-3.5 text-emerald-600" />
            ) : (
              <FileCode className="w-3.5 h-3.5 text-stone-500" />
            )}
            {exportingJson ? 'Exporting...' : 'Export JSON'}
          </button>

          <button
            onClick={handleDownloadCsv}
            disabled={downloadingCsv || musicRecommendations.length === 0}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-amber-600 hover:bg-amber-700 text-white font-semibold text-xs shadow-sm hover:shadow transition disabled:opacity-50"
          >
            <Download className="w-3.5 h-3.5" />
            {downloadingCsv ? 'Downloading...' : 'Download CSV Playlist'}
          </button>
        </div>
      </div>

      <div className="mt-6 divide-y divide-amber-100">
        {musicRecommendations.length === 0 ? (
          <p className="text-sm text-stone-500 italic py-4">
            No music recommendations currently available in this plan.
          </p>
        ) : (
          musicRecommendations.map((track, idx) => {
            const query = encodeURIComponent(
              `${track.title} ${track.creator_or_artist || ''}`.trim()
            );
            const youtubeUrl = `https://www.youtube.com/results?search_query=${query}`;
            const spotifyUrl = `https://open.spotify.com/search/${query}`;

            return (
              <div
                key={track.id || idx}
                className="py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 group"
              >
                <div className="pr-4">
                  <div className="flex items-baseline gap-2">
                    <span className="text-xs font-semibold text-amber-700">
                      #{idx + 1}
                    </span>
                    <h4 className="text-base font-bold text-stone-900">
                      {track.title}
                    </h4>
                    {track.era && (
                      <span className="text-[11px] px-2 py-0.5 rounded-md bg-stone-100 text-stone-600 font-medium">
                        {track.era}
                      </span>
                    )}
                  </div>
                  {track.creator_or_artist && (
                    <p className="text-xs text-stone-600 font-medium mt-0.5">
                      by {track.creator_or_artist}
                    </p>
                  )}
                  {track.reminiscence_connection && (
                    <p className="text-xs text-amber-900/80 mt-1 italic">
                      "{track.reminiscence_connection}"
                    </p>
                  )}
                </div>

                <div className="flex items-center gap-2 self-start sm:self-center shrink-0">
                  <a
                    href={youtubeUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-red-50 hover:bg-red-100 text-red-700 font-medium text-xs border border-red-200/60 transition"
                  >
                    <Video className="w-3.5 h-3.5 text-red-600" />
                    <span>YouTube</span>
                    <ExternalLink className="w-2.5 h-2.5 opacity-60" />
                  </a>

                  <a
                    href={spotifyUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-50 hover:bg-emerald-100 text-emerald-800 font-medium text-xs border border-emerald-200/60 transition"
                  >
                    <Radio className="w-3.5 h-3.5 text-emerald-600" />
                    <span>Spotify</span>
                    <ExternalLink className="w-2.5 h-2.5 opacity-60" />
                  </a>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
