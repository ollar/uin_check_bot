import pytest
from aioresponses import aioresponses
import aiohttp
from app.exceptions import Exception_429, Exception_500
from tests.fixtures import aiohttp_response, url_pattern, responses, create_bot_message
from app.request import check_uin, get_bill_info, get_uin_info, make_request, parse_response 


PAYED_RESP_PATTERN = '**оплачен**'
UNPAYED_RESP_PATTERN = '**не оплачен**'
FAILED_RESP_PATTERN = 'неудача'

@pytest.mark.asyncio
async def test_make_request(url_pattern):
    with aioresponses() as m:
        m.post(url_pattern)
        m.post(url_pattern, status=500)
        m.post(url_pattern, status=429)

        resp = await make_request('123')
        assert isinstance(resp, aiohttp.ClientResponse)
        assert resp.status == 200

        resp = await make_request('123')
        assert isinstance(resp, aiohttp.ClientResponse)
        assert resp.status == 500

        resp = await make_request('123')
        assert isinstance(resp, aiohttp.ClientResponse)
        assert resp.status == 429


@pytest.mark.asyncio
async def test_parse_response(aiohttp_response, responses):
    with pytest.raises(Exception_500):
        resp = aiohttp_response(status=500)
        await parse_response(resp)

    resp = aiohttp_response(status=200, json=responses.get_payed_json)
    assert await parse_response(resp) == responses.payed_response

    resp = aiohttp_response(status=200, json=responses.get_unpayed_json)
    assert await parse_response(resp) == responses.unpayed_response

    with pytest.raises(Exception_429):
        resp = aiohttp_response(status=429)
        await parse_response(resp)


@pytest.mark.asyncio
async def test_get_uin_info(responses):
    assert PAYED_RESP_PATTERN in get_uin_info(responses.payed_response)
    assert UNPAYED_RESP_PATTERN in get_uin_info(responses.unpayed_response)

@pytest.mark.asyncio
async def test_check_uin(url_pattern, create_bot_message, responses):
    
    with aioresponses() as m:
        m.post(url_pattern, payload=responses.payed_response)
        m.post(url_pattern, payload=responses.unpayed_response)
        m.post(url_pattern, status=500)
        m.post(url_pattern, status=400)
        m.post(url_pattern, status=429)

        # ============================= payed
        
        bot, update, context = create_bot_message('')
        
        uin_number, uin_data = await check_uin('123', update)

        bot.send_message.assert_called_once()
        call_args = bot.send_message.call_args.kwargs

        assert PAYED_RESP_PATTERN in call_args['text'] 
        assert uin_number == '123'
        assert uin_data == responses.payed_response

        # ============================= unpayed

        bot, update, context = create_bot_message('')

        uin_number, uin_data = await check_uin('123', update)

        bot.send_message.assert_called_once()
        call_args = bot.send_message.call_args.kwargs

        assert UNPAYED_RESP_PATTERN in call_args['text'] 
        assert uin_number == '123'
        assert uin_data == responses.unpayed_response

        # ============================= 500

        bot, update, context = create_bot_message('')

        uin_number, uin_data = await check_uin('123', update)

        bot.send_message.assert_called_once()
        call_args = bot.send_message.call_args.kwargs

        assert FAILED_RESP_PATTERN in call_args['text'] 
        assert uin_number == '123'
        assert uin_data == {} 

        # ============================= 400

        bot, update, context = create_bot_message('')

        uin_number, uin_data = await check_uin('123', update)

        bot.send_message.assert_called_once()
        call_args = bot.send_message.call_args.kwargs

        assert FAILED_RESP_PATTERN in call_args['text'] 
        assert uin_number == '123'
        assert uin_data == {} 

        # ============================= 429

        bot, update, context = create_bot_message('')

        uin_number, uin_data = await check_uin('123', update)

        bot.send_message.assert_called_once()
        call_args = bot.send_message.call_args.kwargs

        assert 'капчу' in call_args['text'] 
        assert uin_number == '123'
        assert uin_data == {} 


@pytest.mark.asyncio
async def test_get_bill_info(responses):
    bills = responses.payed_response.get('bills', [])
    bill = bills[0]
    bill_info = get_bill_info(bill)
    assert PAYED_RESP_PATTERN in bill_info

    bills = responses.unpayed_response.get('bills', [])
    bill = bills[0]
    bill_info = get_bill_info(bill)
    assert UNPAYED_RESP_PATTERN in bill_info

