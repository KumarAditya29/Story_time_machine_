# Story Time Machine — Hackathon Roadmap

## Product outcome

Deliver a polished local web platform for Pocket FM writers to version stories at scene level. A writer can edit any scene, inspect the precise narrative dependency graph, verify the actual ripple effect with OpenAI, regenerate only scenes that need it, and audit every resulting change.

## Constraints and decisions

- **Deadline:** seven hours from project start; prioritize a reliable, visual end-to-end demo.
- **Experience:** polished React web application, backed by a thin FastAPI API.
- **AI:** live OpenAI API integration is mandatory. The key remains in a local `.env` file only and is never committed or rendered in the UI.
- **Persistence:** JSON files per story, so the app is portable and easy to demo locally.
- **Seed content:** ten Pocket FM-style stories across distinct genres, each with at least ten atomic scenes.
- **Core guarantee:** untouched scenes retain their exact original text; every regenerated scene records why it changed and its before/after diff.

## Milestone 1 — Foundation and story corpus

**Intended outcome:** a runnable repository with a clear data model and ten selectable, multi-genre seed stories (10+ scenes each).

**Scope:** project layout; story, scene, state, version, dependency, and audit schemas; local storage conventions; seed corpus.

**Decisions:** React + TypeScript + Vite for the client; Python + FastAPI for the API; NetworkX for dependency analysis; JSON persistence.

**Blockers:** none.

**Evidence required:** the seed-data validator confirms 10 stories and >=10 ordered scenes per story; each story is loadable through the storage layer.

## Milestone 2 — Narrative intelligence graph

**Intended outcome:** every scene has an AI-extracted story-bible record and the graph engine accurately discovers causal, fact, character, and foreshadow/payoff links.

**Scope:** OpenAI structured extraction, schema validation, graph construction, dependency reasons, and filtered candidate/blast-radius traversal.

**Decisions:** use a cost-efficient OpenAI mini model and structured JSON; preserve explicit/manual metadata as a safe fallback only where extraction is unavailable.

**Blockers:** a valid `OPENAI_API_KEY` must be present in local `.env`.

**Evidence required:** extracted metadata persisted per scene; graph returns explainable candidate links and filters unrelated downstream scenes.

## Milestone 3 — Safe branching regeneration

**Intended outcome:** editing one scene creates a new version, computes a metadata delta, verifies candidates before modification, performs minimal multi-hop rewrites, and stores an audit trail.

**Scope:** edit workflow, delta engine, LLM verification, constrained regeneration, visited-set propagation, hop confidence thresholds, re-extraction, graph update, and version history.

**Decisions:** never overwrite a previous version; never regenerate a scene without a positive verification decision; propagate forward and backward only along meaningful graph links.

**Blockers:** completion of Milestone 2.

**Evidence required:** a scripted edit shows both changed and byte-identical untouched scenes, with reasons, diffs, and version provenance.

## Milestone 4 — Writer-facing interface

**Intended outcome:** a visually polished application that makes the system understandable at a glance.

**Scope:** story library, scene reader/editor, interactive graph, processing state, impact/audit panel, before-after diffs, and version selector.

**Decisions:** graph nodes are visually coded as edited, verified-affected, regenerated, checked-unaffected, and untouched.

**Blockers:** end-to-end backend workflow from Milestone 3.

**Evidence required:** a writer can complete the core edit-to-diff journey from the browser without using API tools.

## Milestone 5 — Demo readiness

**Intended outcome:** an installation-ready, reproducible hackathon submission.

**Scope:** automated smoke tests, seed validation, graceful API errors, README, setup instructions, and a short demo scenario.

**Decisions:** favor one compelling seeded edit scenario plus broad story-library coverage.

**Blockers:** none beyond previous milestones.

**Evidence required:** fresh setup succeeds; a live edit completes using OpenAI; demo steps and expected visual results are documented.
