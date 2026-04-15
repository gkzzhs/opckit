<p align="center">
  <h1 align="center">🏢 OPCKit</h1>
  <p align="center">
    <strong>AI Operating System for One-Person Companies</strong><br>
    Three AI departments (Marketing · Sales · Operations) sharing one local database — industry-configurable, 100% local data.
  </p>
  <p align="center">
    <img src="https://img.shields.io/badge/version-2.1.0-blue" alt="version">
    <img src="https://img.shields.io/badge/license-MIT-green" alt="license">
    <img src="https://img.shields.io/badge/Python-3.10+-yellow" alt="python">
    <img src="https://img.shields.io/badge/code-~300%20lines-blueviolet" alt="code">
    <img src="https://img.shields.io/badge/data-100%25%20local-brightgreen" alt="local data">
  </p>
  <p align="center">
    <a href="README.md">中文</a>
  </p>
</p>

---

## 😩 The Problem

You're a freelancer juggling clients, projects, and side hustles. You use plenty of AI tools — ChatGPT for copywriting, Claude for breaking down requirements, spreadsheets for bookkeeping, notes for managing clients.

But here's the thing: **these tools don't talk to each other.**

You are the human data bus — client info lives in chat histories, finances in random notes, content plans in your head. More tools, more fragmentation. More capability, more chaos.

**OPCKit doesn't give you 3 more tools. It gives you 3 AI departments that share context.**

## 🧭 Before / After

| | Before | After (OPCKit) |
|---|---|---|
| **Client management** | Scrolling through chat history | "Check clients" → see everything |
| **Bookkeeping** | Scribbled notes, can't reconcile | "Got 5000" → auto-categorized, monthly report in one command |
| **Content** | Post by gut feeling | Trend analysis → creation → repurpose → scheduling |
| **Follow-ups** | Rely on memory, often forget | Auto-reminders for stale clients, auto-update after contact |
| **Data silos** | Every tool on its own | Three departments share one database, data flows automatically |

## ⚡ Three Departments

| Department | Skill | Core Capabilities |
|------------|-------|-------------------|
| 📢 **Marketing** | `opckit-mkt` | Trend analysis · Content creation (multi-platform) · Repurpose · Content calendar · Performance tracking |
| 🤝 **Sales** | `opckit-sales` | Client profiling · Requirement breakdown · 3-tier quotes · Follow-up reminders + auto-mark · Deal & payment recording |
| 📊 **Operations** | `opckit-ops` | Bookkeeping · Business reports · Monthly reports · Morning/evening briefs (scheduled) · Payment collection |

**Key design: all three departments share the same SQLite database.** Marketing publishes content — Sales knows. Sales closes a deal — Operations records the income. Data flows between departments automatically.

## 🎯 Industry Configuration

Same framework, completely different templates per industry:

| Industry | Content Platforms | Pricing Reference | Follow-up Cycle |
|----------|------------------|-------------------|-----------------|
| 🎨 Designer | Dribbble, Behance, Instagram | Logo $300-800 | 3 days |
| 💻 Developer | Dev.to, GitHub, HackerNews | Website $800-2500 | 5 days |
| 📋 Consultant | LinkedIn, Medium | Consulting $80-300/h | 7 days |
| ✍️ Creator | Instagram, YouTube, TikTok | Sponsored post $200-1000 | 3 days |

Say "I'm a designer" on first use — configuration loads automatically. Custom templates supported.

## 📊 Real Business Data

The following is real data from the author running their own one-person company with OPCKit:

```
📊 Dashboard: Clients 5 | Income ¥8,800 Expense ¥520 | Content 3
```

| Data | Details |
|------|---------|
| Clients | Enterprise partner (with contract), AI community, competitions |
| Income | Monthly freelance pay + competition prizes |
| Content | GitHub open source projects + technical articles |

**Every record is real business data, not demo data.**

## 🚀 Quick Start

### Prerequisites

