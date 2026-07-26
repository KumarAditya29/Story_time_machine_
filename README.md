# StoryTime Machine

StoryTime Machine is narrative version control for branching fiction: edit one atomic scene, let OpenAI identify its story-state delta, trace only causally related scenes, verify each candidate, and regenerate only the scenes that truly need revision.

## What it demonstrates

- Ten ready-to-demo Pocket FM-style stories across romance, thriller, fantasy, crime, sci-fi, drama, and horror (100 scenes total).
- A **story bible** generated per scene with characters, state, facts, tone, causal setup/payoff, state reads, and writes.
- An explainable NetworkX dependency graph across facts, characters, causality, and foreshadowing.
- Safe editing: an edit creates a version, calculates metadata delta, runs graph BFS with hop thresholds, verifies every candidate with OpenAI, and minimally regenerates only approved scenes.
- A persistent audit trail with reasons, hops, and before/after scene diffs. Non-affected text is never sent to regeneration and remains byte-identical.
- A polished React workspace with a story library, graph canvas, scene editor, impact audit, and new-story ingestion.

## Run locally

1. Create a virtual environment (recommended), install Python dependencies, and configure OpenAI:

   ```bash
   python3 -m pip install -r requirements.txt
   cp .env.example .env
   # Add OPENAI_API_KEY to .env
   ```

2. Start the API (it writes the seed library on its first run):

   ```bash
   python3 -m uvicorn backend.main:app --reload --port 8000
   ```

3. In another terminal, start the frontend:

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. Open `http://localhost:5173`. Select any story and press **Map story with AI**. Edit a scene, then press **Save & propagate** to make a new version.

## Suggested live demo

1. Open **Velvet Voicemail** and map its story bible. Show the edge-labelled dependency map.
2. Edit Scene 6, *The Engraving*: change the ring engraving from Mira's mother's initials to Vikram's childhood nickname.
3. Save and propagate. The engine checks graph-linked downstream scenes, regenerates only those OpenAI confirms, and records every skipped/changed decision.
4. Open the Impact Audit to show the hop number, exact rationale, and before/after minimal diff.

## Architecture

```text
frontend/                 React + TypeScript + React Flow writer workspace
backend/models.py         scene, bible, graph, version, and audit contracts
backend/storage.py        one JSON file per story
backend/seed_data.py      10-story / 100-scene seed corpus
backend/generation.py     OpenAI structured extraction, verification, rewrite
backend/graph_engine.py   NetworkX graph + scoped BFS blast radius
backend/versioning.py     versioned edit and multi-hop propagation loop
backend/main.py           thin FastAPI wrapper
```

## API

- `GET /api/stories` — library view
- `POST /api/stories` — add a story with multiple scenes
- `GET /api/stories/{story_id}` — full versioned story
- `POST /api/stories/{story_id}/analyze` — OpenAI story bible + graph
- `GET /api/stories/{story_id}/graph` — graph nodes and explainable edges
- `POST /api/stories/{story_id}/scenes/{scene_id}/edit` — versioned, verified minimal propagation

## Trust boundary

The real API key is loaded only from the ignored local `.env` file. It is never returned by the API, embedded in the frontend, or committed to git.
