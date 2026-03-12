# Codex Analysis — Agent Office Plan Review

> Codex (gpt-5.3-codex) reviewed PLAN.md, the full codebase, and researched 40+ API docs. Here's the full report.

---

## Honest Analysis — What's Missing

### Needs a Phase 0 (Security & Operability)
- Secrets management (OS keychain, not plaintext in renderer)
- Auth/RBAC — who can access what
- Audit logs for agent actions
- Backup/restore strategy
- Schema migration strategy for SQLite
- Update/rollback strategy for the app itself

### Needs Scope Guardrails
- Clear definition of what v2.0 is **NOT**
- Test strategy: unit/integration/e2e + agent eval harness
- Legal/compliance: scraping ToS, robots.txt, platform posting policies, data retention

### Needs Cost Governance
- Per-agent budget caps with hard kill-switches
- Provider outage fallback behavior
- Token burn rate monitoring

---

## What's Unrealistic (Needs Re-scoping)

1. **"Seamless cloud↔local swap"** — Different models behave differently (context windows, tool use, reasoning). Do **manual + policy-assisted swap** for v2, not "seamless."
2. **Too broad in one sequence** — Dual UI + full CRM + browser agent + multi-business + 15 connectors is too much. Narrow each phase.
3. **Cross-agent memory read/write** — Without strict permissions = data leakage/corruption risk. Need access control.
4. **"Run anywhere" + sync** — Conflict resolution rules are underspecified. Needs event sourcing or strong conflict semantics.

---

## Immediate Architecture Risks (Current App)

| Risk | Location | Severity |
|------|----------|----------|
| Full Node access in renderer | `main.js:13-16` (`nodeIntegration: true`) | HIGH |
| API keys in renderer process | `index.html:2748-2750` | HIGH |
| Heuristic process detection (false positives) | `index.html:2202-2245` | MEDIUM |
| 4000-line monolith | `index.html` | MEDIUM |

---

## Complete Credentials Matrix (All Phases)

Legend: `[F]` = free, `[F/P]` = free tier + paid at scale, `[P]` = paid

### Phase 1: Foundation
| Credential | Type | Cost |
|-----------|------|------|
| `APP_MASTER_KEY` | Self-generated | `[F]` |
| `DATA_ENCRYPTION_KEY` | Self-generated | `[F]` |
| `JWT_SIGNING_KEY` | Self-generated | `[F]` |
| Apple Developer ID + notarization key | Apple | `[P]` $99/yr |
| Windows signing cert | DigiCert etc. | `[P]` |
| GitHub Actions secrets | GitHub | `[F/P]` |

### Phase 2: Agent Engine
| Credential | Type | Cost |
|-----------|------|------|
| `ANTHROPIC_API_KEY` | Anthropic | `[F/P]` |
| `OPENAI_API_KEY` | OpenAI | `[F/P]` |
| `GEMINI_API_KEY` | Google | `[F/P]` |
| `DASHSCOPE_API_KEY` (Qwen cloud) | Alibaba | `[F/P]` |
| `OPENROUTER_API_KEY` | OpenRouter | `[F/P]` |
| Ollama (local) | None needed | `[F]` |

### Phase 3: Skills & Workflows
| Credential | Type | Cost |
|-----------|------|------|
| `WORKFLOW_WEBHOOK_SECRET` | Self-generated HMAC | `[F]` |
| `SKILL_REGISTRY_TOKEN` | If private registry | `[F/P]` |
| Git deploy keys | GitHub/GitLab | `[F/P]` |

### Phase 4: Browser & Research
| Credential | Type | Cost |
|-----------|------|------|
| Playwright (local) | None needed | `[F]` |
| `BROWSERBASE_API_KEY` + `PROJECT_ID` | Stagehand cloud | `[F/P]` |
| `PROXY_USER` / `PROXY_PASS` | Proxy provider | `[P]` |
| `VERCEL_TOKEN` | Vercel | `[F/P]` |
| `NETLIFY_PAT` | Netlify | `[F/P]` |
| `CLOUDFLARE_API_TOKEN` | Cloudflare | `[F/P]` |

