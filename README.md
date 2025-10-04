# GovAI Bangladesh - FastAPI Backend

AI-powered government information assistant for Bangladesh that provides step-by-step guidance in Bangla for all government-related queries.

## Features

- 🤖 **AI-Powered Responses**: Uses Hugging Face LLMs for intelligent, context-aware answers
- 🔍 **Smart Search**: Integrates Tavily and SerpAPI for finding relevant government information
- 🌐 **Multilingual Support**: Accepts queries in English, Bangla, or Banglish
- 🇧🇩 **Bangla Output**: All responses are provided in Bangla for better accessibility
- 📚 **Source Citations**: Includes references to official government sources
- 🏗️ **Modular Architecture**: Clean separation of concerns with LangGraph workflow
- ⚡ **Fast & Reliable**: Built with FastAPI for high performance

## Project Structure

```
govai_backend/
├── main.py                          # Updated with admin routes
├── requirements.txt                 # Updated with new dependencies
├── .env                            # Environment variables
├── .env.example                    # Environment template
├── logs/                           # Auto-created for query logs
│   └── queries.jsonl              # Query logs (auto-created)
├── static/                         # Static files directory
├── templates/                      # Jinja2 templates
│   └── admin/
│       ├── login.html             # Login page
│       ├── dashboard.html         # Main dashboard
│       ├── logs.html              # Logs viewer
│       └── stats.html             # Statistics page
├── config/
│   └── settings.py                # Updated with admin settings
├── models/
│   ├── schemas.py                 # Existing schemas
│   └── admin_schemas.py           # NEW: Admin data models
├── utils/
│   ├── helpers.py                 # Existing helpers
│   ├── admin_auth.py              # NEW: Authentication utilities
│   └── query_logger.py            # NEW: Query logging system
├── admin/
│   ├── __init__.py               # NEW: Admin package init
│   └── routes.py                 # NEW: Admin routes
└── routers/
    └── query_router.py           # Updated with logging
```

## Prerequisites

- Python 3.9 or higher
- Hugging Face API token
- At least one search API key (Tavily or SerpAPI)

## Setup Instructions

### 1. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd govai-backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
# Required: Hugging Face Token
HF_TOKEN=hf_your_token_here

# Required: At least ONE search API key
TAVILY_API_KEY=tvly_your_key_here
SERPAPI_API_KEY=your_serpapi_key_here

# AI Model Configuration
AI_MODEL=google/gemma-2-2b-it OR openai/gpt-oss-120b
MAX_TOKENS=512
TEMPERATURE=0.7

# Search Configuration
SEARCH_MAX_RESULTS=5

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

**⚠️ IMPORTANT**: Generate a secure secret key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Get API Keys

#### Hugging Face Token (Required)
1. Go to https://huggingface.co/settings/tokens
2. Click "New token"
3. Give it a name and select "Read" access
4. Copy the token (starts with `hf_`)

#### Tavily API (Recommended)
1. Go to https://tavily.com/
2. Sign up for a free account
3. Get your API key from the dashboard
4. Free tier includes 1,000 searches/month

#### SerpAPI (Alternative)
1. Go to https://serpapi.com/
2. Sign up for a free account
3. Get your API key from dashboard
4. Free tier includes 100 searches/month

**Note:** You only need ONE search API key (either Tavily or SerpAPI), though having both provides redundancy.

### 4. Verify Configuration

Run the configuration verification script:

```bash
python verify_config.py
```

This will check if all required API keys are properly configured.

### 5. Start the Application

