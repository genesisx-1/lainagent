# Agent Office Evolution Plan

> **Vision**: A self-sustaining AI workforce platform where CLI-based agents think, communicate, remember, and run businesses autonomously — deployable anywhere, controllable from anywhere, with zero API key dependency on the frontend. Inspired by OpenClaw's architecture but built for multi-agent teams instead of a single assistant.

---

## Core Philosophy

- **Agents are employees, not API calls.** Each agent is a persistent process with memory, personality, and a terminal. You hire them, assign them roles, and they work.
- **CLI-first.** Every agent runs off terminal commands (claude, gemini, codex, qwen, ollama, etc.). No API keys in the frontend. The backend spawns CLI processes — the UI just watches and talks to them.
- **Skills & Workflows over prompts.** Reusable, shareable automation scripts (like OpenClaw skills) that agents can execute. Build once, run forever.
- **Offline-capable.** When cloud tokens run dry, agents swap to local LLMs (ollama, llama.cpp, localai) seamlessly. Same agent, different brain. No downtime.
- **Survives shutdown.** Every agent writes memory to disk as Markdown files. On restart, they pick up where they left off — conversations, tasks, context, everything.
- **Multi-business.** One install can run multiple businesses, each with its own agents, CRM, leads, and workflows.
- **Platform-connected.** Notion, Gmail, Telegram, Slack — agents live where you work, not just in the app.

---

## Phase 1: Foundation — Modularize & Fix (Current → v2.0)

**Goal**: Break the monolith, fix what's broken, make it extensible.

### 1.1 Split the Monolith
- Break `index.html` (4000 lines) into modules:
  ```
  src/
    main.js              # Electron main process
    preload.js           # Secure bridge (no more nodeIntegration: true)
    renderer/
      app.js             # Entry point
      canvas/
        office.js        # Pixel art rendering
        sprites.js       # Agent sprites, NPCs, cat
        rooms.js         # Room layouts & furniture
        effects.js       # Particles, weather, day/night
      agents/
        manager.js       # Agent lifecycle (create, start, stop, monitor)
        process.js       # Process detection (fixed)
        memory.js        # Agent memory persistence
        communication.js # Inter-agent messaging
      ui/
        panels.js        # Right-side tab panels
        chat.js          # Chat panel system
        kanban.js        # Task board
        crm.js           # CRM views
        settings.js      # Config UI
      services/
        tasks.js         # Task queue & dispatch
        database.js      # SQLite wrapper
        cli.js           # CLI command builder & runner
  ```
- Add build system (Vite + Electron Forge) for hot reload and imports
- Move to `contextBridge` / `preload.js` for security (no raw `require` in renderer)

### 1.2 Fix Process Detection
- Tighten matching rules — eliminate false positives from macOS system agents
- Match on full binary path, not just `comm` column
- Add PID tracking to distinguish our spawned agents from system processes
- Track agents we spawn ourselves (known PIDs) separately from detected processes
- **Known bug**: Cursor agent matches `distnoted agent`, `UserEventAgent`, `WallpaperAgent`, etc.

### 1.3 Agent Memory System (OpenClaw-Inspired)
- Adopt **Markdown-based memory** like OpenClaw (simple, readable, portable):
  ```
  data/agents/{agent-name}/
    MEMORY.md            # Long-term memory (key facts, preferences, learnings)
    context.md           # Current working context & active tasks
    conversations/       # Chat history as markdown logs
      2026-03-11.md
    tasks/               # Completed task results
    skills/              # Agent-specific skill overrides
  ```
- On shutdown: agents dump current state to memory files
- On startup: agents load memory into their system prompt and resume
- **Heartbeat memory** (from OpenClaw): every N minutes, agent reviews what it learned and writes to MEMORY.md
- Memory summarization: periodically compress old conversations into key facts
- Agents can read each other's memory files for knowledge transfer

---

