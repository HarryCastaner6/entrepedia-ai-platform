# Production Setup Guide for Entrepedia AI Platform

This guide explains how to deploy your platform for free using **Supabase** (Database & Storage), **Render** (Backend), and **Vercel** (Frontend).

## 1. Database & Storage Setup (Supabase)

Supabase provides a free PostgreSQL database and file storage.

1.  **Create Account**: Go to [Supabase](https://supabase.com/) and sign up.
2.  **New Project**: Create a new project. Give it a name and secure password.
3.  **Get Database URL**:
    *   Go to **Project Settings** -> **Database**.
    *   Find **Connection String** -> **URI**.
    *   Copy the string. It looks like: `postgresql://postgres:[PASSWORD]@db.apmwojsfejoiugiohipm.supabase.co:5432/postgres`
    *   **IMPORTANT**: Replace `[PASSWORD]` with the password you created in Step 2.
    *   **Note**: I have already configured your Project URL and API Key in the code. You just need this Database URL for the backend to work.
4.  **Setup Storage**:
    *   Go to **Storage** in the left sidebar.
    *   Create a new bucket named `courses`.
    *   Make it **Public** (so users can access files).
    *   Go to **Project Settings** -> **API**.
    *   Copy the **Project URL** and **service_role** key (keep this secret!).

## 2. Backend Deployment (Render)

Render will host your Python FastAPI backend.

1.  **Create Account**: Go to [Render](https://render.com/) and sign up.
2.  **New Web Service**: Click "New +" -> "Web Service".
3.  **Connect Repo**: Connect your GitHub repository.
4.  **Configuration**:
    *   **Name**: `entrepedia-backend`
    *   **Runtime**: Python 3
    *   **Build Command**: `pip install -r requirements.txt`
    *   **Start Command**: `gunicorn backend.api.main:app -w 4 -k uvicorn.workers.UvicornWorker`
    *   **Instance Type**: Free
5.  **Environment Variables**:
    Add the following variables in the "Environment" tab:
    *   `PYTHON_VERSION`: `3.11.0`
    *   `DATABASE_URL`: (Paste your Supabase connection string from Step 1)
    *   `STORAGE_TYPE`: `supabase`
    *   `SUPABASE_URL`: (Your Supabase Project URL)
    *   `SUPABASE_KEY`: (Your Supabase service_role key)
    *   `OPENAI_API_KEY`: (Your OpenAI Key)
    *   `GEMINI_API_KEY`: (Your Gemini Key)
    *   `SECRET_KEY`: (Generate a random string)
6.  **Deploy**: Click "Create Web Service". Wait for it to go live. Copy the URL (e.g., `https://entrepedia-backend.onrender.com`).

## 3. Frontend Deployment (Vercel)

Vercel will host your React frontend.

1.  **Create Account**: Go to [Vercel](https://vercel.com/) and sign up.
2.  **Import Project**: Click "Add New..." -> "Project" and select your repo.
3.  **Configuration**:
    *   **Framework Preset**: Vite (should detect automatically).
    *   **Root Directory**: `frontend` (Important! Select the frontend folder).
4.  **Environment Variables**:
    *   `VITE_API_URL`: (Paste your Render Backend URL from Step 2)
5.  **Deploy**: Click "Deploy".

## 4. Verify Setup

1.  Visit your Vercel URL.
2.  Try uploading a document. It should be saved to your Supabase `courses` bucket and the metadata stored in the Supabase Database.
3.  The AI should work using the API keys you provided.

## Notes on "Free" Tier Limits

*   **Render Free Tier**: Spins down after 15 minutes of inactivity. The first request might take 30-60 seconds to load. This is normal for free hosting.
*   **Supabase Free Tier**: Generous limits (500MB database, 1GB storage). Perfect for starting out.
*   **Vector Search**: The current setup uses local FAISS for vector search. On Render's free tier, **this index will be reset** when the server restarts.
    *   **Solution**: For a truly persistent AI memory on the free tier, we recommend implementing Supabase `pgvector`. This requires a bit more code change. For now, the platform works, but "memory" of uploaded docs is session-based.
