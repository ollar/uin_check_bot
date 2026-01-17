from datetime import datetime
import pytest
from telegram import Update, Message, User, Chat, Bot
from telegram.ext import ContextTypes
from unittest.mock import AsyncMock
from app.routes import start 


@pytest.mark.asyncio
async def test_start_command():
    user = User(id=123, is_bot=False, first_name="Test")
    chat = Chat(id=456, type="private")
    bot = AsyncMock(spec=Bot)

    message = Message(
        message_id=1,
        from_user=user,
        chat=chat,
        text="/start",
        date=datetime.now(),
    )
    message.set_bot(bot)
    update = Update(update_id=1, message=message)

    context = AsyncMock(spec=ContextTypes.DEFAULT_TYPE)

    await start(update, context)

    bot.send_message.assert_called_once()
    call_args = bot.send_message.call_args.kwargs

    assert call_args['chat_id'] == 456
    assert call_args['text'] == 'Привет None!\nЭто бот проверки УИНов.\nОтправь список УИН в сообщении с разделением по строкам.'