## Phase 2: Agent Engine — CLI Terminals & Employee System (v2.0 → v3.0)

**Goal**: Agents become real employees you create and manage through terminals.

### 2.1 Agent Creation System
```bash
# Create a new agent employee
agentoffice create "Sales Bot" --cli gemini --role sales --department leads

# Create with a local LLM fallback
agentoffice create "Research Agent" --cli claude --fallback ollama:llama3 --role researcher

# Create from a template
agentoffice create "Lead Gen" --template lead-generator

# List all agents
agentoffice list

# Talk to the head agent
agentoffice msg "Hey Claude, research competitors in the CRM space"

# Assign a task
agentoffice task "Scrape top 50 SaaS companies" --to qwen --priority high

# Check status
agentoffice status
```

- **Agent config file** per employee:
  ```json
  {
    "id": "sales-bot-001",
    "name": "Sales Bot",
    "displayName": "Sarah",
    "avatar": "path/to/photo.png",
    "cli": "gemini",
    "fallbackCli": "ollama run llama3",
    "role": "sales",
    "department": "lead-generation",
    "systemPrompt": "You are a sales specialist...",
    "memory": "data/agents/sales-bot-001/",
    "schedule": { "active": "09:00-17:00", "timezone": "America/New_York" },
    "permissions": ["web-scrape", "email-draft", "crm-write", "browser"],
    "skills": ["lead-scraper", "email-writer", "crm-updater"],
    "tokenBudget": { "daily": 100000, "fallbackAfter": 80000 }
  }
  ```

### 2.2 Terminal Per Agent
- Each agent gets its own embedded terminal in the UI
- See exactly what commands are running, what output comes back
- Live view of agent "thinking" (streaming CLI output)
- Tab system: switch between agent terminals like browser tabs
- Show which tabs/tasks each agent has open
- Terminal history saved and searchable

### 2.3 CLI Swapping (Cloud → Local LLM)
- Token usage tracking per agent per day
- When cloud budget hits threshold → auto-swap to local LLM CLI:
  ```
  claude → ollama run deepseek-r1
  gemini → ollama run gemma2
  codex  → ollama run codellama
  qwen   → ollama run qwen2.5
  ```
- Swap is seamless — agent keeps same memory/context, just different brain
- User can force-swap anytime: `agentoffice swap "Sales Bot" --cli ollama:llama3`
- Priority system: use cloud for complex tasks, local for simple ones
- **Smart routing**: classify task complexity → pick cloud or local automatically
- Dashboard shows token burn rate and estimated time until swap

### 2.4 Inter-Agent Communication (Real)
- Agents can @ mention each other in their CLI prompts
- Shared message bus (SQLite `agent_messages` table, upgraded):
  - Threaded conversations
  - Priority levels (urgent, normal, fyi)
  - File attachments (pass file paths between agents)
- **Live conversation view** — watch agents talk to each other in real-time
- Communication log with search and filters
- Head agent (Claude) can delegate and coordinate automatically
- Conversation panel shows all active threads + typing indicators

---

## Phase 3: Skills & Workflows — Reusable Automation (v3.0 → v3.5)

**Goal**: Build a library of reusable automations that agents can execute. Inspired by OpenClaw's skill system but designed for multi-agent teams.

### 3.1 Skill System

Skills are **Markdown files with YAML frontmatter** that teach agents how to do specific things. Simple to write, easy to share, no compilation needed.

```
skills/
  lead-scraper/
    SKILL.md             # Skill definition (instructions + config)
    templates/           # Email templates, prompt templates
    scripts/             # Helper scripts (Python, bash, etc.)
  email-writer/
    SKILL.md
  competitor-monitor/
    SKILL.md
  website-builder/
    SKILL.md
```

