import pytest
import aiohttp
from unittest.mock import AsyncMock
from datetime import datetime
from telegram import Update, Message, User, Chat, Bot
from telegram.ext import ContextTypes
import re
import os
import json


@pytest.fixture
def aiohttp_response():
    def create_response(*args, **kwargs): 
        mock = AsyncMock(spec=aiohttp.ClientResponse)

        for key, value in kwargs.items():
            setattr(mock, key, value)
        
        return mock

    return create_response


@pytest.fixture
def create_bot_message():
    def create_context(text):
        user = User(id=123, is_bot=False, first_name="Test", username="tester")
        chat = Chat(id=456, type="private")
        bot = AsyncMock(spec=Bot)

        message = Message(
            message_id=1,
            from_user=user,
            chat=chat,
            text=text,
            date=datetime.now(),
        )
        message.set_bot(bot)
        update = Update(update_id=1, message=message)

        context = AsyncMock(spec=ContextTypes.DEFAULT_TYPE)
        context.bot = bot

        return bot, update, context

    return create_context


@pytest.fixture
def url_pattern():
    return re.compile(r'^https://www.gosuslugi.ru/api/pay/public/v1/paygate.*$')


@pytest.fixture
def responses():
    class Resp():
        payed_response = {}
        unpayed_response = {}

        def __init__(self):
            with open(os.path.join(os.getcwd(), 'tests/responses/payed_response.json'), 'r') as file:
                self.payed_response = json.loads(file.read())

            with open(os.path.join(os.getcwd(), 'tests/responses/unpayed_response.json'), 'r') as file:
                self.unpayed_response = json.loads(file.read())
            

        async def get_payed_json(self):
            return self.payed_response
        

        async def get_unpayed_json(self):
            return self.unpayed_response


    return Resp()


