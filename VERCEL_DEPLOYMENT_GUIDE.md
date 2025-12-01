# Vercel Deployment Guide - Clean Setup

## Step 1: Delete Current Deployment

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Find your project "entrepedia-ai-platform"
3. Click on the project
4. Go to Settings → General
5. Scroll down to "Delete Project"
6. Type the project name to confirm deletion
7. Click "Delete"

## Step 2: Prepare Clean Files

Replace these files with the clean versions:

### Replace vercel.json
```bash
cp vercel-clean.json vercel.json
```

### Replace api/requirements.txt
```bash
cp api/requirements-clean.txt api/requirements.txt
```

## Step 3: Commit Clean Changes

```bash
git add .
git commit -m "Clean deployment setup for Vercel recreation"
git push origin main
```

## Step 4: Create New Vercel Deployment

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "New Project"
3. Import your GitHub repository "entrepedia-ai-platform"
4. **Configure Build Settings:**
   - Framework Preset: Vite
   - Root Directory: `./` (leave default)
   - Build Command: `npm run build`
   - Output Directory: `frontend/dist`

## Step 5: Set Environment Variables

In the Vercel project settings, add these environment variables:

| Key | Value |
|-----|-------|
| `APP_ENV` | `production` |
| `DEBUG` | `false` |
| `SECRET_KEY` | `production-secret-key-32-chars-minimum-for-security-2024` |
| `JWT_SECRET_KEY` | `production-jwt-secret-32-chars-minimum-for-security-2024` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` |

## Step 6: Deploy

1. Click "Deploy"
2. Wait for deployment to complete
3. Test the endpoints:

### Test Health Check
```
GET https://your-project.vercel.app/api/health
```

### Test Authentication
```
POST https://your-project.vercel.app/api/auth/login
Content-Type: application/x-www-form-urlencoded

username=admin@entrepedia.ai&password=admin123
```

## Working Credentials

After deployment, you can login with:
- **Email:** `admin@entrepedia.ai`
- **Password:** `admin123`

## API Endpoints Available

- `GET /api/health` - Health check
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `GET /api/auth/` - Auth service info

## Troubleshooting

If deployment still fails:

1. **Check Vercel Function Logs** in the dashboard
2. **Verify Node.js dependencies** are installing correctly
3. **Check Python function logs** for any import errors

## Frontend Configuration

Update your frontend API base URL to point to the new Vercel domain.

---

This clean setup removes all problematic backend dependencies and provides a working authentication system for your application.