**SKILL.md format** (OpenClaw-compatible concept):
```markdown
---
name: lead-scraper
description: Scrape websites for leads and add them to CRM
version: 1.0.0
agent: any
requires:
  - web-scrape
  - crm-write
inputs:
  - url: string (required)
  - depth: number (default: 1)
outputs:
  - contacts: array
  - emails: array
triggers:
  - keyword: "scrape leads"
  - keyword: "find contacts"
  - schedule: "0 9 * * MON"
---

# Lead Scraper

## Instructions
1. Navigate to the provided URL
2. Extract all contact information (emails, phone numbers, names)
3. For each email found, create a contact in the CRM
4. Score each lead based on relevance to current business
5. Return a summary of findings

## Rules
- Skip generic emails (info@, support@, noreply@)
- Limit to 100 contacts per run
- Respect robots.txt
```

### 3.2 Workflow Engine (Pipelines)

Workflows chain multiple skills and agents together into repeatable pipelines:

```yaml
# workflows/daily-lead-pipeline.yml
name: Daily Lead Pipeline
description: Full lead gen pipeline that runs every morning
schedule: "0 9 * * *"
trigger: manual | schedule | webhook | file-upload

steps:
  - id: scrape
    agent: qwen
    skill: lead-scraper
    inputs:
      urls: "$file:target-websites.txt"
      depth: 2
    outputs: [contacts, emails]

  - id: research
    agent: gemini
    skill: lead-researcher
    inputs:
      contacts: "$step:scrape.contacts"
    outputs: [enriched_contacts]
    parallel: true  # Research multiple leads simultaneously

  - id: score
    agent: claude
    skill: lead-scorer
    inputs:
      leads: "$step:research.enriched_contacts"
      criteria: "$file:scoring-criteria.md"
    outputs: [scored_leads]

  - id: outreach
    agent: claude
    skill: email-writer
    inputs:
      leads: "$step:score.scored_leads"
      filter: "score > 7"
      template: "skills/email-writer/templates/cold-outreach.md"
    outputs: [draft_emails]

  - id: review
    agent: human  # Pause for human review
    action: approve-drafts
    inputs:
      drafts: "$step:outreach.draft_emails"

  - id: send
    agent: browser
    skill: email-sender
    inputs:
      emails: "$step:review.approved"
    condition: "$step:review.approved_count > 0"

notifications:
  on_complete: [telegram, feed]
  on_error: [telegram]
```

### 3.3 Workflow Builder UI
- Visual drag-and-drop pipeline builder
- Connect skill blocks with arrows (input → output)
- Test workflows step-by-step
- See live execution progress
- History of all workflow runs with results
- Clone and modify existing workflows

### 3.4 Built-in Skill Library (Ships with App)

| Skill | What It Does | Default Agent |
|-------|-------------|---------------|
| `lead-scraper` | Scrape websites for contacts | Qwen |
| `lead-researcher` | Enrich leads with company/LinkedIn data | Gemini |
| `lead-scorer` | Score leads by relevance and potential | Claude |
| `email-writer` | Draft personalized outreach emails | Claude |
| `email-sender` | Send emails via Gmail/SMTP | Browser |
| `competitor-monitor` | Track competitor website changes | Qwen |
| `website-builder` | Generate and deploy websites | Codex |
| `content-writer` | Blog posts, social media, copy | Claude |
| `data-analyzer` | Analyze CSVs, databases, reports | Qwen |
| `web-researcher` | Deep research on any topic | Gemini |
| `social-poster` | Post to Twitter/LinkedIn/Instagram | Browser |
| `invoice-generator` | Create invoices from CRM deals | Qwen |
| `meeting-scheduler` | Schedule via Google Calendar | Gemini |
| `code-reviewer` | Review PRs and code quality | Codex |
| `file-organizer` | Sort and categorize uploaded files | Qwen |

### 3.5 Community Skills (Future)
- Publish skills to a shared registry
- Install community skills: `agentoffice install skill competitor-tracker`
- Rate and review skills
- Version control for skills (git-backed)

---

