# Complete Deployment Guide for Render.com

## Project Overview
This project consists of two main services:
1. **RAG Backend** (`app.py`) - Main Flask API for PDF processing and chat
2. **Telegram Bot** (`telegram-rag-bot/`) - Webhook server for Telegram integration

## Required Environment Variables

### For RAG Backend Service:
```
PINECONE_API_KEY=your_pinecone_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
PINECONE_INDEX=career-rag-index
HF_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
PDF_STORAGE_DIR=storage/pdfs
PORT=8000
```

### For Telegram Bot Service:
```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
BACKEND_URL=http://rag-backend-service-name:8000
WEBHOOK_URL=https://telegram-bot-service-name.onrender.com
PORT=10000
```

## Step-by-Step Render Deployment

### 1. Deploy RAG Backend
- **Service Name**: `rag-backend-api`
- **Root Directory**: (leave empty)
- **Runtime**: Docker
- **Port**: 8000
- **Environment Variables**: Add all RAG Backend variables above

### 2. Deploy Telegram Bot
- **Service Name**: `telegram-rag-webhook`
- **Root Directory**: `telegram-rag-bot`
- **Runtime**: Docker
- **Port**: 10000
- **Environment Variables**: 
  - `TELEGRAM_BOT_TOKEN`: Your bot token
  - `BACKEND_URL`: `http://rag-backend-api:8000` (use the service name from step 1)
  - `WEBHOOK_URL`: Leave blank initially, update after deployment

### 3. Finalize Webhook URL
After both services are deployed:
1. Copy the public URL of your Telegram Bot service (e.g., `https://telegram-rag-webhook-xxxx.onrender.com`)
2. Update the `WEBHOOK_URL` environment variable in your Telegram Bot service
3. Redeploy the Telegram Bot service

## Troubleshooting

### Common Issues:
1. **Build Failures**: Ensure all environment variables are set
2. **Model Download Timeouts**: The `sentence-transformers` package downloads large models. This may take time on first deployment.
3. **Memory Issues**: Consider upgrading to a paid Render plan if you encounter memory limits.

### Testing:
1. Test RAG Backend: `GET https://your-rag-backend.onrender.com/admin/health`
2. Test Telegram Bot: Send `/start` to your bot in Telegram

## File Structure for Deployment:
```
/
├── app.py                          # Main RAG Flask backend
├── backend_requirements.txt        # Backend dependencies
├── Dockerfile                      # Backend Docker config
├── services/                       # Backend services
├── telegram-rag-bot/
│   ├── Dockerfile                  # Telegram bot Docker config
│   ├── requirements.txt            # Telegram bot dependencies
│   └── src/
│       ├── server.py               # Telegram webhook server
│       └── telegram_bot.py         # Telegram bot logic
└── storage/                        # PDF storage directory
```
