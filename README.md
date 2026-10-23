# NostalgiQ 🧠🎶 (The Nostalgia Graph)

> **Agentic reminiscence therapy for caregivers of elderly individuals, bridging cultural memory via the Qloo Taste Graph with clinical dietary adaptation.**

---

## One-Line Pitch
NostalgiQ maps an elder's formative era, regional roots, and cultural affinities via the Qloo Taste Graph to curate familiar music, cinema, and comfort dishes—safely adapted for dysphagia, diabetes, and hypertension.

---

## Problem Statement
Over 55 million people worldwide live with dementia and Alzheimer's disease. As short-term memory fades, long-term emotional and sensory memories from a person's youth (typically ages 15–30) remain remarkably intact. Reminiscence therapy—the deliberate use of music, movies, and comfort dishes from one's youth—is clinically demonstrated to decrease agitation, reduce sundowning symptoms, and restore dignity.

However, caregivers face two severe bottlenecks:
1. **The Cultural Retrieval Gap:** Modern caregivers frequently lack deep encyclopedic knowledge of regional music and cinema from 50+ years ago (e.g., 1960s Maharashtrian Natyasangeet or Chicago South Side blues).
2. **The Safety Transformation Gap:** Beloved cultural dishes (such as festive sweets, crunchy flatbreads, or cured roasts) often present dangerous choking risks for elders with dysphagia or exacerbate chronic conditions like diabetes and hypertension.

---

## Why This Needs Qloo
Generic large language models suffer from severe drawbacks when used for dementia care:
- **Cultural Hallucinations & Anachronisms:** Generic LLMs frequently fabricate song titles, confuse eras, or default to monolithic Western pop (e.g., suggesting The Beatles to an elder who grew up listening to Marathi radio in Pune).
- **Surface-Level Correlative Reasoning:** LLMs lack an explicit, multidimensional cultural taste graph capable of discovering subtle cross-domain bridges—such as correlating Hindustani classical ragas with regional Prabhat Film cinema and festive culinary rituals.
- **Safety Compliance:** LLMs cannot guarantee provenance or deterministic grounding. Qloo provides an authentic, verifiable knowledge graph of cultural affinities. The NostalgiQ agent queries Qloo as ground truth, ensuring that every song, film, and traditional dish traces to a verified cultural entity before deterministic health adaptation rules are applied.

---

## Planned Architecture

```
+-----------------------------------------------------------------------------------+
|                                NostalgiQ Frontend                                 |
|   [ Intake Form ]  -->  [ Plan View ]  <-->  [ Side-by-Side Comparison Panel ]    |
|                               ^                                                   |
|                               +-- [ Reasoning Trail & Caregiver Playlist Export ] |
+-----------------------------------------------------------------------------------+
                                        |  REST API / JSON
                                        v
+-----------------------------------------------------------------------------------+
|                            NostalgiQ Backend Service                              |
|                                                                                   |
|  Endpoints:                                                                       |
|   - GET  /health                                                                  |
|   - GET  /api/personas         (Pre-loaded cultural elder profiles)               |
|   - POST /api/plan             (Agent-orchestrated Qloo taste graph + health)     |
|   - POST /api/compare          (Side-by-side: Qloo Agent vs Generic baseline)     |
|   - POST /api/export-playlist  (Export curated playlist as JSON or CSV)           |
+-----------------------------------------------------------------------------------+
        |                                                 |
        v                                                 v
+-------------------------------------+   +-----------------------------------------+
|     NostalgiQ Reasoning Loop        |   |        Baseline LLM Comparison          |
|  (Orchestrator, Prompt Constraints, |   |   (Generic LLM without Taste Graph)     |
|   Health Rule Engine)               |   +-----------------------------------------+
+-------------------------------------+
        |
        v
+-----------------------------------------------------------------------------------+
|                               Qloo Client Abstraction                            |
|                                                                                   |
|  [ Abstract Base Interface: BaseQlooClient ]                                      |
|        ^                                                                          |
|        |---- Factory (USE_MOCK_QLOO toggle)                                       |
|        |                                                                          |
|        +---> MockQlooClient (mock_client.py) <--- Reads data/mock_data/*.json     |
|        |                                          (tagged "source": "MOCK")       |
|        |                                                                          |
|        +---> RealQlooClient (client.py)      <--- Official Qloo API (TODO)        |
+-----------------------------------------------------------------------------------+
```

---

## Mock Mode Note
> **Transparent Data Provenance:**  
> This project currently operates in **Mock Mode** using `USE_MOCK_QLOO=true`.  
> Every mocked entity in `backend/qloo/mock_data/` explicitly includes `"source": "MOCK"`. Both `MockQlooClient` and the production `QlooClient` implement the exact same `BaseQlooClient` abstract interface. Once the official Qloo API key and endpoint documentation are provisioned, toggling `USE_MOCK_QLOO=false` in `.env` enables live API calls with zero architectural changes.

---

## Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 1. Environment Configuration
Copy the template environment file:
```bash
cp .env.example .env
```
Default configuration values:
```env
USE_MOCK_QLOO=true
QLOO_API_KEY=
QLOO_API_BASE_URL=https://api.qloo.com/v1
LLM_PROVIDER=mock
LLM_API_KEY=
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
```

### 2. Backend Setup (FastAPI)
```bash
# Navigate to project root
cd memory-lane

# Create and activate virtual environment (optional but recommended)
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start backend server
python -m uvicorn backend.main:app --reload --port 8000
```
Verify the backend is live by opening [http://localhost:8000/health](http://localhost:8000/health) or interactive Swagger documentation at [http://localhost:8000/docs](http://localhost:8000/docs).

### 3. Frontend Setup
```bash
# Vite frontend:
cd memory-lane/frontend
npm install
npm run dev

# Or Next.js App Router frontend:
cd memory-lane/frontend-next
npm install
npm run dev
```

### 4. Running Tests
```bash
cd memory-lane
python -m pytest tests/test_export_playlist.py
```

---

## Caregiver Supportive Aid Disclaimer
> **IMPORTANT NOTICE:**  
> NostalgiQ is an assistive lifestyle, reminiscence, and culinary suggestion platform designed exclusively for caregivers. **It does not provide clinical medical advice, diagnostic evaluations, or medical treatments.** Any dietary or texture adaptations (such as dysphagia food softening or diabetic substitutes) are ideas for caregiver convenience and must always be verified with the individual's treating physician, speech-language pathologist, or registered dietitian before serving.

---

## Roadmap Checklist
- [x] Project scaffold & modular directory layout
- [x] Clean abstract interface for Qloo Client (`BaseQlooClient`)
- [x] Realistic mock datasets for Music, Film, and Dining (all tagged `"source": "MOCK"`)
- [x] Mock / Real factory with `USE_MOCK_QLOO` toggle
- [x] Deterministic culinary health adaptation rules (soft food / dysphagia, diabetic, low sodium, allergens)
- [x] Tool-calling agent loop skeleton with step-by-step reasoning trail
- [x] Generic LLM baseline generator for side-by-side comparison
- [x] FastAPI REST endpoints (`/health`, `/api/personas`, `/api/plan`, `/api/compare`, `/api/export-playlist`)
- [x] Interactive UI frontends (IntakeForm, PlanView, ComparisonPanel, ReasoningTrail, Playlist Export)
- [ ] Connect official Qloo API endpoints and authentication once key is provisioned
- [ ] Integrate production LLM function calling (OpenAI / Gemini / Anthropic)
- [ ] Audio voice interface for hands-free caregiver and elder interaction