## Phase 4: Research & Browser Agent (v3.5 → v4.0)

**Goal**: Agents can browse the web, do deep research, and interact with websites.

### 4.1 Browser Agent Integration
- Integrate open-source browser automation:
  - **Playwright** for headless browsing
  - **browser-use** (open source AI browser agent)
  - **Stagehand** (open source web agent framework)
- Agent capabilities:
  - Navigate websites, fill forms, extract data
  - Take screenshots and analyze them with vision models
  - Monitor competitor websites for changes
  - Automated social media posting
  - Website testing and QA
- Browser sessions visible in agent terminal tab
- Screenshot gallery of what the browser agent sees

### 4.2 Deep Research Mode
- Multi-step research workflow:
  1. User asks a question or provides a topic
  2. Research agent (Gemini) creates a research plan
  3. Browser agent crawls relevant sources
  4. Research agent synthesizes findings into a report
  5. Report saved to file manager with sources cited
- Research outputs: Markdown reports, summaries, data tables
- Source tracking — every claim linked to its source URL
- Research library — searchable archive of past research

### 4.3 Website Builder
- Agent can create websites using browser agent + code generation:
  - Claude/Codex: generates code (HTML/CSS/JS, Next.js, etc.)
  - Browser Agent: previews, tests, takes screenshots for iteration
  - Deploy to Vercel/Netlify/Cloudflare via CLI
- Template library for common site types (landing page, SaaS, portfolio)
- Agent iterates based on visual feedback (screenshot → adjust → screenshot)
- Live preview URL shared in chat

---

## Phase 5: File & Document Management (v4.0 → v4.5)

**Goal**: Full file system for agents — upload, organize, search, and use documents across all workflows.

### 5.1 File Manager
```
data/files/
  {business-name}/
    uploads/             # Files uploaded by user
    generated/           # Files created by agents
    templates/           # Reusable templates
    research/            # Research reports and sources
    exports/             # CRM exports, reports, invoices
```

- **Upload from Mac**: drag-and-drop in UI or CLI
  ```bash
  agentoffice upload ./leads.csv --to "Sales Bot" --business my-agency
  agentoffice upload ./brief.pdf --tag "project-alpha"
  ```
- **File browser panel** in UI:
  - Tree view of all files per business
  - Preview files inline (PDF, images, CSV, Markdown)
  - Search across all file contents
  - Tag and categorize files
  - See which agent created/modified each file
  - Version history for modified files

### 5.2 Document Processing
- Agents can read and process uploaded documents:
  - PDFs → extract text, summarize, answer questions
  - CSVs → analyze data, generate charts, find patterns
  - Images → OCR, describe, extract info
  - Spreadsheets → parse, transform, import to CRM
- Auto-processing rules: "When a CSV is uploaded to /leads, run the lead-importer skill"

### 5.3 Shared Knowledge Base
- **Wiki-style knowledge base** per business:
  - Agents contribute research findings, process docs, how-tos
  - Searchable by all agents (loaded into context when relevant)
  - User can edit and curate
  - Linked from agent memory files
- Knowledge base feeds into agent system prompts for better context

---

## Phase 6: Task Pipeline & CRM (v4.5 → v5.0)

**Goal**: Proper task management, lead pipelines, and multi-business CRM.

### 6.1 Task Pipeline System
- **Task states**: `inbox` → `queued` → `assigned` → `in_progress` → `review` → `done` / `failed`
- **Task types**:
  - One-shot (single agent, single action)
  - Pipeline (multi-step, multi-agent workflow)
  - Recurring (scheduled, repeats on cron)
  - Triggered (fires on event: file upload, email received, webhook)
- **Task assignment**:
  - Auto-dispatch by keyword rules (existing)
  - Smart dispatch by agent workload + capability
  - Manual assignment via UI or CLI
  - Head agent (Claude) can reassign based on priority
