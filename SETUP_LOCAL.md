# FinIntel: Local Setup & Git Push Guide

Complete guide to download, set up locally in VS Code, and push to GitHub.

---

## Step 1: Download the Project

### Option A: Direct Download (Recommended for beginners)
1. Download `ai-financial-intelligence.zip` from the outputs folder
2. Unzip it to your desired location (e.g., `~/projects/`)
   ```bash
   unzip ai-financial-intelligence.zip
   cd ai-financial-intelligence
   ```

### Option B: Clone from GitHub (After you push)
```bash
git clone https://github.com/YOUR_USERNAME/ai-financial-intelligence.git
cd ai-financial-intelligence
```

---

## Step 2: Open in VS Code

```bash
code .
```

Or:
1. Open VS Code
2. File → Open Folder → Select `ai-financial-intelligence`

---

## Step 3: Backend Setup (Terminal 1)

### 3.1 Create Virtual Environment
```bash
cd backend
python3 -m venv .venv
```

**Activate:**
- **Mac/Linux:**
  ```bash
  source .venv/bin/activate
  ```
- **Windows:**
  ```bash
  .venv\Scripts\activate
  ```

### 3.2 Install Dependencies
```bash
pip install -r requirements.txt
```

### 3.3 Create `.env` File
```bash
cp ../.env.example ../.env
```

### 3.4 Edit `.env` (No Azure Keys Needed for Local)
Open `../.env` in VS Code and set:
```
APP_ENV=development
DATABASE_URL=sqlite:///./finai.db
REDIS_URL=memory://
VECTOR_STORE=faiss
OCR_PROVIDER=tesseract
SECRET_KEY=dev-secret-change-in-production
CORS_ORIGINS=http://localhost:5173
```

**If using Ollama for free local LLM:**
```
AZURE_OPENAI_ENDPOINT=http://localhost:11434
AZURE_OPENAI_API_KEY=ollama
AZURE_OPENAI_CHAT_DEPLOYMENT=mistral
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=mistral
```

### 3.5 Run Backend
```bash
uvicorn app.main:app --reload
```

✅ Should see:
```
Uvicorn running on http://127.0.0.1:8000
Press CTRL+C to quit
```

Open http://localhost:8000/docs to see interactive API documentation.

---

## Step 4: Frontend Setup (Terminal 2)

### 4.1 Install Dependencies
```bash
cd frontend
npm install
```

### 4.2 Create `.env` (Optional)
```bash
echo "VITE_API_BASE_URL=http://localhost:8000/api/v1" > .env.local
```

### 4.3 Run Dev Server
```bash
npm run dev
```

✅ Should see:
```
VITE v6.0.5 ready in 245 ms

➜  Local:   http://localhost:5173/
```

Open http://localhost:5173 in your browser.

---

## Step 5: Login & Test

1. **Login**
   - Email: `admin@example.com`
   - Password: `ChangeMe123!`

2. **Upload a test file**
   - Go to Upload tab
   - Download sample reports from `sample_data/` folder
   - Upload one with fiscal period `FY2025-26`
   - Wait for status to show `EMBEDDED` (10–30 seconds)

3. **Run Analysis**
   - Go to AI Insights
   - Click "Run analysis"
   - Wait 30–60 seconds for dashboard to populate

4. **Chat**
   - Go to Chat with Reports
   - Ask: "Why did profit grow faster than revenue?"

---

## Step 6: Initialize Git & Push to GitHub

### 6.1 Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `ai-financial-intelligence`
3. Description: "Enterprise AI financial analysis platform"
4. Choose **Public** (so others can see it)
5. **Don't** initialize with README (we already have one)
6. Click "Create repository"

### 6.2 Initialize Local Git

```bash
cd ai-financial-intelligence
git init
git config user.name "Your Name"
git config user.email "your.email@example.com"
git add .
git commit -m "Initial commit: FinIntel enterprise app"
```

### 6.3 Add Remote & Push

Replace `YOUR_USERNAME` with your actual GitHub username:

```bash
git remote add origin https://github.com/YOUR_USERNAME/ai-financial-intelligence.git
git branch -M main
git push -u origin main
```

✅ Your repo is now live at:
```
https://github.com/YOUR_USERNAME/ai-financial-intelligence
```

---

