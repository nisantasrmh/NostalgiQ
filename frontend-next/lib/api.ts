/**
 * NostalgiQ API Client
 * Interacts with FastAPI backend running on port 8000.
 */

const rawBaseUrl =
  process.env.NEXT_PUBLIC_API_URL || 'https://nostalgiq.onrender.com';
// Strip trailing slash and trailing '/api' if already provided in the env var (e.g. https://service.onrender.com/api)
export const API_BASE_URL = rawBaseUrl.replace(/\/+$/, '').replace(/\/api$/, '');

export interface ElderProfileInput {
  id?: string;
  name: string;
  age: number;
  birth_year: number;
  current_residence: string;
  formative_years_decade: string;
  formative_region: string;
  favorite_genres?: string[];
  health_conditions?: string[];
  primary_language?: string;
}

export interface Recommendation {
  id: string;
  domain: 'music' | 'film' | 'dining';
  title: string;
  creator_or_artist?: string;
  era?: string;
  description: string;
  reminiscence_connection: string;
  confidence_score?: number;
  source?: string;
  health_adaptation?: {
    is_adapted: boolean;
    original_dish: string;
    adapted_dish: string;
    texture_instructions: string;
    substitutions: string[];
    addressed_constraints: string[];
  };
}

export interface MemoryPlan {
  plan_id: string;
  persona_id: string;
  persona_name: string;
  created_at: string;
  music_recommendations: Recommendation[];
  film_recommendations: Recommendation[];
  meal_recommendations: Recommendation[];
  caregiver_tips: string[];
}

export interface PlaylistTrack {
  title: string;
  artist?: string;
  era?: string;
  youtube_url: string;
  spotify_search_url: string;
}

export interface PlaylistExportResponse {
  elder_name: string;
  total_tracks: number;
  tracks: PlaylistTrack[];
}

/**
 * Format raw form inputs into ElderProfile payload required by /api/plan
 */
export function formatProfilePayload(input: ElderProfileInput) {
  return {
    id: input.id || `elder_${Date.now()}`,
    name: input.name,
    age: Number(input.age),
    birth_year: Number(input.birth_year),
    current_residence: input.current_residence,
    formative_years_decade: input.formative_years_decade,
    formative_region: input.formative_region,
    primary_language: input.primary_language || 'English',
    favorites: {
      music_genres: input.favorite_genres || [],
      music_artists: [],
      films_and_shows: [],
      favorite_dishes: [],
    },
    health_constraints: {
      texture_requirement: (input.health_conditions || []).some((c) =>
        c.toLowerCase().includes('dysphagia')
      )
        ? 'soft_food'
        : 'normal',
      dietary_restrictions: (input.health_conditions || []).map((c) => {
        const lower = c.toLowerCase();
        if (lower.includes('diabet')) return 'diabetic_friendly';
        if (lower.includes('sodium') || lower.includes('hypertension')) return 'low_sodium';
        if (lower.includes('cardiac') || lower.includes('heart')) return 'cardiac_friendly';
        return 'diabetic_friendly';
      }),
      allergies: [],
      spiciness_tolerance: 'mild',
    },
  };
}

/**
 * Generate Reminiscence Memory Plan via POST /api/plan
 */
export async function generateMemoryPlan(
  profileData: ElderProfileInput
): Promise<MemoryPlan> {
  const payload = formatProfilePayload(profileData);
  const response = await fetch(`${API_BASE_URL}/api/plan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorJson = await response.json().catch(() => null);
    throw new Error(
      errorJson?.error || `Failed to generate plan (Status: ${response.status})`
    );
  }

  return response.json();
}

/**
 * Export Curated Playlist via POST /api/export-playlist
 * Supports 'json' output or triggers direct browser CSV file download.
 */
export async function exportPlaylist(
  elderName: string,
  musicRecommendations: { title: string; creator_or_artist?: string; era?: string }[],
  format: 'json' | 'csv' = 'json'
): Promise<PlaylistExportResponse | void> {
  const payload = {
    elder_name: elderName,
    music_recommendations: musicRecommendations,
    format,
  };

  const response = await fetch(`${API_BASE_URL}/api/export-playlist`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorJson = await response.json().catch(() => null);
    throw new Error(
      errorJson?.error || `Failed to export playlist (Status: ${response.status})`
    );
  }

  if (format === 'csv') {
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    const sanitized =
      elderName.replace(/[^a-zA-Z0-9_-]/g, '') || 'caregiver';
    link.download = `${sanitized}_playlist.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    return;
  }

  return response.json();
}