- **Task dependencies**: Task B waits for Task A to complete
- **Task board views**:
  - Kanban (drag between columns)
  - List (sortable, filterable)
  - Timeline (Gantt-style)
  - Calendar (scheduled tasks)

### 6.2 Lead Pipeline (Enhanced CRM)
- **Pipeline stages**: `prospect` → `contacted` → `meeting` → `proposal` → `negotiation` → `won` / `lost`
- **Per-lead tracking**:
  - All agent interactions logged
  - Emails sent/received
  - Research notes
  - Score history
  - Files attached
  - Revenue value
- **Pipeline views**:
  - Kanban board (drag leads between stages)
  - Table view with filters
  - Revenue forecast chart
  - Conversion funnel visualization
- **Automated actions per stage**:
  - Move to "contacted" → agent drafts follow-up email
  - Move to "meeting" → agent creates calendar event
  - Move to "won" → agent generates invoice

### 6.3 Multi-Business Management
```
businesses/
  my-saas-company/
    config.json          # Business name, domain, branding, colors
    agents.json          # Which agents work here + their roles
    crm.db               # Business-specific CRM database
    workflows/           # Business-specific workflows
    skills/              # Business-specific skill overrides
    files/               # Business files and documents
    knowledge/           # Business knowledge base
  my-agency/
    config.json
    ...
```
- **Business switcher** in UI header (dropdown)
- Each business has its own:
  - Agent team (agents can be shared or dedicated)
  - CRM with separate contacts, leads, pipeline
  - Task queue and workflows
  - File storage
  - Knowledge base
  - Branding/colors in UI
- **Cross-business dashboard**: see all businesses at a glance
- **Business templates**: "Start an e-commerce business" → pre-configured agents + workflows

---

## Phase 7: UI Modes — Gamified & Professional (v5.0 → v5.5)

**Goal**: Two UI modes — fun pixel art and serious business dashboard.

### 7.1 Mode Toggle (Top-Level Switch)
- **Gamified Mode** (current pixel art office, enhanced):
  - Agents walk around, sit at desks, go to break room
  - Customizable avatars (upload photos mapped to pixel sprites)
  - Achievements, XP, level-ups based on tasks completed
  - Office decorations unlock as milestones hit
  - Fun animations when tasks complete (confetti, celebrations)
  - Office cat interacts with agents
  - Sound effects and ambient office sounds
  - Multiple office floors / rooms to unlock

- **Professional Mode** (clean CRM/dashboard):
  - **Main tabs across the top**:
    - **Dashboard** — overview cards (active agents, tasks today, leads, revenue)
    - **Agents** — agent cards with status, current task, live terminal output
    - **Tasks** — kanban + list + timeline views
    - **Pipelines** — lead pipeline, workflow runs, active automations
    - **CRM** — contacts, leads, deals, companies
    - **Files** — file browser, uploads, generated docs
    - **Research** — research library, active research tasks
    - **Workflows** — workflow editor, skill library, run history
    - **Conversations** — all inter-agent chats, live + historical
    - **Analytics** — charts, token usage, costs, task metrics
    - **Settings** — agents, integrations, businesses, CLI config
  - Clean, minimal UI — no pixel art, no animations
  - Think: Linear meets Retool meets HubSpot

### 7.2 Agent Customization
- Upload photos for each agent → shown in both modes
  - Gamified: photo mapped to pixel sprite or shown as profile pic
  - Professional: photo on agent card + chat messages
- Custom names, titles ("Head of Sales"), bios
- Personality settings (formal, casual, creative, analytical)
- Custom system prompts per agent
- Color themes per agent
- Custom notification sounds

### 7.3 Live Conversation Viewer
- See all inter-agent conversations in real-time
- Filter by agent, topic, business, date
- Searchable conversation history
- Highlight when agents are actively talking
- Show "typing" indicators (streaming CLI output)
- Thread view for complex multi-agent discussions
- Timestamp + duration for each message
- Export conversations as Markdown/PDF

