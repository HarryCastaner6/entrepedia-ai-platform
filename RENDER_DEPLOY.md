# Quick Render Deployment Guide

## Option 1: Blueprint (Recommended - Fastest)

I have created a `render.yaml` file that automates your entire deployment.

**Steps:**
1. Push your code to GitHub (if not already done):
   ```bash
   git add .
   git commit -m "Configure for production deployment"
   git push origin main
   ```

2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click **"New +"** → **"Blueprint"**
4. Connect your GitHub repository
5. Select the repository containing this code
6. Click **"Apply"**

That's it! Render will automatically:
- Install all dependencies
- Set up environment variables (including your database password)
- Start the backend server
- Give you a live URL

## Option 2: Manual Setup

If you prefer manual setup, follow the detailed instructions in `PRODUCTION_SETUP.md`.

## After Deployment

Once your backend is live on Render:
1. Copy the backend URL (e.g., `https://entrepedia-backend.onrender.com`)
2. Go to Vercel and deploy your frontend
3. Set `VITE_API_URL` to your Render backend URL

## Testing

After deployment, test by visiting:
- `YOUR_RENDER_URL/health` - Should show "healthy"
- `YOUR_RENDER_URL/docs` - Interactive API documentation

## Notes

- **First Load**: The free tier "spins down" after 15 minutes of inactivity. The first request after that may take 30-60 seconds.
- **Database**: Your Supabase database is already configured and will persist all data.
- **AI Memory**: The vector database (pgvector) is stored in Supabase, so course knowledge persists across restarts.
