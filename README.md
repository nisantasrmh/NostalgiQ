NostalgiQ 🎵🎬✨
NostalgiQ is an AI-driven agentic web application designed to curate personalized memory-lane experiences, media recommendations, and nostalgic itineraries. Powered by Qloo's Taste AI API and Google Gemini, NostalgiQ intelligently maps user cultural affinities, media preferences, and nostalgic themes to deliver hyper-personalized cultural journeys.

🚀 Live Demo & Links
Live Application: https://nostalgi-ypboz1z8a-nisantasrmh.vercel.app/

GitHub Repository: https://github.com/nisantasrmh/NostalgiQ

✨ Key Features & Qloo Integration
Qloo-Powered Taste Engine: Integrates Qloo's Taste AI API to analyze cultural affinities, music, movies, and media preferences for deep personalization.

Agentic Multi-Turn Assistant: Powered by Google Gemini (google-genai SDK) to handle dynamic multi-turn interactions, reasoning, and itinerary building.

Personalized Nostalgia Generation: Transforms user inputs into curated playlists, cultural throwbacks, and tailored activity flows.

Full-Stack Deployment: Fast React/TypeScript frontend deployed on Vercel with a lightweight FastAPI backend hosted on Render.

🛠️ Tech Stack
Frontend: React, TypeScript, Vite / Next.js, Tailwind CSS (Hosted on Vercel)

Backend: Python, FastAPI, Google Gemini SDK, Qloo API (Hosted on Render)

Version Control: Git & GitHub

📦 Local Development Setup
1. Clone the Repository
git clone https://github.com/nisantasrmh/NostalgiQ.git
cd NostalgiQ

2. Backend Setup
cd memory-lane
python -m venv venv

Activate Virtual Environment (Windows)
venv\Scripts\activate

Activate Virtual Environment (macOS/Linux)
source venv/bin/activate

pip install -r requirements.txt

Environment Variables
Create a .env file in your backend folder with:
GEMINI_API_KEY=your_gemini_api_key
QLOO_API_KEY=your_qloo_api_key

Run the API server:
uvicorn backend.main:app --reload

3. Frontend Setup
cd frontend
npm install
npm run dev

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.