---

## Phase 8: Connectivity — Integrations & Remote Access (v5.5 → v6.0)

**Goal**: Connect to external services, control from anywhere.

### 8.1 Platform Connectors (Easy Setup)

Each connector is a simple config — no code needed:

```yaml
# integrations/notion.yml
type: notion
auth: oauth  # or api-key
capabilities:
  - read-databases
  - create-pages
  - sync-tasks
sync:
  tasks: both-ways        # Tasks sync between app and Notion
  contacts: app-to-notion  # Push CRM contacts to Notion
```

**Supported Platforms**:

| Platform | Capabilities | Agent Use |
|----------|-------------|-----------|
| **Notion** | Read/write pages, databases, sync tasks | Knowledge base, task sync, wiki |
| **Gmail** | Read inbox, draft, send, search | Outreach, follow-ups, notifications |
| **Google Calendar** | Create/read events, availability | Meeting scheduling, task deadlines |
| **Google Sheets** | Read/write spreadsheets | Data import/export, reporting |
| **Google Drive** | File storage, sharing | Document management |
| **Slack** | Send/read messages, channels | Team notifications, agent commands |
| **Discord** | Bot messages, channels | Community management |
| **Telegram** | Bot interface, commands | Remote control (see 8.2) |
| **GitHub** | Issues, PRs, code, actions | Dev workflow, code review |
| **Twitter/X** | Post, read, engage | Social media management |
| **LinkedIn** | Post, research profiles | Lead research, content posting |
| **WhatsApp** | Send/receive messages | Client communication |
| **Stripe** | Invoices, payments, customers | Revenue tracking |
| **Zapier/n8n** | Webhook triggers, 1000+ apps | Connect to anything |

### 8.2 Telegram Bot Interface
- Deploy a Telegram bot connected to head agent
- Commands:
  ```
  /task "Research competitors" — assign a task
  /status — get agent status overview
  /chat claude "What's the lead count?" — talk to specific agent
  /business switch my-agency — switch active business
  /upload — send files to agents (photos, PDFs, docs)
  /report — get daily summary
  /workflow run daily-leads — trigger a workflow
  /approve 3 — approve pending item #3
  ```
- Receive notifications: task completions, agent alerts, lead updates
- Forward urgent agent messages to your phone
- Voice messages transcribed and sent as tasks
- **Text the head agent conversationally** — just send a message, Claude figures out what to do

### 8.3 File Upload & Sync
- Upload files from Mac → agent workspace
- Drag-and-drop in UI or CLI: `agentoffice upload ./report.pdf --to "Research Agent"`
- Telegram: send any file to the bot → auto-routed to the right agent
- Shared file storage per business
- Agents can reference uploaded files in their work
- Google Drive sync for automatic backup

---

## Phase 9: Deployment — Run Anywhere (v6.0 → v7.0)

**Goal**: Agents run 24/7 without your Mac being on.

### 9.1 Cloud Deployment Options
- **Docker container** — single image with all agents:
  ```bash
  docker run -d agentoffice/server \
    --business my-saas \
    --agents "claude,gemini,qwen" \
    --telegram-token xxx
  ```
- **VPS deployment** (DigitalOcean, Hetzner, AWS Lightsail):
  - $5-20/mo for always-on agents
  - One-command provisioning script
  - Auto-install all CLI tools + Ollama
- **AWS Lightsail OpenClaw-style** — pre-built AMI (like OpenClaw offers)
- **Headless mode** — no Electron, just agent engine + API:
  - REST API for all operations
  - Web dashboard (React, accessible from any browser)
  - Telegram/Slack as primary interface when headless

### 9.2 Mac ↔ Cloud Sync
- Local Mac app connects to remote deployment
- Real-time sync of:
  - Agent memory and conversations
  - Task queue and results
  - CRM data
  - File uploads
  - Workflow definitions
