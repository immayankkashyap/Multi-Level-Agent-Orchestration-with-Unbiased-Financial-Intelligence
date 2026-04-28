# FinanceAI — Unbiased Financial Intelligence Platform
### Multi-Level Agent Orchestration · Google Solution Challenge 2026

> An adversarial AI debate platform for financial decisions. Every recommendation passes through an Advocate → Devil's Advocate → Judge pipeline before reaching the user, with a bias report attached to every output.

---

## Prerequisites

Make sure these are installed on your machine before anything else.

| Tool | Version | Install |
|------|---------|---------|
| Python | 3.11+ | [python.org](https://python.org) |
| Node.js | 18+ | [nodejs.org](https://nodejs.org) |
| Docker | Latest | [docker.com](https://docker.com) |
| Git | Latest | [git-scm.com](https://git-scm.com) |

---

## Repository Structure

```
unbiased-finance/
├── backend/          # FastAPI + LangGraph + all agents
└── frontend/         # Next.js 14 App Router
```

---

## 1. Clone the Repository

```bash
git clone https://github.com/your-org/Multi-Level-Agent-Orchestration-with-Unbiased-Financial-Intelligence
mv Multi-Level-Agent-Orchestration-with-Unbiased-Financial-Intelligence unbiased_finance
cd unbiased_finance
```

---

## 2. Backend Setup

### 2.1 Create & Activate Virtual Environment

```bash
cd backend
python -m venv venv
```

```bash
# macOS / Linux
source venv/bin/activate

# Windows (PowerShell)
venv\Scripts\Activate.ps1

# Windows (CMD)
venv\Scripts\activate.bat
```

### 2.2 Install Python Dependencies

```bash
pip install fastapi uvicorn[standard] pydantic python-dotenv
pip install langchain langgraph langchain-google-genai
pip install qdrant-client sentence-transformers
pip install asyncpg sqlalchemy[asyncio] alembic
pip install yfinance httpx tenacity
pip install scikit-learn pandas numpy
pip install pytest pytest-asyncio
```

Or if a `requirements.txt` exists:

```bash
pip install -r requirements.txt
```

### 2.3 Start Infrastructure (Docker)

Open a new terminal and run both containers:

```bash
# Qdrant vector database — runs on port 6333
docker run -d --name qdrant-dev \
  -p 6333:6333 \
  qdrant/qdrant

# PostgreSQL — runs on port 5432
docker run -d --name pg-dev \
  -e POSTGRES_PASSWORD=dev \
  -e POSTGRES_DB=finance_db \
  -p 5432:5432 \
  postgres:15
```

Verify both are running:

```bash
docker ps
```

You should see `qdrant-dev` and `pg-dev` listed as `Up`.

### 2.4 Configure Environment Variables

```bash
cp .env.example .env
```

Open `.env` and fill in all values:

```env
# ── LLM ────────────────────────────────────────────────────────
GEMINI_API_KEY=your_google_ai_studio_key_here

# ── Vector Store ────────────────────────────────────────────────
QDRANT_URL=http://localhost:6333

# ── Database ────────────────────────────────────────────────────
DATABASE_URL=postgresql+asyncpg://postgres:dev@localhost/finance_db

# ── Firebase ────────────────────────────────────────────────────
FIREBASE_PROJECT_ID=your_firebase_project_id
FIREBASE_PRIVATE_KEY=your_firebase_private_key
FIREBASE_CLIENT_EMAIL=your_firebase_client_email

# ── Razorpay ────────────────────────────────────────────────────
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret

# ── App ─────────────────────────────────────────────────────────
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000
```

**Where to get these keys:**
- `GEMINI_API_KEY` → [aistudio.google.com](https://aistudio.google.com) → Get API Key
- Firebase keys → [console.firebase.google.com](https://console.firebase.google.com) → Project Settings → Service Accounts → Generate new private key
- Razorpay keys → [dashboard.razorpay.com](https://dashboard.razorpay.com) → Settings → API Keys

### 2.5 Initialize the Database

```bash
# Run the migration SQL to create all tables
psql postgresql://postgres:dev@localhost/finance_db \
  -f database/migrations/001_init.sql
```

If `psql` is not installed locally, run it via Docker:

```bash
docker exec -i pg-dev psql -U postgres finance_db \
  < database/migrations/001_init.sql
```

### 2.6 Ingest Sample Documents into Qdrant

```bash
# Creates the 'financial_docs' and 'regulations' collections
# and ingests the sample PDFs
python scripts/ingest_documents.py
```

> **Note:** Place your RBI/SEBI/IRDAI PDFs in `backend/data/regulations/` and mutual fund prospectuses in `backend/data/financial_docs/` before running this.

### 2.7 Start the Backend Server

```bash
uvicorn api.main:app --reload --port 8000
```

The API is now live at `http://localhost:8000`.  
Interactive docs (Swagger UI): `http://localhost:8000/docs`

---

## 3. Frontend Setup

Open a **new terminal** tab/window.

### 3.1 Navigate to Frontend & Install Dependencies

```bash
cd frontend
npm install
```

### 3.2 Install shadcn/ui Components

```bash
npx shadcn@latest init
# When prompted:
#   TypeScript: yes
#   Style: Default
#   Base color: Slate
#   CSS variables: yes

npx shadcn@latest add button card badge separator scroll-area
npx shadcn@latest add collapsible tooltip progress
```

### 3.3 Configure Environment Variables

```bash
cp .env.local.example .env.local
```

```env
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Firebase (public config — safe to expose)
NEXT_PUBLIC_FIREBASE_API_KEY=your_firebase_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_firebase_project_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_firebase_app_id
```

Firebase public config → Firebase Console → Project Settings → Your apps → Web app → SDK setup and configuration.

### 3.4 Start the Frontend Dev Server

```bash
npm run dev
```

The app is now live at `http://localhost:3000`.

---

## 4. Verify Everything Works

With both servers running, open `http://localhost:3000` and:

1. Sign in with Google (Firebase Auth)
2. Type a test query: **"Should I invest in HDFC Bank given current interest rates?"**
3. You should see:
   - The thinking indicator appear with live agent steps
   - The dropdown expandable for full detail
   - The debate document panel slide in on the right when complete
   - A final decision with confidence score and bias report

**Backend health check:**
```bash
curl http://localhost:8000/health
# Expected: {"status": "ok"}
```

**Qdrant health check:**
```bash
curl http://localhost:6333/health
# Expected: {"title": "qdrant - vector search engine", "version": "..."}
```

---

## 5. Running Tests

```bash
# From the backend directory, with venv activated
cd backend
pytest tests/ -v

# Run just the evaluation suite
python evaluation/fairness_metrics.py
```

---

## 6. Common Issues & Fixes

**`ModuleNotFoundError` when running uvicorn**  
→ Make sure your virtual environment is activated (`source venv/bin/activate`)

**Qdrant connection refused**  
→ Check the Docker container is running: `docker ps`. If not, `docker start qdrant-dev`

**PostgreSQL auth error**  
→ Confirm `DATABASE_URL` in `.env` matches your Docker container password (`dev`)

**Gemini API 403 error**  
→ Check your `GEMINI_API_KEY` is valid at [aistudio.google.com](https://aistudio.google.com). Free tier has rate limits — add a 1s delay between calls during dev.

**`next: command not found`**  
→ Run `npm install` inside the `frontend/` directory first

**Firebase auth not working**  
→ In Firebase Console → Authentication → Sign-in method → enable **Google**. Also add `http://localhost:3000` to Authorized domains.

---

## 7. Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, Tailwind CSS, shadcn/ui, Recharts, React Flow |
| State | Zustand |
| Backend | FastAPI, Python 3.11 |
| Agents | LangGraph (orchestration), LangChain (tools) |
| LLM | Gemini 1.5 Flash (debate), Gemini 1.5 Pro (judge) |
| Vector DB | Qdrant (hybrid dense + BM25) |
| Relational DB | PostgreSQL |
| Auth | Firebase Auth |
| Payments | Razorpay |
| Hosting | Vercel (frontend), Cloud Run (backend) |

---