## Step 7: (Optional) Deploy to Azure

### 7.1 Install Azure CLI
```bash
# Mac
brew install azure-cli

# Windows (Chocolatey)
choco install azure-cli

# Or download: https://aka.ms/installazurecliwindows
```

### 7.2 Login & Follow Deployment Guide
```bash
az login
```

Then follow `docs/azure-deployment.md` step by step.

---

## Troubleshooting

### Backend won't start
```bash
# Check Python version (need 3.12+)
python3 --version

# Clear cache and reinstall
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Frontend shows API errors
1. Ensure backend is running on http://localhost:8000
2. Check CORS_ORIGINS in .env includes http://localhost:5173
3. Check browser console (F12) for actual error

### Database locked (SQLite)
```bash
# Kill any existing processes
pkill -f uvicorn
rm finai.db*
```

### Module not found errors
```bash
# Ensure you're in the virtual environment
which python  # Should show path with .venv
pip list | grep fastapi  # Should show installed packages
```

### Tesseract not found (OCR)
```bash
# Mac
brew install tesseract

# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# Windows (download installer from: https://github.com/UB-Mannheim/tesseract/wiki)
```

---

## Project Structure for Reference

```
ai-financial-intelligence/
├── backend/
│   ├── app/
│   │   ├── api/routes/          ← REST endpoints
│   │   ├── services/            ← Business logic
│   │   ├── agents/              ← LangGraph workflow
│   │   ├── rag/                 ← RAG pipeline
│   │   ├── embeddings/          ← Vector stores
│   │   ├── parser/              ← PDF/Excel parsing
│   │   ├── analytics/           ← KPI engine
│   │   ├── models/              ← SQLAlchemy ORM
│   │   ├── schemas/             ← Pydantic DTOs
│   │   ├── repositories/        ← Data access layer
│   │   ├── auth/                ← JWT/OAuth2
│   │   ├── middleware/          ← Logging, error handling
│   │   ├── database/            ← Session management
│   │   ├── config/              ← Settings
│   │   └── main.py              ← FastAPI app
│   ├── requirements.txt
│   ├── Dockerfile
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── pages/               ← All 10 dashboard pages
│   │   ├── components/          ← Reusable UI components
│   │   ├── layouts/             ← AppShell with nav
│   │   ├── services/            ← API client
│   │   ├── hooks/               ← React Query hooks
│   │   ├── contexts/            ← Auth & Theme
│   │   ├── types/               ← TypeScript interfaces
│   │   └── App.tsx              ← Router
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── Dockerfile
│   └── nginx.conf
├── docs/
│   ├── api.md                   ← API reference
│   └── azure-deployment.md      ← Cloud setup guide
├── sample_data/
│   ├── Sample_PnL_FY2024-25.xlsx
│   ├── Sample_PnL_FY2025-26.xlsx
│   ├── Sample_Balance_Sheet_FY2025-26.xlsx
│   └── Sample_Audit_Report_FY2025-26.pdf
├── .env.example
├── .github/workflows/ci.yml     ← GitHub Actions CI/CD
├── docker-compose.yml
├── README.md
└── SETUP_LOCAL.md               ← This file
```

---

## Git Workflow Tips

### Before you push, clean up (optional)
```bash
# Remove pycache and node_modules if accidentally added
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type d -name node_modules -exec rm -rf {} +
find . -name ".DS_Store" -delete
```

### Make a .gitignore (already included, but just in case)
```
backend/.venv/
backend/__pycache__/
backend/.pytest_cache/
backend/finai.db*
frontend/node_modules/
frontend/dist/
.env
.DS_Store
*.pyc
```

### Everyday workflow
```bash
# After making changes
git status
git add .
git commit -m "Describe your change"
git push origin main
```

---

## Next Steps

1. ✅ Download & extract project
2. ✅ Set up backend + frontend locally
3. ✅ Test with sample financial data
4. ✅ Push to GitHub
5. 🚀 (Optional) Deploy to Azure or Heroku

---

## Questions?

- **API Docs:** http://localhost:8000/docs (Swagger)
- **Tech Stack Doc:** See `FinIntel_Tech_Stack_Documentation.docx`
- **Code Structure:** See `backend/app/main.py` and `frontend/src/App.tsx` as entry points

Happy coding! 🚀
