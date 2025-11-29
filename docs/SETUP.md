# Entrepedia AI Platform - Setup Guide

This comprehensive guide will walk you through setting up the Entrepedia AI Platform from scratch.

## 📋 Prerequisites

### System Requirements

- **Operating System**: Linux, macOS, or Windows 10/11
- **RAM**: Minimum 8GB, Recommended 16GB+
- **Storage**: 20GB+ free space
- **CPU**: Multi-core processor recommended
- **GPU**: Optional, improves embedding performance

### Software Dependencies

#### Required
- **Python 3.11+**: [Download Python](https://python.org/downloads/)
- **Node.js 18+**: [Download Node.js](https://nodejs.org/)
- **Git**: [Download Git](https://git-scm.com/)

#### Recommended (for production)
- **Docker & Docker Compose**: [Install Docker](https://docs.docker.com/get-docker/)
- **PostgreSQL 15+**: [Install PostgreSQL](https://postgresql.org/download/)
- **Redis 7+**: [Install Redis](https://redis.io/download/)

### API Keys Required

1. **Anthropic API Key**
   - Sign up at [console.anthropic.com](https://console.anthropic.com)
   - Create API key
   - Billing setup required for usage

2. **OpenAI API Key**
   - Sign up at [platform.openai.com](https://platform.openai.com)
   - Create API key
   - Add payment method for usage

3. **Entrepedia Credentials**
   - Valid Entrepedia account
   - Username and password

### Optional API Keys

4. **Pinecone** (for cloud vector database)
   - Sign up at [pinecone.io](https://pinecone.io)
   - Create project and get API key

5. **Google Calendar** (for integration)
   - Google Cloud Console setup
   - Enable Calendar API
   - Download credentials JSON

6. **Notion** (for integration)
   - Create Notion integration
   - Get API token

## 🚀 Installation Options

### Option 1: Docker Setup (Recommended)

Docker provides the easiest setup with all dependencies included.

#### 1. Clone Repository
```bash
git clone <repository-url>
cd entrepedia-ai-platform
```

#### 2. Environment Configuration
```bash
cp .env.example .env
```

Edit `.env` with your API keys:
```env
# Required API Keys
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENAI_API_KEY=sk-your-openai-key-here

# Entrepedia Credentials
ENTREPEDIA_USERNAME=your_username
ENTREPEDIA_PASSWORD=your_password

# Security (generate strong random strings)
SECRET_KEY=your-32-character-secret-key-here
JWT_SECRET_KEY=your-32-character-jwt-secret

# Database (Docker will handle these)
DATABASE_URL=postgresql://entrepedia_user:entrepedia_password@postgres:5432/entrepedia_db
REDIS_URL=redis://redis:6379/0
```

#### 3. Start Services
```bash
cd docker
docker-compose up -d
```

#### 4. Verify Installation
```bash
# Check all services are running
docker-compose ps

# Check application health
curl http://localhost:8000/health

# Access frontend
open http://localhost:3000
```

### Option 2: Manual Development Setup

For development or when you want more control over the setup.

#### Backend Setup

1. **Clone and Navigate**
```bash
git clone <repository-url>
cd entrepedia-ai-platform
```

2. **Python Environment**
```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

3. **Download AI Models**
```bash
# Spacy model for NLP
python -m spacy download en_core_web_sm

# Whisper model (downloaded automatically on first use)
```

4. **Database Setup**
```bash
# Install PostgreSQL locally
# Create database
createdb entrepedia_db

# Install Redis locally or use Docker
docker run -d -p 6379:6379 redis:7-alpine
```

5. **Environment Configuration**
```bash
cp .env.example .env
# Edit .env with your local database URLs and API keys
```

6. **Start Backend**
```bash
export PYTHONPATH=$PWD
uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

1. **Navigate to Frontend**
```bash
cd frontend
```

2. **Install Dependencies**
```bash
npm install
```

3. **Start Development Server**
```bash
npm run dev
```

Frontend will be available at http://localhost:3000

## 🔧 Configuration

### Environment Variables Reference

#### Core Application
```env
APP_NAME=Entrepedia AI Platform
APP_ENV=development
DEBUG=True
SECRET_KEY=your-secret-key-32-chars-minimum
```

#### Database Configuration
```env
DATABASE_URL=postgresql://user:password@localhost:5432/entrepedia_db
REDIS_URL=redis://localhost:6379/0
```

#### AI Service Configuration
```env
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENAI_API_KEY=sk-your-openai-key-here
```

#### Vector Database Options
```env
# Local FAISS (default)
VECTOR_DB_TYPE=faiss

# Cloud Pinecone
VECTOR_DB_TYPE=pinecone
PINECONE_API_KEY=your-pinecone-key
PINECONE_ENVIRONMENT=your-pinecone-env

# Self-hosted Weaviate
VECTOR_DB_TYPE=weaviate
WEAVIATE_URL=http://localhost:8080
```

#### Storage Configuration
```env
# Local storage (default)
STORAGE_TYPE=local
OUTPUT_DIR=./data/courses

# AWS S3 storage
STORAGE_TYPE=s3
S3_BUCKET=your-bucket-name
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
```

#### External Integrations
```env
GOOGLE_CALENDAR_CREDENTIALS=./credentials/google_calendar.json
NOTION_API_KEY=secret_your-notion-key
TRELLO_API_KEY=your-trello-key
TRELLO_TOKEN=your-trello-token
```

#### Security Settings
```env
JWT_SECRET_KEY=your-jwt-secret-32-chars-minimum
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENCRYPTION_KEY=your-encryption-key-32-chars-for-fernet
```

#### Scraper Settings
```env
ENTREPEDIA_BASE_URL=https://app.entrepedia.co
ENTREPEDIA_USERNAME=your_username
ENTREPEDIA_PASSWORD=your_password
SCRAPER_SCHEDULE_HOURS=24
MAX_CONCURRENT_DOWNLOADS=5
REQUEST_TIMEOUT=30
```

### Generating Secure Keys

#### Python Method
```python
import secrets

# Generate SECRET_KEY
print(secrets.token_urlsafe(32))

# Generate JWT_SECRET_KEY
print(secrets.token_urlsafe(32))

# Generate ENCRYPTION_KEY (for Fernet)
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

#### Command Line Method
```bash
# Linux/macOS
openssl rand -base64 32

# Generate multiple keys
for i in {1..3}; do openssl rand -base64 32; done
```

## 🔍 System Verification

### Health Checks

After setup, verify everything is working:

#### 1. Backend Health
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "app": "Entrepedia AI Platform",
  "environment": "development",
  "version": "1.0.0"
}
```

#### 2. Database Connection
```bash
curl http://localhost:8000/documents/stats
```

#### 3. AI Services
```bash
curl -X POST http://localhost:8000/query/agents \
  -H "Content-Type: application/json"
```

#### 4. Frontend Access
Visit http://localhost:3000 and verify:
- [ ] Page loads without errors
- [ ] Navigation works
- [ ] Can access different sections

### Test Document Upload

1. Go to "Upload Files" section
2. Upload a sample PDF
3. Verify processing completes
4. Check document appears in stats

### Test AI Chat

1. Go to "AI Chat" section
2. Send a test message: "Hello, can you help me learn?"
3. Verify response from AI agent
4. Check conversation history

## 🛠️ Troubleshooting

### Common Setup Issues

#### Docker Issues

**Problem**: Docker containers fail to start
```bash
# Check Docker is running
docker --version
docker-compose --version

# View container logs
docker-compose logs backend
docker-compose logs frontend

# Restart specific service
docker-compose restart backend
```

**Problem**: Port conflicts
```bash
# Check what's using ports
lsof -i :8000
lsof -i :3000

# Stop conflicting services or change ports in docker-compose.yml
```

#### Python Dependencies

**Problem**: Package installation fails
```bash
# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install with verbose output
pip install -v package-name

# For macOS M1/M2 issues
pip install --no-use-pep517 package-name
```

**Problem**: Tesseract not found
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-eng

# macOS
brew install tesseract

# Windows - Download installer from GitHub
```

#### Database Issues

**Problem**: PostgreSQL connection fails
```bash
# Check PostgreSQL is running
systemctl status postgresql

# Test connection
psql -h localhost -U postgres -d entrepedia_db

# Reset password if needed
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'new_password';"
```

**Problem**: Redis connection fails
```bash
# Check Redis is running
redis-cli ping

# Start Redis
systemctl start redis

# Or use Docker
docker run -d -p 6379:6379 redis:7-alpine
```

#### API Key Issues

**Problem**: Invalid API keys
```bash
# Test Anthropic API
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"claude-3-haiku-20240307","max_tokens":10,"messages":[{"role":"user","content":"Hi"}]}'

# Test OpenAI API
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_KEY"
```

#### Frontend Issues

**Problem**: Node.js build fails
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Use specific Node version
nvm install 18
nvm use 18
```

**Problem**: Frontend can't connect to backend
- Check backend is running on port 8000
- Verify CORS settings in backend
- Check proxy configuration in vite.config.ts

### Performance Optimization

#### For Large Document Collections

1. **Increase Resource Limits**
```yaml
# In docker-compose.yml
backend:
  deploy:
    resources:
      limits:
        memory: 4G
        cpus: '2.0'
```

2. **Optimize Embeddings**
```env
# Use smaller embedding model
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Reduce chunk size
CHUNK_SIZE=256
```

3. **Database Tuning**
```sql
-- Increase shared_buffers in postgresql.conf
shared_buffers = 256MB
work_mem = 64MB
```

#### For High Concurrent Users

1. **Scale Backend**
```yaml
backend:
  scale: 3  # Run 3 backend instances
```

2. **Add Load Balancer**
```nginx
upstream backend {
    server backend_1:8000;
    server backend_2:8000;
    server backend_3:8000;
}
```

## 🔐 Security Hardening

### Production Security Checklist

- [ ] Use strong, unique secret keys
- [ ] Enable HTTPS with valid SSL certificates
- [ ] Configure firewall to restrict access
- [ ] Use environment variables for all secrets
- [ ] Enable database connection encryption
- [ ] Implement rate limiting
- [ ] Regular security updates
- [ ] Monitor logs for suspicious activity
- [ ] Backup encryption keys securely
- [ ] Use non-root users in containers

### SSL/HTTPS Setup

1. **Obtain SSL Certificate**
```bash
# Let's Encrypt (free)
certbot certonly --standalone -d yourdomain.com

# Or use commercial certificate
```

2. **Update Nginx Configuration**
```nginx
server {
    listen 443 ssl http2;
    ssl_certificate /etc/ssl/certs/yourdomain.com.pem;
    ssl_certificate_key /etc/ssl/private/yourdomain.com.key;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
}
```

### Database Security

```sql
-- Create dedicated user
CREATE USER entrepedia_user WITH ENCRYPTED PASSWORD 'strong_password';
GRANT CONNECT ON DATABASE entrepedia_db TO entrepedia_user;
GRANT USAGE ON SCHEMA public TO entrepedia_user;
GRANT CREATE ON SCHEMA public TO entrepedia_user;

-- Enable SSL
ssl = on
ssl_cert_file = 'server.crt'
ssl_key_file = 'server.key'
```

## 📞 Getting Help

### Documentation
- [API Reference](API_REFERENCE.md)
- [Architecture Overview](ARCHITECTURE.md)
- [User Guide](USER_GUIDE.md)

### Community Support
- GitHub Issues: Report bugs and feature requests
- Discussions: Ask questions and share ideas

### Debugging Information

When requesting help, please include:

1. **System Information**
```bash
# Operating system
uname -a

# Python version
python --version

# Node.js version
node --version

# Docker version (if using)
docker --version
```

2. **Error Logs**
```bash
# Backend logs
tail -n 50 logs/app.log

# Docker logs
docker-compose logs --tail=50 backend

# Frontend console errors
# Open browser dev tools and check console
```

3. **Configuration** (sanitized, no secrets)
```bash
# Environment variables (remove sensitive values)
env | grep -E "(APP_|DATABASE_|REDIS_)" | sed 's/=.*/=***/'
```

---

**Setup complete! 🎉 You're ready to start using the Entrepedia AI Platform.**