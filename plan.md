# CloudDoctor — Development Plan (POC → V1 → Expand → Harden)

## Objectives
- Deliver a working CloudDoctor MVP that can **trigger simulated infra failures**, **generate logs**, **analyze logs**, and **run AI diagnosis** (GPT-4o via Emergent key), while storing incidents in **MongoDB**.
- Integrate **BetterStack Logtail** when tokens are provided; until then, ship a **local log buffer + query** fallback with the same API contract.
- Provide a **dark-theme React dashboard** with health pills, incident triggering, log analyzer, AI diagnosis, and incident reports.

---

## Implementation Steps

### Phase 1 — Core Workflow POC (Isolation; do not proceed until stable)
**Goal:** prove the hardest integration/data-flow: *failure trigger → logs generated → logs retrievable → AI diagnosis produced → incident persisted*.

1. **Web research / best practices**
   - Review BetterStack Logtail ingestion + querying patterns and rate limits.
   - Review FastAPI logging patterns (structured logs, correlation IDs) and emergentintegrations `LlmChat` usage.

2. **POC: LLM call sanity**
   - Add `EMERGENT_LLM_KEY` to backend env.
   - Create minimal script/endpoint to call `LlmChat` with GPT-4o and return structured JSON (root cause, confidence, fixes, MTTR).

3. **POC: Failure simulator + log generation**
   - Implement `/api/simulate/{scenario}` that flips an in-memory “service state” and emits structured logs.
   - Implement a background task that, while in failed state, emits logs every few seconds (to simulate real streaming).

4. **POC: Log retrieval abstraction**
   - Define `LogProvider` interface:
     - `append(log_event)`
     - `query(levels, since, limit)`
     - `stats(since)`
   - Implement **LocalLogProvider** (ring buffer in memory) as default.
   - Stub **BetterStackLogProvider** behind env flags; returns “not configured” until tokens exist.

5. **POC: Incident persistence**
   - MongoDB `incidents` collection: create incident on trigger; update with diagnosis; resolve/close.

6. **POC validation checklist**
   - Trigger scenario → logs appear in query within 1–2 seconds (local provider).
   - AI diagnosis endpoint returns consistent JSON schema.
   - Incident record created/updated in MongoDB.

**Phase 1 user stories**
1. As a user, I can trigger a failure scenario and receive an incident id.
2. As a user, I can fetch recent logs filtered by severity.
3. As a user, I can run AI diagnosis on an incident and see root cause + fixes.
4. As a user, I can see the incident stored and retrievable from the database.
5. As a user, I can reset the system to healthy (stop scenario) and see logs reflect recovery.

---

### Phase 2 — V1 App Development (Backend + Frontend MVP)
**Goal:** build the full UI around the proven core flow, with consistent APIs and dark theme.

1. **Backend (FastAPI)**
   - Models (Pydantic): `Incident`, `IncidentCreate`, `DiagnosisResult`, `LogEvent`, `HealthStatus`.
   - Routes:
     - `GET /api/health` (MongoDB, LLM, BetterStack-configured?, Sample App state)
     - `POST /api/incidents/trigger` (scenario) → creates incident + starts emitting logs
     - `POST /api/incidents/{id}/diagnose` → pulls logs + calls LLM + stores diagnosis
     - `GET /api/incidents` + `GET /api/incidents/{id}`
     - `POST /api/incidents/{id}/resolve`
     - `GET /api/logs` (filters: level, since, limit) + `GET /api/logs/stats`
     - `POST /api/simulate/stop`
   - Logging:
     - Structured JSON logs, correlation id middleware.
     - Provider switch: BetterStack if tokens exist, else local provider.

2. **Frontend (React, dark theme)**
   - Pages: `Dashboard`, `Log Analyzer`, `AI Diagnosis`, `Reports`.
   - Dashboard:
     - 4 health pills (BetterStack, MongoDB, LLM, Sample App).
     - Trigger Incident modal (scenario select) + current incident banner.
   - Log Analyzer:
     - Severity filter, auto-refresh (polling), log list + counts.
   - AI Diagnosis:
     - Select incident, “Run AI Diagnosis”, display confidence, MTTR, root cause, fixes.
   - Reports:
     - Incident table, status badges, details drawer, resolve button.

