#!/bin/bash

# Automated Vercel Deployment Script
# This script will help you redeploy your project cleanly

echo "🚀 Entrepedia AI Platform - Clean Deployment Script"
echo "=================================================="

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
fi

echo ""
echo "📋 MANUAL STEP REQUIRED:"
echo "1. Go to https://vercel.com/dashboard"
echo "2. Find your 'entrepedia-ai-platform' project"
echo "3. Click on it → Settings → General → Delete Project"
echo "4. Type the project name to confirm deletion"
echo "5. Press Enter here when done..."
read -p "Press Enter after deleting the project..."

echo ""
echo "🔄 Pushing latest clean configuration..."
git add .
git commit -m "Final clean deployment configuration" || echo "No changes to commit"
git push origin main

echo ""
echo "🌐 Starting new Vercel deployment..."
echo "When prompted:"
echo "- Link to existing project? → No"
echo "- Project name → entrepedia-ai-platform"
echo "- Directory → ./"
echo ""

# Deploy with Vercel
vercel --prod

echo ""
echo "✅ Deployment initiated!"
echo ""
echo "🔗 Your new deployment URL will be shown above."
echo "📝 Test these endpoints after deployment:"
echo "   GET  https://your-project.vercel.app/api/health"
echo "   POST https://your-project.vercel.app/api/auth/login"
echo ""
echo "🔐 Login credentials:"
echo "   Email: admin@entrepedia.ai"
echo "   Password: admin123"
echo ""
echo "🎉 Deployment complete!"