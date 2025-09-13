# Telegram RAG Chatbot Integration

This directory contains the necessary code to integrate a Telegram bot client with your existing RAG Flask backend.

## Features
- Telegram bot using `python-telegram-bot` with webhooks.
- Flask server to expose the webhook endpoint.
- Loads configuration from a `.env` file.
- Handles `/start` and `/help` commands.
- Processes text messages by sending queries to the RAG backend's `/chat` endpoint.
- Handles PDF uploads by sending files to the RAG backend's `/ingest` endpoint, using the user's Telegram ID as the namespace.
- Implements error handling with user-friendly messages.

## Setup Instructions

### 1. Create a Telegram Bot
1. Open Telegram and search for `@BotFather`.
2. Send the `/newbot` command.
3. Follow the instructions to choose a name and a username for your bot.
4. `@BotFather` will provide you with an `HTTP API Token` (e.g., `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`). Keep this token safe.

### 2. Configure Environment Variables
Create a `.env` file inside the `telegram-rag-bot` directory with the following variables:

```
TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN_HERE
BACKEND_URL=http://localhost:8000 # Or the URL of your RAG Flask backend
WEBHOOK_URL=https://your-public-domain.com/telegram-webhook # Public HTTPS URL for your webhook
```

- **`TELEGRAM_BOT_TOKEN`**: The API token you received from `@BotFather`.
- **`BACKEND_URL`**: The URL where your main RAG Flask backend is running (e.g., `http://localhost:8000` if running locally, or its public URL if deployed).
- **`WEBHOOK_URL`**: This MUST be a publicly accessible **HTTPS** URL. Telegram requires secure connections for webhooks. For local testing, you can use tools like `ngrok`.

**Example `.env` for local testing with `ngrok`:**
(Assuming `ngrok` provides `https://your-ngrok-id.ngrok-free.app`)
```
TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN_HERE
BACKEND_URL=http://localhost:8000
WEBHOOK_URL=https://your-ngrok-id.ngrok-free.app/telegram-webhook
```

### 3. Install Dependencies
Navigate to the `telegram-rag-bot` directory and install the required Python packages:

```bash
cd telegram-rag-bot
pip install -r requirements.txt
```

### 4. Run the Telegram Bot Server
Make sure your main RAG Flask backend (`app.py`) is running before starting the Telegram bot server.

To run the Telegram bot's Flask server:

```bash
python -m src.server
```

This will start a Flask server on `http://0.0.0.0:8443` and attempt to set the Telegram webhook to `${WEBHOOK_URL}/${BOT_TOKEN}` at startup.

### 5. Expose the Webhook URL (for local development)
If you are running locally, you need to expose your Flask server to the internet using a tool like `ngrok`.

1. Start `ngrok` for port `8443` (the port the Telegram bot's Flask server runs on):
   ```bash
   ngrok http 8443
   ```
2. `ngrok` will provide you with a public HTTPS URL (e.g., `https://your-ngrok-id.ngrok-free.app`).
3. Update your `WEBHOOK_URL` in the `.env` file to include the `telegram-webhook` path, e.g., `https://your-ngrok-id.ngrok-free.app/telegram-webhook`.
4. Restart the `python -m src.server` process so it picks up the new `WEBHOOK_URL` and sets the webhook correctly.

### 6. Deployment with Docker (Optional)

Refer to the main project's `docker-compose.yml` (or similar Docker setup) for a scalable deployment strategy combining the RAG backend and the Telegram bot.

**Example `docker-compose.yml` snippet for integrating the Telegram bot:**

```yaml
version: "3.9"

services:
  backend:
    build: .
    container_name: rag-backend
    ports:
      - "8000:8000"
    env_file:
      - .env # Your main RAG backend .env file

  telegram-bot:
    build: ./telegram-rag-bot
    container_name: rag-telegram-bot
    ports:
      - "8443:8443"
    env_file:
      - ./telegram-rag-bot/.env # .env file for the Telegram bot
    depends_on:
      - backend
```

**Note for Docker Compose `WEBHOOK_URL` and `BACKEND_URL`:**
- When running with Docker Compose, `BACKEND_URL` in `telegram-rag-bot/.env` should point to the Docker service name of your RAG backend (e.g., `http://backend:8000`).
- `WEBHOOK_URL` still needs to be your public HTTPS URL (e.g., provided by NGINX/ALB in AWS or `ngrok` for local testing).
