# GovAI Bangladesh - FastAPI Backend

AI-powered government information assistant for Bangladesh that provides step-by-step guidance in Bangla for all government-related queries.

## Features

- 🤖 **AI-Powered Responses**: Uses GPT-OSS-120B for intelligent, context-aware answers
- 🔍 **Smart Search**: Integrates SearXNG for finding relevant government information
- 🌐 **Multilingual Support**: Accepts queries in English, Bangla, or Banglish
- 🇧🇩 **Bangla Output**: All responses are provided in Bangla for better accessibility
- 📚 **Source Citations**: Includes references to official government sources
- 🏗️ **Modular Architecture**: Clean separation of concerns with routers and services

## Project Structure

```
govai-backend/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create from .env.example)
├── config/
│   ├── __init__.py
│   └── settings.py        # Configuration and settings
├── models/
│   ├── __init__.py
│   └── schemas.py         # Pydantic models
├── services/
│   ├── __init__.py
│   ├── ai_service.py      # AI/LLM integration
│   └── search_service.py  # SearXNG integration
├── routers/
│   ├── __init__.py
│   └── query_router.py    # API routes
└── utils/
    ├── __init__.py
    └── helpers.py         # Utility functions
```

## Setup Instructions

### 2. Installation

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

### 3. Environment Configuration

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
HF_TOKEN=your_huggingface_token_here
SEARCHXNG_URL=http://localhost:8080
PORT=8000
HOST=0.0.0.0
```

### 4. Running SearXNG (if not already running)

If you don't have SearXNG running, you can use Docker:

```bash
docker pull searxng/searxng
docker run -d -p 8080:8080 searxng/searxng
```

Or follow the official SearXNG installation guide: https://docs.searxng.org/

### 5. Start the Application

```bash
# Development mode (with auto-reload)
python main.py

# Or using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
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
  "timestamp": "2025-10-02T10:30:00"
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
      "title": "Bangladesh Passport",
      "url": "https://www.passport.gov.bd",
      "snippet": "Official passport portal"
    }
  ],
  "timestamp": "2025-10-02T10:30:00",
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
print(response.json())
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
5. **License**: "ড্রাইভিং লাইসেন্স রিনিউ করতে কত টাকা লাগে?"
6. **Business Registration**: "trade license kivabe nibo?"

## Configuration Options

Edit `config/settings.py` to customize:

```python
# AI Model settings
AI_MODEL = "openai/gpt-oss-120b"
MAX_TOKENS = 2000
TEMPERATURE = 0.7

# Search settings
SEARCH_MAX_RESULTS = 5
SEARCH_TIMEOUT = 10
```

## Logging

The application uses Python's logging module. Logs are displayed in the console with the format:

```
2025-10-02 10:30:00 - service_name - INFO - Log message
```

## Error Handling

The API includes comprehensive error handling:

- **400 Bad Request**: Empty or invalid queries
- **500 Internal Server Error**: AI service or search failures
- Fallback responses when AI generation fails

## Production Deployment

For production deployment:

1. Set `reload=False` in `main.py`
2. Use a production WSGI server (e.g., Gunicorn)
3. Configure proper CORS origins
4. Set up SSL/TLS certificates
5. Use environment-specific configurations
6. Implement rate limiting
7. Add authentication if needed

Example with Gunicorn:

```bash
pip install gunicorn
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Troubleshooting

### SearXNG Connection Error
- Ensure SearXNG is running and accessible
- Check the `SEARCHXNG_URL` in your `.env` file
- Test SearXNG directly: `curl http://localhost:8080`

### Hugging Face API Error
- Verify your `HF_TOKEN` is valid
- Check if you have access to Fireworks AI provider
- Ensure your token has not expired

### Import Errors
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version compatibility (3.9+)

## Contributing

Contributions are welcome! Please ensure:
- Code follows PEP 8 style guidelines
- All functions have docstrings
- New features include appropriate logging
- Test changes before submitting

## License

[Add your license here]

## Support

For issues or questions:
- Create an issue in the repository
- Contact: [your-contact-info]

---

**Made with ❤️ for the citizens of Bangladesh**1. Prerequisites

- Python 3.9 or higher
- SearXNG instance (running locally or remotely)
- Hugging Face API token with Fireworks AI access

###