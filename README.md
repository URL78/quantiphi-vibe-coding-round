# 🚀 GitHub Developer Portfolio

> **Turn any GitHub username into a professional, interactive developer portfolio — with analytics, AI-powered repository insights, and job-description compatibility scoring.**

Built for the **Quantiphi Vibe Coding Assessment**.

---

## 📌 What Is This Project?

Imagine you want to show a recruiter how good you are as a developer — but instead of a traditional resume, you just hand them your GitHub username. This app does the rest.

You enter **any public GitHub username**, and within seconds the app:

1. **Fetches** that developer's GitHub profile and all their public repositories.
2. **Displays** a beautiful analytics dashboard — contribution heatmap, coding streaks, language distribution, starred repos, and more.
3. **Runs a "Vibe Check"** — you paste a job description, and the app tells you exactly which programming languages from that JD the developer already has in their portfolio (and which ones are missing).
4. **Gives career recommendations** on how to fill those skill gaps.
5. **Answers questions about any repo** using an AI called DeepWiki — like "how does the authentication work in this codebase?"

---

## 🖼️ How It Looks

```
┌─────────────────────────────────────────────────────────┐
│  🏠 Home  📊 Dashboard  📁 Portfolio  ⚡ Vibe Check  🧠 DeepWiki │
└─────────────────────────────────────────────────────────┘

Enter GitHub username: [ torvalds       ] [ Explore → ]

╔══════════════════════════════════════════════════════╗
║  Linus Torvalds    @torvalds                         ║
║  "Nothing better to do..."                           ║
║  👥 236k followers  ⭐ 42k stars  🍴 8k forks        ║
╠══════════════╦═══════════════╦══════════════════════╣
║ Languages    ║ Heatmap       ║ Streaks               ║
║ C       85%  ║ ░░▒▓█▒░▒▓█▒  ║ 🔥 Current: 12 days  ║
║ Shell    8%  ║ ░▒░░▒░▒▒▒░░  ║ 📈 Longest: 45 days  ║
║ Makefile 7%  ║               ║ 📅 Last: 2026-11-06  ║
╚══════════════╩═══════════════╩══════════════════════╝
```

---

## 🧩 Key Features

| Feature | What It Does |
|---|---|
| **GitHub Profile Sync** | Fetches profile picture, bio, followers, stars, forks, and repos |
| **Analytics Dashboard** | Visualizes contribution heatmap, language pie chart, coding streaks |
| **Repository Browser** | Lists all public repos — sortable by stars, recency, or name; with featured toggle |
| **⚡ Vibe Check** | Paste a job description → see % match of languages → get career improvement tips |
| **📁 Public Portfolio** | Shareable portfolio view with featured projects and latest Vibe Check score |
| **🧠 DeepWiki AI** | Ask any question about any repo in plain English ("How does X work?") |
| **Interview Prep** | Generate and evaluate technical interview questions about a repository |
| **Smart Caching** | GitHub data is cached in SQLite — no repeated API calls within 1 hour |

---

## 🏗️ How It's Built (Architecture)

```
┌─────────────────────┐         ┌──────────────────────────┐
│   React Frontend    │  HTTP   │    FastAPI Backend        │
│  (Vite + Tailwind)  │ ──────► │  (Python 3.10+)          │
│                     │         │                          │
│  • Dashboard UI     │         │  • GitHub REST API       │
│  • Vibe Check form  │ ◄────── │  • GitHub GraphQL API    │
│  • DeepWiki chat    │  JSON   │  • DeepWiki MCP          │
│  • Portfolio view   │         │  • SQLite (caching)      │
└─────────────────────┘         └──────────────────────────┘
         ↓                                  ↓
   Browser on                     portfolio.db (local file)
   localhost:5173                 auto-created on startup
```

The frontend **never** talks to GitHub or DeepWiki directly. All external calls go through the backend — keeping API tokens secure.

---

## 🛠️ Tech Stack

**Frontend**
- React 18 + Vite (lightning-fast dev server)
- Tailwind CSS v3 (dark-mode UI)
- React Router (page navigation)
- TanStack Query (data fetching + caching)
- Recharts (pie charts, bars)
- Lucide React (icons)
- Axios (HTTP client)

**Backend**
- Python 3.10+
- FastAPI (REST API framework with auto-generated docs)
- SQLAlchemy ORM + Alembic (database migrations)
- SQLite (zero-config local database)
- HTTPX (async HTTP calls to GitHub)
- Pydantic (request/response validation)
- Pytest (automated tests)

**External Services**
- GitHub REST API (profile + repositories)
- GitHub GraphQL API (contribution calendar — requires a token)
- DeepWiki MCP (`https://mcp.deepwiki.com/mcp`) — AI repo assistant

---

## 📁 Project Structure

