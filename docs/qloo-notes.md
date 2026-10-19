# Qloo API Notes & Reference Documentation

> **Status:** Pending Official API Key & Full Specification  
> **Target:** Replace Mock Qloo Adapter with production endpoints once keys/docs are granted.

---

## 1. Authentication & Base URL
- **Base URL:** `https://api.qloo.com/v1` (to be confirmed from official docs)
- **Header:** `X-Api-Key: <QLOO_API_KEY>` or `Authorization: Bearer <QLOO_API_KEY>`
- **Rate Limits:** TBD

---

## 2. Key Entities & Domains
Qloo maps cultural taste cross-domain. Key domains relevant for dementia reminiscence:
- **Music:** Tracks, albums, artists, genres, eras
- **Film & TV:** Movies, TV shows, directors, actors, release years
- **Dining / Food:** Cuisines, traditional dishes, restaurant profiles, culinary traditions
- **Books / Literature (Optional future expansion):** Authors, classic works

---

## 3. Endpoints to Document
*Fill these in once official Qloo docs are reviewed:*

### Entity Search
- **Endpoint:** `GET /search` or `POST /entity/search`
- **Query Params / Payload:**
  ```json
  {
    "query": "Lata Mangeshkar",
    "types": ["music_artist"]
  }
  ```
- **Response Format:**
  ```json
  {
    "results": []
  }
  ```

### Cross-Domain Recommendations / Taste Graph Traversal
- **Endpoint:** `GET /recommendations` or `POST /correlations`
- **Query Params / Payload:**
  ```json
  {
    "seed_entities": [],
    "target_domain": "music",
    "filters": {
      "release_year_range": [1960, 1975]
    }
  }
  ```
- **Response Format:**
  ```json
  {
    "recommendations": []
  }
  ```

---

## 4. Reminiscence Mapping Notes
- How does Qloo handle regional Indian music / regional cinema?
- How to filter by decade / era to match the elder's formative years (typically age 15–30)?
- Best taxonomy mappings for traditional foods / regional cuisines.
