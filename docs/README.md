# Agent Office

A multi-AI CLI orchestration system with a visual pixel-art office interface. Built with Electron. No server required.

## What It Does

Agent Office lets you manage, monitor, and communicate with multiple AI CLI agents from a single dashboard. Think of it as a virtual office where your AI agents walk around, work at desks, and respond to your commands — all running locally on your machine.

### Supported Agents

| Agent | CLI | Role | Dept |
|-------|-----|------|------|
| **Claude** | `claude` | Lead Dev / Commander | Lead Dev |
| **Codex** | `codex` | Second-in-command | Backend |
| **Gemini** | `gemini` | Research & Analysis | Research |
| **Cursor** | `agent` (cursor-agent) | Frontend / Editing | Frontend |
| **Qwen** | `qwen` | Data / Scripts / Python | Data Lab |

### Chain of Command

```
Claude -> Codex -> Qwen -> Gemini -> Cursor
```

When Claude is offline, Codex takes over as acting commander. If Codex is also offline, Qwen takes over, and so on.

---

## Features

### Visual Office (Canvas)
- 16px tile-based pixel-art office rendered on HTML5 Canvas at 2x scale
- Agents are sprites that walk around, sit at desks, visit the coffee machine, and interact
- 4 rooms: **Office** (main), **Server Room**, **Break Room**, **Data Lab**
- Office cat that wanders, follows agents, and sleeps
- Visitor NPCs spawned from detected dev processes (webpack, vite, python, etc.)
- Day/night cycle based on real time, weather effects (rain, clouds, stars)
- Ambient dust particles, footstep trails, confetti on task completion
- Agent accessories: hat, glasses, mug, headphones, goggles

### Process Detection
- Scans running processes every 4 seconds using `ps axo pid,pcpu,rss,comm,args`
- Detects each agent by matching the `comm` column (e.g., `claude`, `gemini`, `codex`)
- Tracks CPU%, memory, PID, uptime, and active project directory
- Shows online/offline transitions with particle effects and sound

### Click-to-Chat (v6)
- **Click any agent** (canvas or sidebar) to open a floating chat panel
- Type a message, it gets sent to the agent's CLI asynchronously via `spawn`
- Agent responds in real-time — no blocking
- **Multiple chats run in parallel** — talk to Gemini and Codex simultaneously
- Panels are draggable, resizable, color-coded per agent
- All conversations saved to the CRM database
- CLI commands used:
  - Claude: `claude -p "..." --yolo`
  - Gemini: `gemini -p "..." --yolo -o text`
  - Codex: `codex exec "..."`
  - Cursor: `agent -p "..." --yolo --output-format text`
  - Qwen: `qwen -p "..." --yolo`

### Right Panel Tabs

| Tab | What It Does |
|-----|-------------|
| **Feed** | Live activity log — agent status changes, messages, task events |
| **Term** | Terminal output from each agent (files they're touching) |
| **Stats** | CPU, memory, uptime per agent + system stats |
| **Timeline** | Visual timeline of agent activity throughout the day + git log |
| **Tasks** | Kanban board (Todo / In Progress / Done) backed by `tasks.json` |
| **Auto** | Chain of command, auto-dispatch controls, workflow rules, dispatch log |
| **CRM** | Web scraper, contacts, leads, agent messaging |
| **Scripts** | Python script editor, AI code generation (Qwen/Gemini), quick actions |

### Task Queue & Auto-Dispatch
- File-backed task queue in `tasks.json`
- Tasks auto-classified by keywords:
  - `research` -> Gemini
  - `edit`, `refactor` -> Cursor
  - `generate`, `review` -> Codex
  - `scrape`, `data`, `analyze`, `script`, `python`, `database` -> Qwen
  - `plan` -> Claude
- One-click dispatch: sends task to agent CLI and captures result
- Dispatch All: batch-dispatch all todo tasks
- Custom workflow rules (trigger -> agent -> action)

### CRM System
- **SQLite database** (`crm.db`) with tables: contacts, leads, scrape_results, scripts, agent_messages
- **Web Scraper**: Enter a URL, scrapes with Python (requests + BeautifulSoup), extracts title, content, links, emails, phone numbers
- **AI Scrape**: Scrape + send to Gemini for business analysis
- **Auto-contact creation**: Emails found during scraping are automatically added as contacts
- **Agent Messages**: Inter-agent messaging stored in database
- **Python Scripts**: Write/save/run Python scripts, AI-generate scripts via Qwen or Gemini

### Sound Engine
- Web Audio API synthesizer (no audio files needed)
- Sounds: click (typing), ding (task done), online (agent appears), step (walking), ambient (office hum)
- Toggle on/off from status bar

### Other Features
- Context menu (right-click agent): chat, inspect, send to coffee/water/couch, make wave/say
- Inspector panel: detailed agent info popup
- Minimap: bottom-right overview of all agent positions
- Log export: save feed to `~/agent-office-log.txt`
- Desktop notifications on agent status changes

---

## Project Structure

```
agent-office/
  main.js          # Electron main process
  index.html       # Entire app (styles + canvas + JS — single file)
  package.json     # Electron dependency
  tasks.json       # Persistent task queue + dispatch config
  crm.db           # SQLite database (auto-created)
  scripts/
    db.py          # CRM database CLI (init, add-contact, list, query, etc.)
    scrape.py      # Web scraper (requests + BeautifulSoup)
    run_script.py  # Execute saved Python scripts from DB
  docs/
    README.md      # This file
    ROADMAP.md     # Future features and ideas
```

## How to Run

```bash
cd ~/agent-office
npx electron .
```

Requirements:
- Node.js + npm
- Electron (`npm install` in the directory)
- Python 3 with `requests` and `beautifulsoup4` (for CRM features)
- Any combination of: `claude`, `gemini`, `codex`, `agent` (cursor), `qwen` CLIs installed

## Configuration

Edit `tasks.json` to customize:
- `chain_of_command`: Order of agent authority
- `dispatch_rules`: Keyword -> agent mapping for auto-classification
- `auto_dispatch`: Enable/disable automatic task routing

Edit `~/CLAUDE.md` for Claude's orchestration rules.
Edit `~/CODEX.md` for Codex's second-in-command behavior.
