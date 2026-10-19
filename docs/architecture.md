# Memory Lane - Architecture & Design

## Overview
Memory Lane is an agentic caregiver assistant designed to spark reminiscence therapy for elderly individuals (particularly those experiencing dementia or Alzheimer's). It merges **cultural taste graph intelligence (via Qloo)** with **agent-driven health adaptation** (soft food, diabetic-friendly, low-sodium, allergen-safe).

```
+-----------------------------------------------------------------------------------+
|                                React Frontend (Vite)                              |
|   [ Intake Form ]  -->  [ Plan View ]  <-->  [ Side-by-Side Comparison Panel ]    |
|                               ^                                                   |
|                               +-- [ Reasoning Trail & Feedback Buttons ]          |
+-----------------------------------------------------------------------------------+
                                        |  REST API / JSON
                                        v
+-----------------------------------------------------------------------------------+
|                             FastAPI Backend Service                               |
|                                                                                   |
|  Endpoints:                                                                       |
|   - GET  /health                                                                  |
|   - POST /api/plan      (Agent-orchestrated Qloo taste graph + health adaptation) |
|   - POST /api/compare   (Side-by-side: Qloo Agent vs Generic LLM baseline)       |
+-----------------------------------------------------------------------------------+
        |                                                 |
        v                                                 v
+-------------------------------------+   +-----------------------------------------+
|        Agent Reasoning Loop         |   |        Baseline LLM Comparison          |
|  (Orchestrator, Prompt Constraints, |   |   (Generic LLM without Taste Graph)     |
|   Health Rule Engine)               |   +-----------------------------------------+
+-------------------------------------+
        |
        v
+-----------------------------------------------------------------------------------+
|                               Qloo Client Abstraction                            |
|                                                                                   |
|  [ Abstract Base Interface: base.py ]                                             |
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

## Key Modules

### 1. Qloo Taste Graph Layer (`backend/qloo/`)
- **`base.py`**: Abstract base class (`QlooClient`) defining `search_entity()` and `get_recommendations()`.
- **`mock_client.py`**: Simulates Qloo API responses with high-fidelity, culturally coherent entities tagged with `"source": "MOCK"`.
- **`client.py`**: Real client stub awaiting official documentation and API key.
- **`factory.py`**: Dynamic factory switching between real and mock clients using `USE_MOCK_QLOO`.

### 2. Agent & Tool Orchestration (`backend/agent/`)
- **`agent.py`**: Reasoning loop driving persona analysis, Qloo taste queries, and dietary transformations.
- **`tools.py`**: Callable tools (`search_entity`, `get_recommendations`, `adapt_for_health`).
- **`prompts.py`**: Strict system prompt enforcing grounding: every recommendation must link back to taste graph evidence, forbidding fabricated songs/dishes, and maintaining non-medical boundaries.
- **`health_rules.py`**: Deterministic rule engine for soft food modifications, diabetic sugar swaps, low-sodium seasonings, and allergen exclusions.

### 3. Models (`backend/models/schemas.py`)
- Pydantic models validating `ElderProfile`, `RecommendationItem`, `ReasoningStep`, `MemoryPlan`, and `ComparisonResult`.

### 4. Baseline (`backend/baseline/llm_only.py`)
- Generates ungrounded generic LLM recommendations to showcase the superior authenticity and safety of Qloo-grounded taste graph retrieval.
