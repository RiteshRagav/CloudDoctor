# CloudDoctor — Development Plan (POC → V1 → Expand → Harden)

## Objectives
- ✅ Deliver a working CloudDoctor MVP that can **trigger simulated infra failures**, **generate logs**, **analyze logs**, and **run AI diagnosis** (GPT-4o via Emergent key), while storing incidents in **MongoDB**.
- ✅ Provide a **dark-theme React dashboard** with health pills, incident triggering, log analyzer (streaming via polling), AI diagnosis, and incident reports.
- ⏳ Integrate **BetterStack Logtail** when tokens are provided; until then, run with a **local log ring buffer + query** fallback using the same API contract.
- 🔧 Next focus: production hardening (LLM budget/quotas, persistence, rate limits, pagination) and BetterStack enablement.

---

## Implementation Steps

### Phase 1 — Core Workflow POC (Isolation; do not proceed until stable)
**Goal:** prove the hardest integration/data-flow: *failure trigger → logs generated → logs retrievable → AI diagnosis produced → incident persisted*.

**Status: ✅ Completed**

1. **Web research / best practices**
   - Reviewed BetterStack Logtail ingestion/querying patterns (integration staged behind env).
   - Reviewed FastAPI logging patterns and emergentintegrations `LlmChat` usage.

2. **POC: LLM call sanity**
   - Added `EMERGENT_LLM_KEY` to backend env.
   - Validated GPT-4o call and JSON diagnosis output.

3. **POC: Failure simulator + log generation**
   - Implemented scenario-based failure simulator with background log emission.

4. **POC: Log retrieval abstraction**
   - Implemented **LocalLogProvider** (in-memory ring buffer) with query + stats.
   - BetterStack provider planned behind env flags (tokens not yet supplied).

5. **POC: Incident persistence**
   - MongoDB `incidents` collection: create, update (diagnosis), resolve.

6. **POC validation checklist**
   - Trigger scenario → logs appear in query within seconds.
   - AI diagnosis returns consistent schema (or fails gracefully if budget exceeded).
   - Incident record created/updated in MongoDB.

**Phase 1 user stories (✅ met)**
1. Trigger a failure scenario and receive an incident id.
2. Fetch recent logs filtered by severity.
3. Run AI diagnosis and see root cause + fixes.
4. See the incident stored and retrievable from the database.
5. Reset system to healthy (stop scenario) and see recovery logs.

---

### Phase 2 — V1 App Development (Backend + Frontend MVP)
**Goal:** build the full UI around the proven core flow, with consistent APIs and dark theme.

**Status: ✅ Completed (with minor fixes applied)**

1. **Backend (FastAPI)**
   - Models (Pydantic): `Incident`, `IncidentCreate`, `DiagnosisResult`, `LogEvent`.
   - Routes implemented:
     - `GET /api/health` (MongoDB, LLM, BetterStack-configured?, Sample App state)
     - `GET /api/scenarios`
     - `POST /api/incidents/trigger`
     - `GET /api/incidents` + `GET /api/incidents/{id}`
     - `POST /api/incidents/{id}/diagnose`
     - `POST /api/incidents/{id}/resolve`
     - `GET /api/logs` + `GET /api/logs/stats`
     - `GET /api/simulator/state` + `POST /api/simulator/stop`
   - Logging:
     - Local ring-buffer log provider active.
     - BetterStack tokens supported via env but not configured yet.

2. **Frontend (React, dark theme)**
   - Pages delivered: `Dashboard`, `Log Analyzer`, `AI Diagnosis`, `Reports`.
   - Dashboard:
     - Health pills visible in sidebar; incident trigger dialog; active incident banner; recent incidents list.
   - Log Analyzer:
     - Severity chips + counts; live streaming toggle (polling); formatted log lines.
   - AI Diagnosis:
     - Incident selector; “Run AI Diagnosis”; results UI with confidence meter, root cause, fixes, MTTR.
     - Note: diagnosis calls may fail with **LLM budget exceeded** under heavy testing; UI/UX handles this gracefully.
   - Reports:
     - Incidents table with status/severity badges.
     - Detail sheet with diagnose/resolve actions.

3. **End-to-end wiring**
   - Frontend wired to backend via `REACT_APP_BACKEND_URL`.
   - Stop scenario resets simulator state and UI.