- [OpenClaw](https://github.com/anthropics/openclaw) installed
- Python 3.10+

### One-line Install

```bash
git clone https://github.com/gkzzhs/opckit.git
cd opckit
chmod +x install.sh
./install.sh
```

Then tell your Agent: **"I'm a designer"** to get started.

## 💬 Usage Examples

### Marketing
```
You: What design content is trending on social media?
AI: [Search analysis] Here are 3 hot topics this week...

You: Write me a post about 5 Logo design mistakes to avoid
AI: [Generates full content] ...

You: Published it, got 230 likes and 45 comments
AI: ✅ Status updated to "published", engagement data recorded.
```

### Sales
```
You: New client Mr. Zhang, restaurant industry, wants brand VI, budget $3000
AI: Confirm: Name Mr. Zhang, Industry Restaurant... Confirm?

You: Who needs follow-up?
AI: Mr. Zhang hasn't been contacted in 3 days, suggest sending a message...
    Let me know when you've reached out, I'll update the follow-up time.

You: Done
AI: ✅ Mr. Zhang's follow-up time updated to today.
```

### Operations
```
You: Got $1500 deposit from Mr. Zhang
AI: Confirm: Income $1,500, from Mr. Zhang... ✅

You: How's this month looking?
AI: [Business Report] Income $2,300 / Expense $480 / Net $1,820
    📌 Mr. Zhang hasn't been contacted in 5 days. Content output below plan.

You: Enable daily morning brief
AI: ✅ Set up daily briefing at 8 AM
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│              Conversation Layer               │
│          OpenClaw / QClaw / WorkBuddy         │
└──────────┬──────────┬──────────┬─────────────┘
           │          │          │
    ┌──────▼──┐ ┌─────▼────┐ ┌──▼───────┐
    │Marketing│ │  Sales    │ │Operations│
    │SKILL.md │ │ SKILL.md │ │ SKILL.md │
    └────┬────┘ └────┬─────┘ └────┬─────┘
         │           │            │
         └───────────┼────────────┘
                     │
              ┌──────▼──────┐
              │  db.py CLI   │
              │  (~300 lines)│
              └──────┬──────┘
                     │
              ┌──────▼──────┐
              │   SQLite     │
              │ opckit.db    │
              │ 3 tables     │
              └─────────────┘
```

- **Data layer:** SQLite (`~/.opckit/data/opckit.db`), three tables: `clients` / `ledger` / `content_log`
- **Config layer:** JSON industry templates (`~/.opckit/config/`), auto-loaded on first use
- **Interaction layer:** Pure SKILL.md (zero code), calls data operations via `python3 {baseDir}/scripts/db.py`
- **Safety design:** All write operations require user confirmation; list queries enforce limits; errors halt execution immediately

## 📁 Directory Structure

```
opckit/
├── src/db.py                  # Shared database CLI (only code file, ~300 lines)
├── install.sh                 # One-line installer
├── AGENTS.md                  # Agent orchestration config
├── opckit-mkt/
│   ├── SKILL.md               # Marketing Skill
│   └── scripts/db.py          # db.py copy
├── opckit-sales/
│   ├── SKILL.md               # Sales Skill
│   └── scripts/db.py          # db.py copy
├── opckit-ops/
│   ├── SKILL.md               # Operations Skill
│   └── scripts/db.py          # db.py copy
└── config/templates/          # Industry config templates
    ├── designer.json
    ├── developer.json
    ├── consultant.json
    └── creator.json
```

## 🔧 Custom Industry Templates

```bash
cp config/templates/designer.json config/templates/myindustry.json
# Edit platforms, pricing, follow-up cycles, etc.
```

Then tell your Agent "Initialize as myindustry" to load it.

## 🛡️ Design Principles

1. **AI assists, human decides** — All operations involving money or client data require user confirmation
2. **Data stays local** — SQLite stored in `~/.opckit/`, nothing uploaded to any cloud
3. **Errors don't hide** — When db.py fails, execution stops immediately and shows the raw error
4. **Categories don't drift** — Expense categories selected from a fixed enum, ensuring accurate report aggregation

## 📄 License

[MIT](LICENSE)

---

<p align="center">
  <strong>Not just AI doing one task for you — AI running an entire company for you.</strong>
</p>