- Work locally when online, agents continue in cloud when Mac is off
- Sync via SQLite replication (Litestream) or simple REST API
- Conflict resolution: cloud wins for agent-generated, local wins for user-edited

### 9.3 Local LLM on Server
- Install Ollama on the VPS alongside CLI tools
- Agents use local models for routine tasks (saves tokens)
- Cloud LLMs only for complex reasoning
- Cost optimization: $5/mo VPS + minimal API usage
- **GPU VPS option**: Hetzner/Lambda for faster local inference

---

## Phase 10: Intelligence & Autonomy (v7.0 → v8.0)

**Goal**: Agents get smarter over time, work more autonomously.

### 10.1 Heartbeat System (From OpenClaw)
- Every N minutes (configurable, default 30), each active agent:
  1. Reviews its current tasks and context
  2. Checks for new messages or events
  3. Writes learnings to memory
  4. Only alerts user if something needs attention
- Enables **proactive behavior**:
  - "I noticed the competitor updated their pricing page"
  - "3 leads haven't been contacted in 5 days, should I follow up?"
  - "The daily scrape found 12 new contacts"

### 10.2 Agent Learning
- Agents summarize what they learned from each task
- Build knowledge base per business domain
- Share learnings between agents (knowledge transfer via shared memory)
- User feedback loop: rate agent outputs → agent adjusts approach
- Pattern recognition: "You always modify my email drafts the same way, I'll adjust"