```
quantiphi-vibe-coding-round/
│
├── frontend/                    ← React app (what users see)
│   ├── src/
│   │   ├── pages/               ← Full pages (Home, Dashboard, VibeCheck…)
│   │   ├── components/
│   │   │   ├── common/          ← Navbar, Spinner, StatCard, ErrorMessage
│   │   │   └── dashboard/       ← Charts, Heatmap, RepoList, StreakWidget
│   │   ├── services/api.js      ← All API calls to the backend
│   │   ├── context/             ← Global state (current user)
│   │   └── utils/               ← Formatters, language colour map
│   ├── tailwind.config.js
│   └── vite.config.js           ← Proxies /api → localhost:8000
│
├── backend/                     ← FastAPI app (the brain)
│   ├── app/
│   │   ├── main.py              ← App entry point, CORS, startup
│   │   ├── config.py            ← All settings loaded from .env
│   │   ├── database.py          ← SQLite engine + session factory
│   │   ├── api/endpoints/       ← One file per feature (profile, repos…)
│   │   ├── models/models.py     ← 6 database tables (SQLAlchemy ORM)
│   │   ├── schemas/schemas.py   ← Request/response shapes (Pydantic)
│   │   ├── services/            ← Business logic (GitHub, Vibe Check…)
│   │   ├── integrations/        ← DeepWiki MCP client
│   │   └── utils/               ← Helpers + 35-language dictionary
│   ├── tests/                   ← Pytest tests (mocked, no real API calls)
│   ├── alembic/                 ← Database migration scripts
│   └── requirements.txt
│
├── docs/                        ← Requirements, API spec, DB schema
├── UML diagrams/                ← Architecture, sequence, class diagrams
└── README.md                    ← You are here
```

---

## ⚙️ Setup & Run Locally

You need **Python 3.10+** and **Node.js 18+** installed.

### Step 1 — Clone the repo

```bash
git clone https://github.com/URL78/quantiphi-vibe-coding-round.git
cd quantiphi-vibe-coding-round
```

---

### Step 2 — Set up the Backend

```bash
cd backend
```

**Create a Python virtual environment:**

```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

> ⚠️ **Windows PowerShell tip:** If you see an error about execution policy, run this first:
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
> ```
> Then activate again.

**Install dependencies:**

```bash
pip install -r requirements.txt
```

**Configure environment variables:**

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Now open `backend/.env` in any text editor. It looks like this:

```env
GITHUB_TOKEN=            ← Add your GitHub token here (optional but recommended)
DATABASE_URL=sqlite:///./portfolio.db
DEEPWIKI_MCP_URL=https://mcp.deepwiki.com/mcp
FRONTEND_URL=http://localhost:5173
```