```bash
# Development mode (with auto-reload)
uvicorn main:app --reload

# Or specify host and port
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at:
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

## API Endpoints

### Health Check
```http
GET /health
```

Response:
```json
{
  "status": "healthy",
  "message": "GovAI Bangladesh API is running",
  "timestamp": "2025-10-03T10:30:00"
}
```

### Process Query
```http
POST /query
```

Request Body:
```json
{
  "query": "How do I apply for a passport?",
  "user_id": "optional_user_id",
  "include_sources": true
}
```

Response:
```json
{
  "query": "How do I apply for a passport?",
  "answer": "পাসপোর্টের জন্য আবেদন করতে নিম্নলিখিত ধাপগুলি অনুসরণ করুন:\n\n১. অনলাইন আবেদন...",
  "sources": [
    {
      "title": "পাসপোর্ট আবেদন - বাংলাদেশ সরকার",
      "url": "https://www.dip.portal.gov.bd/",
      "snippet": "পাসপোর্ট আবেদনের জন্য প্রয়োজনীয় কাগজপত্র...",
      "score": 0.95
    }
  ],
  "timestamp": "2025-10-03T10:30:00",
  "processing_time": 2.5
}
```

## Example Usage

### Using cURL

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "পাসপোর্ট করতে কি কি লাগে?",
    "include_sources": true
  }'
```

### Using Python Requests

```python
import requests

url = "http://localhost:8000/query"
payload = {
    "query": "How to get NID card?",
    "include_sources": True
}

response = requests.post(url, json=payload)
data = response.json()
print(data["answer"])
```

### Using JavaScript Fetch

```javascript
const response = await fetch('http://localhost:8000/query', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    query: 'birth certificate er jonno ki korte hobe?',
    include_sources: true
  })
});

const data = await response.json();
console.log(data.answer);
```

## Supported Query Types

The API can handle various government-related queries in English, Bangla, or Banglish:

- **English**: "How do I apply for a passport?"
- **Bangla**: "আমি কিভাবে পাসপোর্টের জন্য আবেদন করব?"
- **Banglish**: "passport korte ki ki lagbe?"

## Common Use Cases

1. **Passport Applications**: "পাসপোর্ট করতে কি কি ডকুমেন্ট লাগে?"
2. **NID Card**: "জাতীয় পরিচয়পত্র করতে কত সময় লাগে?"
3. **Birth Certificate**: "birth certificate online e kivabe korbo?"
4. **Tax Information**: "আয়কর রিটার্ন দাখিল করার নিয়ম কি?"
5. **Driving License**: "ড্রাইভিং লাইসেন্স রিনিউ করতে কত টাকা লাগে?"
6. **Business Registration**: "trade license kivabe nibo?"
7. **Land Records**: "জমির দলিল যাচাই করব কিভাবে?"
8. **Education**: "SSC certificate হারিয়ে গেলে কি করব?"

## Configuration Options

Edit `config/settings.py` to customize:

```python
# AI Model settings
AI_MODEL = "google/gemma-2-2b-it"  # Recommended for Bangla
MAX_TOKENS = 512
TEMPERATURE = 0.7

# Alternative models:
# AI_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"
# AI_MODEL = "meta-llama/Llama-2-7b-chat-hf"

# Search settings
SEARCH_MAX_RESULTS = 5
```

## Recommended AI Models

For best Bangla language support, use these models:

1. **google/gemma-2-2b-it** (Recommended) - Best Bangla support, fast OR openai/gpt-oss-120b
2. **mistralai/Mistral-7B-Instruct-v0.2** - Good multilingual support
3. **meta-llama/Llama-2-7b-chat-hf** - Requires model access approval

## Architecture

The application uses LangGraph for intelligent query processing:

```
User Query → Language Detection → Search Service → AI Generation → Response
                                     ↓
                                  Tavily/SerpAPI
                                     ↓
                              Government Websites
```

### LangGraph Workflow

1. **Analyze Query** - Understands user intent
2. **Search Information** - Finds relevant sources
3. **Generate Response** - Creates detailed Bangla answer

## Logging

Logs are saved in the `logs/` directory:
- `govai.log` - All logs
- `govai_errors.log` - Error logs only

## Error Handling

The API includes comprehensive error handling:

- **400 Bad Request**: Empty or invalid queries
- **500 Internal Server Error**: AI service or search failures
- Automatic fallback to cached government service information
- Graceful degradation when search APIs are unavailable

## Production Deployment

For production deployment:

### Using Gunicorn