### 10.3 Multi-Agent Reasoning
- Agents can have group discussions on complex problems
- **Debate mode**: two agents argue different approaches, third decides
- **Peer review**: one agent checks another's work before delivery
- **Escalation chain**: stuck agent → head agent → user (only if head agent can't solve)
- **Pair work**: two agents collaborate on same task in real-time

### 10.4 Autonomous Workflows
- Agents can propose new workflows based on patterns they notice
- "I've been doing these 3 steps manually every day — should I create a workflow?"
- Auto-optimize: if a workflow step consistently fails, agent suggests alternatives
- Self-healing: if a step fails, agent retries with different approach before alerting user

---

## Technical Architecture (Target State)

```
agent-office/
  src/
    main/                    # Electron main process
      index.js
      preload.js
      ipc-handlers.js       # IPC bridge to renderer
    renderer/                # Frontend (Electron renderer)
      app.js
      views/
        gamified/            # Pixel art office mode
          canvas.js
          sprites.js
          rooms.js
          effects.js
        professional/        # Clean dashboard mode
          dashboard.js
          agents-view.js
          tasks-view.js
          pipeline-view.js
          crm-view.js
          files-view.js
          research-view.js
          workflows-view.js
          conversations-view.js
          analytics-view.js
          settings-view.js
      components/            # Shared UI components
        chat-panel.js
        agent-card.js
        terminal.js
        file-browser.js
        kanban-board.js
      stores/                # State management
        agents-store.js
        tasks-store.js
        files-store.js
    engine/                  # Core agent engine (runs in main process)
      agent-manager.js       # Create, start, stop, monitor agents
      cli-runner.js          # Spawn and manage CLI processes
      memory-store.js        # Markdown-based agent memory
      message-bus.js         # Inter-agent communication
      task-dispatcher.js     # Task routing and execution
      workflow-engine.js     # Workflow/pipeline execution
      skill-loader.js        # Load and parse SKILL.md files
      heartbeat.js           # Periodic agent check-in system
      token-tracker.js       # Usage tracking + CLI swap logic
      browser-agent.js       # Playwright/browser-use integration
    integrations/            # Platform connectors
      notion.js
      google/
        gmail.js
        calendar.js
        sheets.js
        drive.js
      telegram.js
      slack.js
      github.js
      zapier.js
    server/                  # Headless mode / API server
      api.js                 # REST API for all operations
      websocket.js           # Real-time updates to UI
      telegram-bot.js        # Telegram bot server
    cli/                     # `agentoffice` CLI tool
      index.js
      commands/
        create.js            # Create agent
        task.js              # Assign task
        msg.js               # Message agent
        upload.js            # Upload file
        status.js            # Check status
        workflow.js          # Run/manage workflows
        deploy.js            # Deploy to cloud
  data/
    agents/                  # Per-agent memory, context, conversations
    businesses/              # Per-business config, CRM, files
    skills/                  # Shared skill library
    workflows/               # Workflow definitions
    files/                   # Uploaded and generated files
    crm.db                   # SQLite database (default business)
  skills/                    # Built-in skills (ship with app)
    lead-scraper/SKILL.md
    email-writer/SKILL.md
    web-researcher/SKILL.md
    ...
  scripts/                   # Python utility scripts (legacy, migrate to skills)
  docker/                    # Docker deployment
    Dockerfile
    docker-compose.yml
```

---

## What Makes This Different From OpenClaw

| | OpenClaw | Agent Office (Ours) |
|---|---------|-------------------|
| **Architecture** | Single agent, single brain | Multi-agent team with roles & departments |
| **Interface** | Chat-only (messaging apps) | Full GUI (gamified + professional) + chat + CLI + Telegram |
| **Business focus** | Personal assistant | Multi-business CRM + lead gen + automation |
| **Agent creation** | One agent, you configure it | Create unlimited agents with different CLIs and roles |
| **Visualization** | None (text-only) | Pixel art office + dashboard + live conversation viewer |
| **CRM** | No built-in CRM | Full CRM with pipeline, leads, contacts, deals |
| **Workflows** | Skills + pipelines | Skills + visual workflow builder + multi-agent pipelines |
| **Collaboration** | N/A (single agent) | Agents debate, peer review, delegate, escalate |
| **File management** | Markdown memory only | Full file manager with uploads, search, processing |
| **Offline** | Supports Ollama | Auto-swap cloud↔local based on token budget |

**We're not competing with OpenClaw — we're building on top of the same ideas but for teams of agents running businesses, not a single personal assistant.**

---

## Naming Ideas

The project needs a new name. Some options:

- **HiveDesk** — agents working together like a hive
- **CrewStation** — crew of AI agents at their stations
- **AgentForge** — forge/create your own agents
- **BossAI** — you're the boss, they're the employees
- **TerminalCrew** — CLI-native agent workforce
- **Nexus Office** — nexus of AI agents
- **The Agency** — simple, clean, on-brand
- **ClawDesk** — nod to OpenClaw heritage, desk = workspace
- **HireAI** — you hire AI employees
- **ShiftWork** — agents working in shifts, 24/7

(Pick one or brainstorm more — can rename anytime)

---

## Priority Order

1. **Phase 1** — Modularize (required for everything else)
2. **Phase 2** — Agent creation + CLI terminals + swap (core value prop)
3. **Phase 3** — Skills & Workflows (reusable automation)
4. **Phase 5** — File & document management (agents need to work with files)
5. **Phase 6** — Task pipelines + CRM (business operations)
6. **Phase 7** — Dual UI modes (gamified + professional)
7. **Phase 4** — Browser agent + research (high-impact features)
8. **Phase 8** — Platform integrations + Telegram (remote control)
9. **Phase 9** — Cloud deployment (24/7 agents)
10. **Phase 10** — Intelligence & autonomy (agents get smarter)

---

## Open Questions

- [ ] Final name for the project?
- [ ] Ship as open-source from the start or go private first?
- [ ] Electron-only or also build a web version for headless mode?
- [ ] Build our own skill marketplace or integrate with OpenClaw's ClawHub?
- [ ] Which platforms to integrate first? (Notion + Gmail + Telegram seems like the starter pack)
- [ ] Pricing model if this becomes a product? (Free local + paid cloud hosting?)

---

*Last updated: 2026-03-11*