> 💡 **Should I add a GitHub token?**
> - Without a token: profile + repos work, but contribution heatmap won't load (GitHub requires auth for GraphQL).
> - With a token: everything works. Create one at [github.com/settings/tokens](https://github.com/settings/tokens) — only `read:user` scope is needed.

**Start the backend server:**

```bash
uvicorn app.main:app --reload
```

✅ Backend is running at **http://localhost:8000**

You can verify it's alive by opening: http://localhost:8000/health

Explore all API routes at: http://localhost:8000/docs ← *interactive API playground*

---

### Step 3 — Set up the Frontend

Open a **new terminal** (keep the backend running):

```bash
cd frontend
npm install
npm run dev
```

✅ Frontend is running at **http://localhost:5173**

Open your browser and go to **http://localhost:5173** 🎉

---

### Step 4 — Use the App

1. Enter any public GitHub username (e.g. `torvalds`, `gvanrossum`, `addyosmani`)
2. Click **Explore** — the app syncs the profile from GitHub (first load takes ~2–3 seconds)
3. You're on the **Dashboard** — explore stats, contributions, repos
4. Click **Vibe Check** → paste a job description → get your tech-stack match score
5. Click **DeepWiki AI** → ask anything about any GitHub repo

---

## 🔑 API Endpoints Reference

The API lives at `http://localhost:8000/api/v1`. Here are the main endpoints:

| Method | Endpoint | What It Does |
|--------|----------|-------------|
| `POST` | `/profile/sync` | Sync a GitHub profile (fetches from GitHub + saves to DB) |
| `GET` | `/profile/{username}` | Get cached profile |
| `GET` | `/analytics/{username}` | Get stats (stars, forks, followers…) |
| `GET` | `/analytics/{username}/languages` | Language distribution |
| `GET` | `/contributions/{username}` | Contribution heatmap data |
| `GET` | `/contributions/{username}/streaks` | Current + longest streaks |
| `GET` | `/repositories/{username}` | Paginated repo list |
| `PATCH` | `/repositories/{username}/{repo}/featured` | Mark a repo as featured |
| `POST` | `/compatibility/analyze` | ⚡ **Vibe Check** — JD vs repo languages |
| `GET` | `/career/recommendations/{id}` | Career tips from Vibe Check result |
| `GET` | `/portfolio/{username}` | Full public portfolio view |
| `POST` | `/deepwiki/{owner}/{repo}/ask` | Ask DeepWiki a question |
| `POST` | `/interview/generate` | Generate interview questions for a repo |
| `GET` | `/settings/{username}` | Get user settings (theme) |

> 📖 For full request/response schemas, open **http://localhost:8000/docs** while the server is running.

---

## ⚡ The Vibe Check — How It Works

This is the **flagship feature** of the project.

**Problem:** A recruiter posts a job description. How do you know if a developer's GitHub portfolio matches that role?

**Solution:**

```
Job Description (text)
        ↓
  Extract programming languages mentioned
  e.g. "Python, TypeScript, Go, React, Docker"
        ↓
  Filter to recognized programming languages only
  → Python ✓  TypeScript ✓  Go ✓
  → React ✗ (framework, not a language)
  → Docker ✗ (tool, not a language)
        ↓
  Compare against developer's cached repo languages
  Developer's repos: Python, JavaScript, Shell, C
        ↓
  Result:
    ✅ Python     — Found in portfolio
    ❌ TypeScript — Not found (gap!)
    ❌ Go         — Not found (gap!)

  Match score: 1/3 = 33%

  💡 Career tip: "Add a TypeScript project to improve your portfolio alignment."
```

The score formula is:
```
match % = (matched recognized languages / total recognized required languages) × 100
```

Data is **read from your cached repositories in SQLite** — no extra GitHub API call needed.

---

## 🧪 Running Tests

The test suite covers the Vibe Check algorithm, analytics calculations, and API endpoints — all with mocked external services (no real GitHub calls):

```bash
cd backend
pytest -v
```

Expected output:
```
tests/test_compatibility.py::TestExtractLanguages::test_recognizes_common_languages PASSED
tests/test_compatibility.py::TestCalculateMatch::test_all_languages_matched      PASSED
tests/test_analytics.py::TestStreaks::test_longest_streak_calculation             PASSED
tests/test_github.py::TestProfileSync::test_sync_valid_user                       PASSED
...
```

---

## 🗄️ Database

The app uses **SQLite** — a single file database that requires zero installation or configuration. It's created automatically when you start the backend.

**Location:** `backend/portfolio.db` (created on first run)

**6 Tables:**

| Table | Stores |
|-------|--------|
| `users` | Cached GitHub profiles |
| `repositories` | Cached public repos per user |
| `contributions` | Daily contribution counts (heatmap data) |
| `user_settings` | Theme preference |
| `featured_repositories` | User's hand-picked showcase repos |
| `compatibility_analyses` | Saved Vibe Check results |

**Cache TTLs** (how long before data is re-fetched from GitHub):
- Profile + Repos → **1 hour**
- Contributions → **6 hours**

---

## 🌐 Pages & Navigation

| Page | URL | What You See |
|------|-----|-------------|
| **Home** | `/` | Search box, feature overview |
| **Dashboard** | `/dashboard/:username` | Full analytics — stats, heatmap, repos |
| **Portfolio** | `/portfolio/:username` | Public shareable portfolio view |
| **Vibe Check** | `/vibe-check` | JD paste → match score + recommendations |
| **DeepWiki AI** | `/deepwiki` | Ask questions about any GitHub repo |

---

## 🐛 Common Issues & Fixes

**"Profile sync failed" / 404 error**
- The GitHub username doesn't exist or is typed incorrectly.
- Try `torvalds` or `gvanrossum` to test.

**"Contribution heatmap not available"**
- You need a GitHub token for the GraphQL API.
- Add `GITHUB_TOKEN=your_token_here` to `backend/.env` and restart the server.

**PowerShell activation error**
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

**Port already in use**
```bash
# Backend on a different port
uvicorn app.main:app --reload --port 8001

# Frontend on a different port
npm run dev -- --port 5174
```

**DeepWiki says "not indexed"**
- DeepWiki only indexes public, well-known repositories.
- Try `facebook/react` or `microsoft/vscode` as examples.

---

## 📂 Documentation

The `docs/` folder contains the original project specification:

| File | Contents |
|------|----------|
| [`REQUIREMENTS.md`](docs/REQUIREMENTS.md) | Full product requirements and acceptance criteria |
| [`USER_STORIES.md`](docs/USER_STORIES.md) | User stories with testable acceptance criteria |
| [`API_DOCUMENTATION.md`](docs/API_DOCUMENTATION.md) | Detailed API contracts |
| [`DATABASE_SCHEMA.md`](docs/DATABASE_SCHEMA.md) | Full database schema with indexes and TTL policies |

The `UML diagrams/` folder contains 6 architecture and flow diagrams:
- System architecture
- Use case diagram
- Sequence diagrams (GitHub sync, DeepWiki interaction)
- Class diagram
- Activity diagram (Vibe Check flow)

---

## 👨‍💻 Author

Built by **Umang Limbasiya** as part of the **Quantiphi Vibe Coding Assessment**.

GitHub: [@URL78](https://github.com/URL78)

---

> *"Your GitHub is your portfolio. This app just makes it look like one."*
