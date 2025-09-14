
import requests
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramRAGBot:
    def __init__(self, bot_token: str, backend_url: str):
        self.backend_url = backend_url
        self.application = Application.builder().token(bot_token).build()

        # Register handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message))
        # Removed PDF upload handler as per user's request
        # self.application.add_handler(MessageHandler(filters.Document.PDF, self.handle_pdf_upload))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /start is issued."""
        user = update.effective_user
        await update.message.reply_html(
            f"Hi {user.mention_html()}!\nI am a RAG chatbot. Send me your questions or upload PDFs."
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /help is issued."""
        help_message = (
            "You can interact with me in the following way:\n"
            "- Send a text message: I will answer your questions using my knowledge base."
            # Removed mention of PDF upload from help message
        )
        await update.message.reply_text(help_message)

    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle incoming text messages and query the RAG backend."""
        user_query = update.message.text
        user_id = update.effective_user.id
        logger.info(f"Received text message from {user_id}: {user_query}")

        try:
            # Log the URL and payload before sending
            chat_url = f"{self.backend_url}/chat"
            payload = {'query': user_query, 'namespace': str(user_id)}
            logger.info(f"Sending chat request to RAG backend: URL={chat_url}, Payload={payload}")

            response = requests.post(
                chat_url,
                json=payload,
                timeout=30
            )
            response.raise_for_status() # Raise an exception for HTTP errors
            rag_response = response.json()
            logger.info(f"Received response from RAG backend: {rag_response}")
            answer = rag_response.get('answer', "Sorry, I couldn't get an answer from the RAG backend.")
            await update.message.reply_text(answer)
        except requests.exceptions.RequestException as e:
            logger.error(f"Error communicating with RAG backend: {e}")
            await update.message.reply_text("Sorry, I'm having trouble connecting to the RAG backend. Please try again later.")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            await update.message.reply_text("An unexpected error occurred while processing your request. Please try again later.")

# Removed handle_pdf_upload method as it's no longer needed
# async def handle_pdf_upload(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Handle PDF file uploads and send to the RAG backend for ingestion."""
#     document = update.message.document
#     user_id = update.effective_user.id
#     logger.info(f"Received PDF from {user_id}: {document.file_name}")
#
#     if not document.file_name.lower().endswith('.pdf'):
#         await update.message.reply_text("Please upload a PDF file.")
#         return
#
#     try:
#         # Download the PDF file
#         pdf_file = await context.bot.get_file(document.file_id)
#         pdf_content = requests.get(pdf_file.file_path).content
#
#         files = {'file': (document.file_name, pdf_content, 'application/pdf')}
#         response = requests.post(
#             f"{self.backend_url}/ingest?namespace={user_id}",
#             files=files,
#             timeout=120 # Increased timeout for file uploads
#         )
#         response.raise_for_status()
#         ingest_response = response.json()
#         message = ingest_response.get('message', f"Successfully processed {document.file_name}.")
#         await update.message.reply_text(f"✅ {message}")
#     except requests.exceptions.RequestException as e:
#         logger.error(f"Error ingesting PDF with RAG backend: {e}")
#         await update.message.reply_text("Sorry, I'm having trouble ingesting the PDF with the RAG backend. Please try again later.")
#     except Exception as e:
#         logger.error(f"An unexpected error occurred during PDF ingestion: {e}")
#         await update.message.reply_text("An unexpected error occurred while processing your PDF. Please try again later.")

    def run(self):
        """Starts the bot (for local polling, not for webhooks)."""
        logger.info("Bot started in polling mode. This should not be used for webhook deployments.")
        self.application.run_polling()
