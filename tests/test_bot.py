import asyncio
import pytest
from app.routes import start, echo
from tests.fixtures import create_bot_message, url_pattern, responses 
from aioresponses import aioresponses, CallbackResult
from app.request import reset_selected_proxy

 
@pytest.mark.asyncio
async def test_start_command(create_bot_message):
    bot, update, context = create_bot_message('/start')

    await start(update, context)

    bot.send_message.assert_called_once()
    call_args = bot.send_message.call_args.kwargs

    assert call_args['chat_id'] == 456
    assert call_args['text'] == 'Привет tester!\nЭто бот проверки УИНов.\nОтправь список УИН в сообщении с разделением по строкам.'


@pytest.mark.asyncio
async def test_echo_command(create_bot_message, url_pattern, responses):
    bot, update, context = create_bot_message('111 222 333 444 555 666 777 888 999 000')

    with aioresponses() as m:
        m.post(url_pattern, payload=responses.payed_response, repeat=True)
        # m.post(URL_PATTERN, status=500)
        # m.post(URL_PATTERN, status=429)


        await echo(update, context)

        bot.send_chat_action.assert_called_once()
        assert bot.send_message.call_count == 10 + 1 # +1 is total message 


@pytest.mark.asyncio
async def test_echo_get_429(create_bot_message, url_pattern, responses):
    # ====================================== request uin, get 429, show captcha message
    reset_selected_proxy()
    bot, update, context = create_bot_message('111')

    with aioresponses() as m:
        m.post(url_pattern, status=429, repeat=True)
        
        await echo(update, context)

        bot.send_message.assert_called_once()
        call_args = bot.send_message.call_args.kwargs

        assert 'капчу' in call_args['text'] 

    # ===================================== request 10 uins, recover, success
    reset_selected_proxy()
    bot, update, context = create_bot_message('111 222 333 444 555 666 777 888 999 000')

    with aioresponses() as m:
        m.post(url_pattern, payload=responses.payed_response, repeat=4)
        m.post(url_pattern, status=429)
        m.post(url_pattern, payload=responses.payed_response)
        m.post(url_pattern, payload=responses.payed_response, repeat=4)
        m.post(url_pattern, payload=responses.payed_response)
        # m.post(url_pattern, status=429, repeat=True)

        await echo(update, context)

        bot.send_chat_action.assert_called_once()
        assert bot.send_message.call_count == 10 + 1 # +1 is total message 

    # ===================================== request 10 uins, 4 success, recover, 1 success, 4 success, show captcha message
    reset_selected_proxy()
    bot, update, context = create_bot_message('111 222 333 444 555 666 777 888 999 000')

    with aioresponses() as m:
        m.post(url_pattern, payload=responses.payed_response, repeat=4)
        m.post(url_pattern, status=429)
        m.post(url_pattern, payload=responses.payed_response)
        m.post(url_pattern, payload=responses.payed_response, repeat=4)
        m.post(url_pattern, status=429, repeat=True)

        await echo(update, context)

        bot.send_chat_action.assert_called_once()
        assert bot.send_message.call_count == 4 + 1 + 4 + 1 # +1 is total message

        call_args = bot.send_message.call_args.kwargs

        assert 'капчу' in call_args['text'] 


@pytest.mark.asyncio
async def test_echo_get_proxy_timeout(create_bot_message, url_pattern, responses):
    bot, update, context = create_bot_message('111')

    attempt = 0

    async def callback(url, **kwargs):
        nonlocal attempt
        
        if attempt < 1:
            attempt += 1
            await asyncio.sleep(6)

        return CallbackResult(payload=responses.payed_response)

    with aioresponses() as m:
        m.post(url_pattern, callback=callback)

        await echo(update, context)

        bot.send_chat_action.assert_called_once()
        assert bot.send_message.call_count == 1 # +1 is total message 


@pytest.mark.asyncio
async def test_echo_get_proxy_timeout_with_multiple_messages(create_bot_message, url_pattern, responses):
    bot, update, context = create_bot_message('111 222 333 444 555 666 777 888 999 000')
    attempt = 0

    async def callback(url, **kwargs):
        nonlocal attempt

        print(attempt)
        
        if attempt % 3 == 0:
            attempt += 1
            await asyncio.sleep(6)

        return CallbackResult(payload=responses.payed_response)

    with aioresponses() as m:
        m.post(url_pattern, callback=callback, repeat=True)

        await echo(update, context)

        call_args = bot.send_message.call_args.kwargs

        assert call_args['text']

