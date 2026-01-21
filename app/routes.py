import asyncio
from app.request import check_uin, get_uin_total
from telegram import Update
from telegram.ext import ContextTypes 
from telegram import constants

from app.utils import parse_uins

async def start(update: Update, context):
    user = update.effective_user

    await update.message.reply_text(
        f'Привет {user.username}!\nЭто бот проверки УИНов.\nОтправь список УИН в сообщении с разделением по строкам.'
    )


async def handle_help(update: Update, context):
    await update.message.reply_text('Отправь УИНы в сообщении в формате один УИН на строку без пробелов и пунктуации')


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text or ''

    uins_arr = parse_uins(message_text)

    await context.bot.send_chat_action(
        chat_id=update.effective_message.chat_id, action=constants.ChatAction.TYPING
    )

    sem = asyncio.Semaphore(5)

    async with sem:
        uins_data = await asyncio.gather(*[check_uin(uin_number, update) for uin_number in uins_arr])

    if len(uins_arr) > 1:
        total = get_uin_total(uins_data)

        await update.message.reply_text(total)

        