4. **Testing: 1st full E2E pass**
   - Backend: ✅ 100% passing.
   - Frontend: ✅ core flows validated.
   - Fixes applied:
     - Trigger dialog confirm button reliably enables after scenario selection.
     - Reports status filter testid applied on trigger element.

**Phase 2 user stories (✅ met)**
1. Open Dashboard and see subsystem health.
2. Trigger a scenario and see incident created.
3. Watch logs appear and filter by severity.
4. Run AI diagnosis and get recommended fixes (or graceful budget error).
5. Review past incidents and resolve/close them.

---

### Phase 3 — BetterStack Enablement + Streaming UX (after tokens available)
**Goal:** switch from local logs to BetterStack without changing UI contracts.

**Status: ⏳ Pending (blocked on tokens)**

1. **Token onboarding**
   - Obtain BetterStack:
     - `BETTERSTACK_SOURCE_TOKEN` (ingestion)
     - `BETTERSTACK_QUERY_TOKEN` (query)
   - Add `/api/health` enhancements: report “configured” + last successful send/query.

2. **BetterStack provider implementation**
   - Ingestion:
     - Route simulator logs + application logs to BetterStack.
   - Query:
     - Implement log querying/search via BetterStack APIs.
     - Normalize responses into `LogEvent` schema.
   - Resilience:
     - Auto-fallback to local provider on BetterStack errors/timeouts.

3. **Near-real-time logs**
   - Improve Log Analyzer from full refresh to incremental fetch (`since=last_ts`).
   - Optional: switch to SSE/WebSocket once BetterStack query latency is validated.

4. **Testing: 2nd E2E pass**
   - Verify the same UI flow works with BetterStack enabled.
   - Verify behavior when BetterStack is misconfigured/unavailable.

**Phase 3 user stories (target)**
1. When BetterStack is configured, logs come from BetterStack.
2. If BetterStack fails, the app still shows logs via local fallback.
3. Log volume stats update as new logs arrive.
4. Health pills reflect BetterStack configuration/state.
5. Diagnosis uses consistent log shape regardless of provider.

---

### Phase 4 — Hardening, Quality, and Maintainability
**Goal:** stabilize for longer-running use, heavier load, and real operational usage.

**Status: ⏳ Next recommended phase**

1. **Data quality & schemas**
   - Enforce consistent incident lifecycle: `open → diagnosed → resolved`.
   - Standardize severity mapping and timestamps.

2. **LLM prompt + output robustness**
   - Force strict JSON output; validate with Pydantic.
   - Add retry/backoff on transient LLM failures.
   - Add a clear UX state for budget exceeded (already graceful) + optional admin banner.

3. **Performance & safety**
   - Pagination for `/api/logs` + `/api/incidents`.
   - Server-side filters (scenario, levels, since) and caps.
   - Rate limit diagnosis endpoint to protect budget.
   - Redact secrets from logs before sending to providers.

4. **Testing: final regression pass**
   - Add pytest coverage for simulator + provider behaviors.
   - UI smoke tests for empty/error states.
   - Add a non-LLM “diagnosis stub” mode for test environments.

**Phase 4 user stories (target)**
1. Diagnosis cards never break due to malformed AI output.
2. App remains responsive with many logs/incidents.
3. Incident statuses and timestamps are consistent.
4. Users see friendly errors for degraded subsystems.
5. App remains usable even when one subsystem is degraded.

---

## Next Actions
1. **BetterStack tokens**: user provides `BETTERSTACK_SOURCE_TOKEN` and `BETTERSTACK_QUERY_TOKEN`.
2. Implement BetterStack provider + query normalization + fallback.
3. Improve streaming UX to incremental fetch (`since=last_ts`) and add pagination.
4. Add rate limiting + retries for AI diagnosis to manage cost/budget.
5. Run the 2nd E2E pass with BetterStack enabled.

---

## Success Criteria
- ✅ Core flow works end-to-end: **Trigger incident → logs visible → (AI diagnosis if budget available) → incident stored → resolve/stop resets**.
- ✅ `/api/health` accurately reports MongoDB + LLM + BetterStack-configured + sample state.
- ✅ Log Analyzer supports severity filtering + counts; updates near real-time (polling).
- ✅ UI is dark-themed, stable, and handles empty/error states cleanly.
- ⏳ With BetterStack configured: logs are ingested/queried from BetterStack with reliable fallback.
