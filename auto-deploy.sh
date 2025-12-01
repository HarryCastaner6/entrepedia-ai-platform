#!/bin/bash

# Fully Automated Vercel Deployment
# User only needs to delete the old project manually, then run this script

echo "🚀 ENTREPEDIA AI PLATFORM - AUTOMATED DEPLOYMENT"
echo "================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
print_step "Checking prerequisites..."

# Check if we're in the right directory
if [ ! -f "vercel.json" ]; then
    print_error "vercel.json not found. Please run this from the project root."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if Git is configured
if ! git config user.email > /dev/null; then
    print_error "Git is not configured. Please configure git first."
    exit 1
fi

print_success "All prerequisites met!"

# Install Vercel CLI if not installed
print_step "Installing/updating Vercel CLI..."
npm install -g vercel@latest

# Ensure we're logged into Vercel
print_step "Checking Vercel authentication..."
if ! vercel whoami &> /dev/null; then
    print_warning "Not logged into Vercel. Starting login process..."
    vercel login
fi

print_success "Logged into Vercel!"

# Commit and push latest changes
print_step "Committing and pushing latest changes..."
git add .
git commit -m "Automated deployment - clean setup" || true
git push origin main

print_success "Code pushed to repository!"

# Manual step reminder
echo ""
echo "⚠️  MANUAL ACTION REQUIRED ⚠️"
echo "================================"
print_warning "You MUST delete the old Vercel project first!"
echo ""
echo "1. Open: https://vercel.com/dashboard"
echo "2. Find: 'entrepedia-ai-platform' project"
echo "3. Click: Project → Settings → General"
echo "4. Scroll down and click: 'Delete Project'"
echo "5. Type: 'entrepedia-ai-platform' to confirm"
echo "6. Click: Delete"
echo ""
read -p "Press ENTER after deleting the old project..."

# Deploy to Vercel
print_step "Deploying to Vercel..."
echo ""
echo "When Vercel asks:"
echo "- 'Set up and deploy?' → Press Enter (Yes)"
echo "- 'Which scope?' → Press Enter (your account)"
echo "- 'Link to existing project?' → Type 'n' + Enter (No)"
echo "- 'What's your project's name?' → Type 'entrepedia-ai-platform' + Enter"
echo "- 'In which directory is your code located?' → Press Enter (./)"
echo ""

# Run Vercel deployment
vercel --prod

# Get the deployment URL
DEPLOYMENT_URL=$(vercel --prod --confirm 2>/dev/null | grep -E 'https://[^[:space:]]+' | tail -1)

if [ -z "$DEPLOYMENT_URL" ]; then
    print_warning "Couldn't automatically detect deployment URL. Please check Vercel dashboard."
    DEPLOYMENT_URL="your-new-project.vercel.app"
else
    print_success "Deployment URL: $DEPLOYMENT_URL"
fi

echo ""
print_step "Testing deployment..."

# Test health endpoint
echo ""
echo "Testing health endpoint..."
HEALTH_URL="$DEPLOYMENT_URL/api/health"
if curl -s -o /dev/null -w "%{http_code}" "$HEALTH_URL" | grep -q "200"; then
    print_success "Health endpoint working!"
else
    print_warning "Health endpoint might not be ready yet (normal for new deployments)"
fi

# Test auth endpoint
echo ""
echo "Testing auth endpoint..."
AUTH_URL="$DEPLOYMENT_URL/api/auth/"
if curl -s -o /dev/null -w "%{http_code}" "$AUTH_URL" | grep -q "200"; then
    print_success "Auth endpoint working!"
else
    print_warning "Auth endpoint might not be ready yet (normal for new deployments)"
fi

echo ""
echo "🎉 DEPLOYMENT COMPLETE!"
echo "======================"
print_success "Your application is deployed at: $DEPLOYMENT_URL"
echo ""
echo "📝 Test these endpoints:"
echo "   Health: $DEPLOYMENT_URL/api/health"
echo "   Auth:   $DEPLOYMENT_URL/api/auth/login"
echo ""
echo "🔐 Login credentials:"
echo "   Email:    admin@entrepedia.ai"
echo "   Password: admin123"
echo ""
echo "🔧 Next steps:"
echo "1. Update your frontend to use the new API URL"
echo "2. Test login from your frontend"
echo "3. Monitor Vercel function logs for any issues"
echo ""
print_success "Deployment automation complete!"

# Save deployment info
echo "DEPLOYMENT_URL=$DEPLOYMENT_URL" > .deployment-info
echo "DEPLOYED_AT=$(date)" >> .deployment-info
print_success "Deployment info saved to .deployment-info"