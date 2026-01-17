from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters 
from dotenv import load_dotenv
from app.routes import start, handle_help, echo
import os
import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

load_dotenv()

auth_token = os.getenv('telegram_auth_token', '')


def main():
    application = Application.builder().token(auth_token).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', handle_help))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

    return application