### Phase 5: Files & Documents
| Credential | Type | Cost |
|-----------|------|------|
| `AWS_ACCESS_KEY_ID` / `SECRET` | AWS S3 | `[F/P]` |
| GCS service account | Google Cloud | `[F/P]` |
| OCR/doc processing API keys | Various | `[F/P]` |

### Phase 6: Task Pipeline + CRM
| Credential | Type | Cost |
|-----------|------|------|
| SMTP creds or Gmail OAuth tokens | Email provider | `[F/P]` |
| Google Calendar/Sheets/Drive OAuth | Google Cloud Console | `[F/P]` |
| `STRIPE_SECRET_KEY` | Stripe | `[F/P]` |
| `STRIPE_PUBLISHABLE_KEY` | Stripe | `[F/P]` |
| `STRIPE_WEBHOOK_SECRET` | Stripe | `[F/P]` |

### Phase 7: UI Modes
| Credential | Type | Cost |
|-----------|------|------|
| Analytics/feature flag keys (optional) | Various | `[F/P]` |

### Phase 8: Integrations
| Credential | Type | Cost |
|-----------|------|------|
| **Notion**: integration token or OAuth client | Notion | `[F/P]` |
| **Slack**: bot token, app token, signing secret | Slack | `[F/P]` |
| **Discord**: bot token, client ID/secret | Discord | `[F]` |
| **Telegram**: bot token (via BotFather) | Telegram | `[F]` |
| **GitHub**: App ID, private key, webhook secret | GitHub | `[F/P]` |
| **X/Twitter**: developer account + API creds | X | `[P]` ~$200/mo+ |
| **LinkedIn**: OAuth + approved product permissions | LinkedIn/Microsoft | `[F/P]` approval required |
| **WhatsApp**: Meta app ID/secret + system-user token | Meta | `[F/P]` per-message pricing |
| **Zapier/n8n**: OAuth/API key | Zapier/n8n | `[F/P]` |

### Phase 9: Deployment
| Credential | Type | Cost |
|-----------|------|------|
| Cloud provider (AWS IAM / DO PAT / Hetzner token) | Provider | `[P]` $5-20/mo |
| Container registry token | Docker Hub / GHCR | `[F/P]` |
| SSH deploy key | Self-generated | `[F]` |
| `POSTGRES_URL` / Redis password | Managed DB | `[F/P]` |
| Litestream storage creds | S3/compatible | `[F/P]` |
| Observability (Sentry/Grafana) | Various | `[F/P]` |

### Phase 10: Intelligence
| Credential | Type | Cost |
|-----------|------|------|
| Eval/trace platform (Langfuse etc.) | Various | `[F/P]` |
| Vector store (if managed) | Pinecone/Weaviate | `[F/P]` |
| Guardrail policy signing keys | Self-generated | `[F]` |

---

## Recommended Tech Stack

| Component | Tech | Why |
|-----------|------|-----|
| Desktop shell | Electron + Vite + TypeScript + React | Modern, fast builds, type safety |
| Agent runtime | Node.js TS in main process + worker subprocesses | Already using Node, natural fit |
| Terminal emulator | `node-pty` + xterm.js | Real terminal per agent |
| IPC | `contextBridge` + `zod` typed contracts | Security + type safety |
| Database | SQLite (`better-sqlite3`) + Drizzle ORM | Already using SQLite, WAL mode |
| Queue (local) | SQLite-backed queue | No Redis dependency for v2 |
| Queue (cloud) | BullMQ + Redis | When going multi-worker |
| Memory | Markdown files + SQLite FTS5 index | Searchable, human-readable |
| Browser automation | Playwright (primary) | Free, reliable, well-maintained |
| AI browser agent | Pick ONE: Stagehand or browser-use | Don't do both |
| Integrations API | Fastify + WebSocket | Fast, typed, streaming |
| Observability | OpenTelemetry JS | Vendor-neutral |
| Backup/sync | Litestream (SQLite → S3) | Simple, reliable |
| Secrets (local) | OS keychain (`keytar`) | Don't store in plaintext |
| Secrets (cloud) | AWS Secrets Manager / Vault | Production grade |