3. **End-to-end wiring**
   - Ensure API base URL uses `REACT_APP_BACKEND_URL`.
   - Validate stop scenario resets states and UI reflects health.

4. **Testing: 1st full E2E pass**
   - Run through core flow in preview:
     - Health → Trigger → Logs appear → Diagnose → Incident stored → Resolve → Stop.
   - Fix critical UX/API issues immediately.

**Phase 2 user stories**
1. As a user, I open Dashboard and instantly see which subsystems are healthy/unhealthy.
2. As a user, I can trigger a scenario from the UI and see confirmation plus an incident created.
3. As a user, I can watch logs appear and filter by ERROR/WARN/INFO/DEBUG.
4. As a user, I can run AI diagnosis and get actionable recommended fixes.
5. As a user, I can review past incidents and resolve/close them.

---

### Phase 3 — BetterStack Enablement + Streaming UX (after tokens available)
**Goal:** switch from local logs to BetterStack without changing UI contracts.

1. **Token onboarding**
   - Add env vars: `BETTERSTACK_SOURCE_TOKEN`, `BETTERSTACK_QUERY_TOKEN` (or query creds depending on API), host/endpoint.
   - Add `/api/health` reporting “configured” + last successful send/query.

2. **BetterStack provider implementation**
   - Ingestion: route app logs + simulated logs to BetterStack.
   - Querying: implement log search/query; normalize into `LogEvent` schema.
   - Fallback behavior: auto-fallback to local provider on BetterStack errors.

3. **Near-real-time logs**
   - Improve log analyzer polling cadence + incremental fetch (`since=last_ts`).

4. **Testing: 2nd E2E pass**
   - Verify same UI flow works with BetterStack enabled.
   - Verify resilience when BetterStack is misconfigured/unavailable.

**Phase 3 user stories**
1. As a user, when BetterStack is configured, I can see logs sourced from BetterStack.
2. As a user, if BetterStack fails, the app still shows logs via local fallback.
3. As a user, I can see log volume stats update as new logs arrive.
4. As a user, health pills accurately reflect BetterStack configuration and status.
5. As a user, diagnosis uses the same log shape regardless of provider.

---

### Phase 4 — Hardening, Quality, and Maintainability
1. **Data quality & schemas**
   - Enforce consistent incident lifecycle states; timestamps; severity mapping.

2. **LLM prompt + output robustness**
   - Force JSON output; validate with Pydantic; retry on invalid format.
   - Add deterministic “confidence” + MTTR heuristics if model omits them.

3. **Performance & safety**
   - Ring buffer size limits, pagination, server-side filtering.
   - Rate limiting for diagnose endpoint.
   - Redact secrets from logs.

4. **Testing: final regression pass**
   - Backend pytest for models/providers.
   - UI smoke test of all routes + empty/error states.

**Phase 4 user stories**
1. As a user, I never see broken diagnosis cards due to malformed AI output.
2. As a user, the app remains responsive even with many logs/incidents.
3. As a user, I can rely on incidents having consistent statuses and timestamps.
4. As a user, I can understand errors via friendly UI states.
5. As a user, the app remains usable even when one subsystem is degraded.

---

## Next Actions
1. Add `EMERGENT_LLM_KEY` to `/app/backend/.env` and implement Phase 1 POC endpoints/scripts.
2. Implement `LocalLogProvider` + incident MongoDB persistence and validate core flow via curl.
3. Build V1 React UI (dark theme) and wire to stable APIs.
4. Run first end-to-end test pass; fix issues before expanding features.

---

## Success Criteria
- Core flow works end-to-end: **Trigger incident → logs visible → AI diagnosis → incident stored → resolve/stop resets**.
- `/api/health` accurately reports MongoDB + LLM + BetterStack-configured + sample state.
- Log Analyzer supports severity filtering + shows counts; updates in near real-time (polling).
- AI Diagnosis returns validated structured output (root cause, fixes, confidence, MTTR) and persists to MongoDB.
- UI is dark-themed, stable, and handles empty/error states cleanly.
