# NostalgiQ 

> **AI-Driven Personal Cultural & Nostalgia Journey Generator**  
> *Powered by Qloo Taste AI Engine & Google Gemini Multimodal Agents.*

[![Live Demo](https://img.shields.io/badge/Demo-Live_App-7C3AED?style=for-the-badge&logo=vercel&logoColor=white)](https://nostalgi-ypboz1z8a-nisantasrmh.vercel.app/)
[![GitHub Repo](https://img.shields.io/badge/GitHub-NostalgiQ-0F172A?style=for-the-badge&logo=github&logoColor=white)](https://github.com/nisantasrmh/NostalgiQ)
[![License: MIT](https://img.shields.io/badge/License-MIT-10B981?style=for-the-badge)](LICENSE)
---

### ⚡ Note for Hackathon Evaluators
> **Live Demo Notice:** The hosted live URL runs on pre-generated cached Taste Graph sessions to guarantee zero-latency uptime and prevent API rate-limiting during judge evaluation. The full dynamic API pipeline, Gemini orchestration handlers, and Qloo endpoint code are completely available and inspectable in this public repository.
---

## 📌 Executive Summary

**NostalgiQ** is an agentic web platform designed to bridge cultural memories with modern algorithmic curation. By leveraging **Qloo’s Taste AI API** alongside **Google Gemini**, NostalgiQ analyzes multi-domain user affinities (music, cinema, literature, dining) to craft hyper-personalized nostalgic itineraries, playlists, and interactive cultural experiences.

---

## 🏛️ System Architecture

```
                                  +------------------------+
                                  |   React / Next.js UI   |
                                  |      (Vercel App)      |
                                  +-----------+------------+
                                              |
                                              v  REST / JSON
                                  +-----------+------------+
                                  |    FastAPI Engine      |
                                  |     (Render Host)      |
                                  +----+--------------+----+
                                       |              |
                    +------------------+              +------------------+
                    |                                                    |
                    v                                                    v
    +---------------+---------------+                    +---------------+---------------+
    |       Qloo Taste AI API       |                    |     Google Gemini LLM Agent   |
    |  (Cultural Affinity Engine)   |                    |   (Multi-Turn Reasoning/Plan) |
    +-------------------------------+                    +-------------------------------+
```

---

## ✨ Key Features & Technical Highlights

* **Qloo Affinity Engine Integration:** Connects user preferences across cross-domain entities (e.g., mapping film preferences to music and dining tastes).
* **Agentic Multi-Turn Planning:** Powered by Google Gemini (`google-genai` SDK) with tool-calling capabilities to construct step-by-step nostalgic plans and reasoning trails.
* **Deterministic Health & Culinary Adaptation:** Rule-based adjustments for diet, allergens, and physical accessibility.
* **Full-Stack Cloud Deployment:** Client deployed on Vercel Edge Network; API backend hosted on Render.

---

## 🗺️ Engineering Roadmap & Feature Matrix

- [x] **Core Architecture:** Project scaffold & modular directory layout
- [x] **Abstract Client:** Clean interface layer for Qloo Client (`BaseQlooClient`)
- [x] **Dataset Layer:** Mock datasets for Music, Film, and Dining (`"source": "MOCK"`)
- [x] **Factory Architecture:** Dynamic Mock/Real factory using `USE_MOCK_QLOO` flag
- [x] **Adaptation Engine:** Deterministic culinary adaptation rules (low-sodium, soft food, diabetic, allergens)
- [x] **Agentic Loop:** Tool-calling skeleton with step-by-step reasoning trail
- [x] **Side-by-Side Evaluation:** Baseline generic LLM generator vs. Qloo-enhanced generator
- [x] **REST API Layer:** FastAPI endpoints (`/health`, `/api/personas`, `/api/plan`, `/api/compare`, `/api/export-playlist`)
- [x] **UI Components:** Interactive frontend (`IntakeForm`, `PlanView`, `ComparisonPanel`, `ReasoningTrail`, `Playlist Export`)
- [ ] **Production API:** Live production Qloo API key provisioning & rate-limit handler
- [ ] **LLM Function Calling:** Production-level function calling integration
- [ ] **Voice Interface:** Audio input/output pipeline for hands-free caregiver & elder interaction

---

## 🛠️ Tech Stack

| Category | Technology | Deployment / Hosting |
| :--- | :--- | :--- |
| **Frontend** | React, TypeScript, Next.js / Vite, Tailwind CSS | **Vercel** |
| **Backend** | Python 3.11+, FastAPI, Uvicorn | **Render** |
| **AI / ML** | Google Gemini SDK (`google-genai`), Qloo Taste AI API | Cloud Services |
| **Tooling & VCS** | Git, GitHub, Environment (.env) | GitHub Repository |

---

## 📦 Local Setup & Installation

### Prerequisites
* **Node.js** >= 18.x
* **Python** >= 3.10
* **Git**

### 1. Clone the Repository
```bash
git clone https://github.com/nisantasrmh/NostalgiQ.git
cd NostalgiQ
```

### 2. Backend Setup
```bash
# Navigate to backend directory
cd NostalgiQ

# Create and activate virtual environment
python -m venv venv

# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Environment Configuration
Create a `.env` file in the backend root directory:
```env
GEMINI_API_KEY=your_gemini_api_key_here
QLOO_API_KEY=your_qloo_api_key_here
USE_MOCK_QLOO=true
```

#### Start FastAPI Development Server
```bash
uvicorn backend.main:app --reload --port 8000
```

### 3. Frontend Setup
```bash
# In a new terminal window, navigate to frontend
cd frontend

# Install packages
npm install

# Start development server
npm run dev
```

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.