---

## Open-Source Projects to Integrate

### Use Now (v2.0)
- **Playwright** (Apache-2.0) — browser automation
- **better-sqlite3** — SQLite driver
- **node-pty** — terminal multiplexing
- **xterm.js** — terminal rendering in UI

### Use in v3.0+
- **BullMQ** — job queue when going cloud/multi-worker
- **OpenTelemetry JS** — observability
- **Litestream** — SQLite replication to S3
- **Playwright MCP server** — agent/browser bridge

### Use Carefully (Evaluate First)
- **browser-use** (MIT) — AI browser agent, Python-based
- **Stagehand** (MIT) — AI browser agent, TS-based
- **n8n** — workflow automation (⚠️ source-available/fair-code license, NOT standard OSS)
- **Crawlee** — web scraping framework (Apify)

### Recommendation
Pick **one** AI-browser abstraction for v2 (Stagehand or browser-use), not both.

---

## Fastest Path to v2.0 (Codex's Recommendation)

### Scope Lock
v2.0 = secure modularization + spawn-tracked agents + memory + terminal tabs + CLI

**v2.0 IS**:
- Modular codebase (split monolith)
- Secure IPC (no nodeIntegration in renderer)
- Agent creation via CLI
- PID-tracked agent processes (no false positives)
- Markdown memory that survives restart
- Terminal tab per agent
- Single business only

**v2.0 IS NOT**:
- Professional dashboard mode
- Visual workflow builder
- Multi-business
- 15 platform integrations
- Cloud deployment
- Browser agent

### 4-Sprint Execution Plan

**Sprint 1: Split Monolith + Secure IPC**
- Extract index.html into modules (canvas, agents, ui, services)
- Add Vite build system
- Move to contextBridge + preload.js
- Remove API keys from renderer process
- Move secrets to OS keychain

**Sprint 2: Agent Supervisor**
- Spawn registry with PID tracking
- Restart policy (agent crashes → auto-restart)
- Fix process detection (match full binary path)
- Track our own spawned PIDs separately

**Sprint 3: Memory + Heartbeat**
- Markdown-based memory per agent
- Heartbeat summarization (every 30min)
- SQLite FTS5 index for memory search
- State dump on shutdown, restore on startup

**Sprint 4: CLI + Terminal + Package**
- `agentoffice` CLI: create, list, msg, task, status
- Terminal multiplexing (node-pty + xterm.js)
- Smoke tests: 3 agents concurrent, survive restart, retain memory
- Package with Electron Forge

### Ship Gate
Reproducible demo where 3 agents run tasks concurrently, survive restart, and retain memory with zero false-positive process detection.

---

## Key Sources
- Playwright: https://playwright.dev/
- browser-use: https://github.com/browser-use/browser-use
- Stagehand: https://github.com/browserbase/stagehand
- BullMQ: https://docs.bullmq.io/
- Notion auth: https://developers.notion.com/guides/get-started/authorization
- Google auth: https://developers.google.com/workspace/guides/auth-overview
- Slack signing: https://docs.slack.dev/authentication/verifying-requests-from-slack/
- Telegram bots: https://core.telegram.org/bots
- GitHub App auth: https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app
- Stripe keys: https://docs.stripe.com/keys
- X API pricing: https://docs.x.com/x-api/getting-started/pricing
- LinkedIn access: https://learn.microsoft.com/en-us/linkedin/shared/authentication/getting-access
- WhatsApp pricing: https://business.whatsapp.com/products/platform-pricing
- Litestream: https://litestream.io/guides/s3/

---

*Generated by Codex (gpt-5.3-codex) — 242,277 tokens used, 40+ web searches*
*Date: 2026-03-11*
