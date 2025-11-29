# Entrepedia AI Platform

A comprehensive AI-enhanced education platform that automatically scrapes and ingests course materials, processes documents with advanced AI, and enables interactive learning through intelligent agents.

## 🚀 Features

### Document Processing
- **Multi-format Support**: PDF, DOCX, PPTX, images, audio, and video files
- **Advanced OCR**: Extract text from images and scanned documents
- **Audio Transcription**: Convert speech to text using Whisper
- **Intelligent Chunking**: Semantic document segmentation

### AI-Powered Learning
- **Coach Agent**: Personalized learning guidance and motivation
- **Strategist Agent**: Comprehensive learning strategies and game plans
- **Knowledge Search**: Semantic search across all processed content
- **Interactive Chat**: Natural language interface with AI agents

### Automated Scraping
- **Entrepedia Integration**: Automated course material discovery and download
- **Robust Authentication**: Secure login and session management
- **Retry Logic**: Fault-tolerant downloading with exponential backoff
- **Metadata Extraction**: Rich document and course information

### Vector Database & Embeddings
- **Multiple Providers**: Support for FAISS, Pinecone, and Weaviate
- **Semantic Search**: Find relevant content based on meaning, not just keywords
- **Knowledge Graph**: Discover connections between concepts
- **Real-time Updates**: Automatic embedding generation for new content

### External Integrations
- **Google Calendar**: Schedule study sessions and milestones
- **Notion**: Create organized study notes and plans
- **Trello**: Task management and progress tracking
- **Extensible Architecture**: Easy to add new integrations

## 🏗️ Architecture

```mermaid
graph TB
    A[Entrepedia Scraper] --> B[Document Processing Pipeline]
    B --> C[Embeddings Engine]
    C --> D[Vector Database]
    D --> E[AI Agent System]
    E --> F[Web Interface]
    F --> G[Integration Hub]
    G --> H[External Tools]

    subgraph "Processing Pipeline"
        I[PDF Processor]
        J[DOCX Processor]
        K[Image OCR]
        L[Audio Transcription]
    end

    B --> I
    B --> J
    B --> K
    B --> L
```

## 📋 Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **Docker & Docker Compose** (recommended)
- **PostgreSQL 15+**
- **Redis 7+**

### Required API Keys
- **Anthropic API Key** (for Claude)
- **OpenAI API Key** (for GPT and Whisper)
- **Entrepedia Credentials** (for course scraping)

### Optional API Keys
- **Pinecone API Key** (if using Pinecone vector database)
- **Google Calendar API** (for calendar integration)
- **Notion API Key** (for Notion integration)
- **Trello API Credentials** (for Trello integration)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd entrepedia-ai-platform
cp .env.example .env
```

### 2. Configure Environment Variables

Edit `.env` with your API keys and settings:

```env
# Required
ANTHROPIC_API_KEY=your_anthropic_api_key
OPENAI_API_KEY=your_openai_api_key
ENTREPEDIA_USERNAME=your_username
ENTREPEDIA_PASSWORD=your_password
SECRET_KEY=your-secret-key-32-chars-minimum
JWT_SECRET_KEY=your-jwt-secret-32-chars-minimum

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/entrepedia_db
REDIS_URL=redis://localhost:6379/0

# Optional integrations
PINECONE_API_KEY=your_pinecone_key
NOTION_API_KEY=your_notion_key
```

### 3. Run with Docker (Recommended)

```bash
cd docker
docker-compose up -d
```

This will start:
- Backend API (port 8000)
- Frontend (port 3000)
- PostgreSQL database
- Redis cache
- Nginx reverse proxy

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 💻 Development Setup

### Backend Development

```bash
# Install Python dependencies
pip install -r requirements.txt

# Download required models
python -m spacy download en_core_web_sm

# Set environment
export PYTHONPATH=$PWD
export DATABASE_URL=postgresql://user:password@localhost:5432/entrepedia_db

# Run development server
uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at http://localhost:3000 with hot reload.

### Database Setup

```bash
# Create database
createdb entrepedia_db

# Run migrations (when implemented)
# alembic upgrade head
```

## 📖 Usage Guide

### 1. Document Upload and Processing

Upload documents through the web interface:

1. Navigate to "Upload Files"
2. Drag and drop or select files
3. Choose whether to generate embeddings
4. Monitor processing progress

Supported formats: PDF, DOCX, PPTX, JPG, PNG, MP3, MP4

### 2. Entrepedia Course Scraping

Automatically scrape course materials:

1. Configure Entrepedia credentials in `.env`
2. Use the "Scrape Entrepedia" feature
3. Monitor download progress
4. All files are automatically processed and indexed

### 3. AI Chat Interface

Interact with AI agents:

1. Go to "AI Chat"
2. Choose your agent:
   - **Coach**: For learning guidance and motivation
   - **Strategist**: For comprehensive planning
3. Ask questions or request learning plans
4. Get contextual responses based on your knowledge base

### 4. Learning Plan Creation

Generate personalized learning plans:

```python
# Example API usage
learning_plan = await queryApi.createLearningPlan({
    "topic": "Machine Learning",
    "level": "beginner",
    "duration": "8 weeks"
})
```

### 5. Knowledge Base Search

Search across all processed content:

```python
# Semantic search
results = await queryApi.searchKnowledgeBase(
    "neural networks explanation",
    limit=10
)
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `ANTHROPIC_API_KEY` | Claude API key | Yes | - |
| `OPENAI_API_KEY` | OpenAI API key | Yes | - |
| `ENTREPEDIA_USERNAME` | Entrepedia login | Yes | - |
| `ENTREPEDIA_PASSWORD` | Entrepedia password | Yes | - |
| `DATABASE_URL` | PostgreSQL connection string | Yes | - |
| `REDIS_URL` | Redis connection string | No | redis://localhost:6379/0 |
| `VECTOR_DB_TYPE` | Vector database type | No | faiss |
| `OUTPUT_DIR` | File storage directory | No | ./data/courses |
| `SECRET_KEY` | App secret key | Yes | - |
| `JWT_SECRET_KEY` | JWT signing key | Yes | - |

### Vector Database Options

#### FAISS (Local)
```env
VECTOR_DB_TYPE=faiss
```

#### Pinecone (Cloud)
```env
VECTOR_DB_TYPE=pinecone
PINECONE_API_KEY=your_key
PINECONE_ENVIRONMENT=your_env
```

#### Weaviate (Self-hosted)
```env
VECTOR_DB_TYPE=weaviate
WEAVIATE_URL=http://localhost:8080
```

## 🔌 API Reference

### Authentication

```bash
# Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpassword"

# Use token
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/query/agents"
```

### Document Operations

```bash
# Upload document
curl -X POST "http://localhost:8000/documents/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@document.pdf" \
  -F "create_embeddings=true"

# Scrape Entrepedia
curl -X POST "http://localhost:8000/documents/scrape-entrepedia" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get document stats
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/documents/stats"
```

### AI Agent Queries

```bash
# Ask a question
curl -X POST "http://localhost:8000/query/ask" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do I learn machine learning effectively?",
    "agent_type": "coach",
    "include_knowledge_base": true
  }'

# Create learning plan
curl -X POST "http://localhost:8000/query/learning-plan" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Deep Learning",
    "level": "intermediate",
    "duration": "12 weeks"
  }'
```

## 🧪 Testing

```bash
# Run backend tests
pytest tests/

# Run frontend tests
cd frontend
npm test

# Run integration tests
pytest tests/integration/
```

## 📊 Monitoring

### Health Checks

- **Application**: http://localhost:8000/health
- **Database**: Check PostgreSQL connection
- **Redis**: Check cache connectivity
- **Vector Store**: Verify embedding operations

### Logs

- **Application logs**: `logs/app.log`
- **Scraper logs**: `logs/scraper.log`
- **Processor logs**: `logs/processor.log`
- **Agent logs**: `logs/agent.log`

### Metrics

Monitor key metrics:
- Document processing speed
- Embedding generation time
- Query response time
- API success rates
- Storage usage

## 🔧 Troubleshooting

### Common Issues

#### 1. Document Processing Fails
```bash
# Check Tesseract installation
tesseract --version

# Verify file permissions
ls -la data/courses/

# Check processor logs
tail -f logs/processor.log
```

#### 2. Embedding Generation Slow
```bash
# Check GPU availability
nvidia-smi

# Monitor CPU usage
htop

# Use smaller embedding models
export EMBEDDING_MODEL=all-MiniLM-L6-v2
```

#### 3. Scraper Authentication Issues
```bash
# Verify credentials
curl -u "username:password" https://app.entrepedia.co/login

# Check network connectivity
ping app.entrepedia.co

# Review scraper logs
tail -f logs/scraper.log
```

#### 4. Vector Database Connection
```bash
# FAISS: Check disk space
df -h

# Pinecone: Verify API key
curl -H "Api-Key: YOUR_KEY" https://api.pinecone.io/databases

# Weaviate: Check service status
curl http://localhost:8080/v1/meta
```

## 🚀 Deployment

### Production Deployment

```bash
# Set production environment
export APP_ENV=production
export DEBUG=False

# Use production Docker compose
docker-compose -f docker/docker-compose.prod.yml up -d

# Configure SSL/TLS
# Update nginx.conf with SSL certificates
```

### Scaling Considerations

1. **Database**: Use managed PostgreSQL (AWS RDS, Google Cloud SQL)
2. **Vector Database**: Consider Pinecone for large-scale deployments
3. **File Storage**: Use S3 or similar object storage
4. **Load Balancing**: Add multiple backend replicas
5. **Caching**: Implement Redis clustering

### Security Checklist

- [ ] Use strong secret keys (32+ characters)
- [ ] Enable HTTPS with valid certificates
- [ ] Configure firewall rules
- [ ] Use environment variables for secrets
- [ ] Enable database encryption at rest
- [ ] Implement rate limiting
- [ ] Regular security updates
- [ ] Audit API access logs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### Development Guidelines

- Follow PEP 8 for Python code
- Use TypeScript for frontend development
- Write comprehensive docstrings
- Include unit tests for new features
- Update documentation for API changes

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Anthropic** for Claude AI capabilities
- **OpenAI** for GPT and Whisper models
- **Hugging Face** for transformer models
- **FastAPI** for the excellent web framework
- **React** ecosystem for frontend tools

## 📞 Support

For support and questions:

1. Check the troubleshooting section
2. Search existing GitHub issues
3. Create a new issue with detailed information
4. Include logs and error messages

---

**Built with ❤️ for enhanced learning experiences**