```bash
pip install gunicorn
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Using Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🔐 Accessing the Admin Dashboard

### Login

1. Navigate to: `http://localhost:8000/admin/login`
2. Enter credentials:
   - Username: `admin` (or your custom username)
   - Password: Your password from `.env`

### Dashboard Features

**Main Dashboard** (`/admin/dashboard`):
- Real-time statistics cards
- Query trend charts (last 24 hours)
- Language distribution pie chart
- Top 10 most frequent queries
- Recent queries list

**Logs Page** (`/admin/logs`):
- Complete query logs table
- Search functionality
- Filter by status (success/error)
- Filter by language (Bengali/English/Banglish)
- Export to CSV

**Statistics Page** (`/admin/stats`):
- Detailed performance metrics
- Enhanced visualizations
- Top 20 queries with percentages
- Language breakdown

## 🔒 Security Features

1. **JWT Authentication**: Session-based authentication using JWT tokens
2. **HTTP-Only Cookies**: Tokens stored in secure cookies
3. **Password Hashing**: Using bcrypt (ready for production)
4. **Session Expiration**: Auto-logout after configured time
5. **Protected Routes**: All admin routes require authentication

## 📊 Query Logging

The system automatically logs:
- Query text
- Detected language
- Processing time
- Client IP address
- Success/failure status
- Timestamp

### Production Checklist

- [ ] Set proper CORS origins
- [ ] Use environment-specific configurations
- [ ] Set up SSL/TLS certificates
- [ ] Implement rate limiting
- [ ] Add authentication if needed
- [ ] Set up monitoring and logging
- [ ] Configure backup search API
- [ ] Set DEBUG=False in production

## Troubleshooting

### Search API Connection Error
**Problem**: "No search tool available"  
**Solution**: 
- Verify your API keys in `.env`
- Check if you have either TAVILY_API_KEY or SERPAPI_API_KEY
- Run `python verify_config.py` to diagnose

### Hugging Face API Error
**Problem**: "Task 'text-generation' not supported"  
**Solution**: 
- Make sure you're using a compatible model like openai/gpt-oss-120b
- Change AI_MODEL to `google/gemma-2-2b-it` in `.env`
- Verify your HF_TOKEN is valid

### Unicode/Encoding Errors (Windows)
**Problem**: UnicodeEncodeError in console logs  
**Solution**:
- Use the logging configuration in `config/logging_config.py`
- Run: `chcp 65001` in your terminal before starting
- Or redirect logs to file instead of console

### Import Errors
**Problem**: ModuleNotFoundError  
**Solution**: 
```bash
pip install -r requirements.txt
python -m pip install --upgrade pip
```

## API Rate Limits

### Tavily (Free Tier)
- 1,000 searches per month
- 5 requests per second

### SerpAPI (Free Tier)
- 100 searches per month
- No rate limit

### Hugging Face Inference API (Free)
- Rate limits vary by model
- Consider using HF Pro for production

## Contributing

Contributions are welcome! Please ensure:
- Code follows PEP 8 style guidelines
- All functions have docstrings
- New features include appropriate logging
- Test changes before submitting
- Update README if adding new features

## Testing

```bash
# Run tests (if implemented)
pytest

# Test specific endpoint
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "test query", "include_sources": true}'
```

## Performance

Typical response times:
- Simple queries: 2-5 seconds
- Complex queries: 5-15 seconds
- With search: 15-25 seconds

Factors affecting performance:
- AI model size
- Search API response time
- Query complexity
- Network latency

## Security

- Never commit `.env` file to version control
- Rotate API keys regularly
- Use HTTPS in production
- Implement rate limiting
- Add authentication for public deployment

## 📞 Contact

- GitHub: [yeakiniqra](https://github.com/yeakiniqra)  
- Website: [www.yeakiniqra.com](https://www.yeakiniqra.com)

## Support

For issues or questions:
- Create an issue in the repository
- Check troubleshooting section
- Review logs in `logs/` directory

## Acknowledgments

- Hugging Face for LLM infrastructure
- Tavily for search capabilities
- LangChain for workflow orchestration
- FastAPI for the excellent framework

---

**Made with ❤️ for the citizens of Bangladesh**