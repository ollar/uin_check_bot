from telegram import Update
from telegram import constants
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes 
from dotenv import load_dotenv
import re
import os
import logging
import asyncio

from spider import get_uin_result 


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# set higher logging level for httpx to avoid all GET and POST requests being logged

logging.getLogger("httpx").setLevel(logging.WARNING)


logger = logging.getLogger(__name__)

load_dotenv()
auth_token = os.getenv('telegram_auth_token', '')


async def start(update: Update, context):
    user = update.effective_user

    await update.message.reply_html(
        f'Привет {user.mention_html()}!\nЭто бот проверки УИНов.\nОтправь список УИН в сообщении с разделением по строкам.'
    )


async def handle_help(update: Update, context):
    await update.message.reply_text('Отправь УИНы в сообщении в формате один УИН на строку без пробелов и пунктуации')


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text or ''

    uins = message_text 

    uins_arr = uins.split()
    uins_arr = [re.sub(r'\D', '', item) for item in uins_arr if item]
    uins_arr = [item for item in uins_arr if item]

    await context.bot.send_chat_action(
        chat_id=update.effective_message.chat_id, action=constants.ChatAction.TYPING
    )

    await asyncio.gather(*[get_uin_result(uin_number, update) for uin_number in uins_arr])


def main():
    application = Application.builder().token(auth_token).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', handle_help))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

    
if __name__ == '__main__':
    main()
