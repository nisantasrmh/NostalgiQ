"""Tests for playlist export endpoint."""

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_export_playlist_json():
    payload = {
        "elder_name": "Aaji",
        "music_recommendations": [
            {
                "title": "Ghei Chhand Makarand",
                "creator_or_artist": "Vasantrao Deshpande",
                "era": "1960s",
            },
            {
                "title": "Ketakichya Banaat",
                "creator_or_artist": "Suman Kalyanpur",
            },
        ],
        "format": "json",
    }
    response = client.post("/api/export-playlist", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["elder_name"] == "Aaji"
    assert data["total_tracks"] == 2
    assert len(data["tracks"]) == 2
    first = data["tracks"][0]
    assert first["title"] == "Ghei Chhand Makarand"
    assert first["artist"] == "Vasantrao Deshpande"
    assert "youtube.com" in first["youtube_url"]
    assert "spotify.com" in first["spotify_search_url"]


def test_export_playlist_csv():
    payload = {
        "elder_name": "Sharada Devi",
        "music_recommendations": [
            {
                "title": "Albela Sajan Aayo Ri",
                "creator_or_artist": "Ustad Amir Khan",
                "era": "1950s",
            }
        ],
        "format": "csv",
    }
    response = client.post("/api/export-playlist", json=payload)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert 'filename="SharadaDevi_playlist.csv"' in response.headers["content-disposition"]
    csv_text = response.text
    assert "Title,Artist,Era,YouTube URL,Spotify Search URL" in csv_text
    assert "Albela Sajan Aayo Ri" in csv_text
    assert "Ustad Amir Khan" in csv_text


def test_export_playlist_invalid_format():
    payload = {
        "elder_name": "Test",
        "music_recommendations": [],
        "format": "xml",
    }
    response = client.post("/api/export-playlist", json=payload)
    assert response.status_code == 400
    assert "Unsupported format" in response.json()["error"]
