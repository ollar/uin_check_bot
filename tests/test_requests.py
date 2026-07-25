import pytest
import asyncio
from aioresponses import aioresponses
import aiohttp
from app.exceptions import Exception_429, Exception_500
from tests.fixtures import aiohttp_response, url_pattern, responses, create_bot_message
from app.request import check_uin, get_bill_info, get_uin_info, get_uin_total, make_request, parse_response 


PAYED_RESP_PATTERN = '<b>оплачен</b>'
UNPAYED_RESP_PATTERN = '<b>не оплачен</b>'
UNKNOWN_RESP_PATTERN = '<b>нет данных</b>'
FAILED_RESP_PATTERN = '<b>неудача</b>'


@pytest.mark.asyncio
async def test_make_request(url_pattern):
    with aioresponses() as m:
        m.post(url_pattern)
        m.post(url_pattern, status=500)
        m.post(url_pattern, status=400)

        resp = await make_request('123')
        assert isinstance(resp, aiohttp.ClientResponse)
        assert resp.status == 200

        resp = await make_request('123')
        assert isinstance(resp, aiohttp.ClientResponse)
        assert resp.status == 500

        resp = await make_request('123')
        assert isinstance(resp, aiohttp.ClientResponse)
        assert resp.status == 400


@pytest.mark.asyncio
async def test_make_request_gather_resend(url_pattern, responses):
    with aioresponses() as m:
        m.post(url_pattern, repeat=10, payload=responses.payed_response)
        m.post(url_pattern, status=429)
        m.post(url_pattern, repeat=5, payload=responses.payed_response)
        m.post(url_pattern, status=429)
        m.post(url_pattern, repeat=True, payload=responses.payed_response)

        sem = asyncio.Semaphore(5)

        async with sem:
            await asyncio.gather(
                make_request('123'), # success requests 
                make_request('123'),
                make_request('123'),
                make_request('123'),
                make_request('123'),
                
                make_request('123'),
                make_request('123'),
                make_request('123'),
                make_request('123'),
                make_request('123'),

                make_request('123'), # get 429, switch proxy, rerequest

                make_request('123'), # success
                make_request('123'),
                make_request('123'),
                make_request('123'),
                
                make_request('123'), # get 429, switch proxy, rerequest

                make_request('123'),
            )


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
        m.post(url_pattern, status=429, repeat=True)

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


@pytest.mark.asyncio
async def test_get_uin_total(responses):
    total = [
        ('111', responses.payed_response),
        ('222', responses.payed_response),
        ('333', responses.payed_response),
        ('444', responses.payed_response),
    ]

    assert get_uin_total(total) == f'Итого:\n111 - {PAYED_RESP_PATTERN}\n222 - {PAYED_RESP_PATTERN}\n333 - {PAYED_RESP_PATTERN}\n444 - {PAYED_RESP_PATTERN}'

    total = [
        ('111', responses.payed_response),
        ('222', responses.unpayed_response),
        ('333', responses.payed_response),
        ('444', responses.unpayed_response),
    ]

    assert get_uin_total(total) == f'Итого:\n111 - {PAYED_RESP_PATTERN}\n222 - {UNPAYED_RESP_PATTERN}\n333 - {PAYED_RESP_PATTERN}\n444 - {UNPAYED_RESP_PATTERN}'

    total = [
        ('111', responses.unpayed_response),
        ('222', responses.unpayed_response),
        ('333', responses.unpayed_response),
        ('444', responses.unpayed_response),
    ]

    assert get_uin_total(total) == f'Итого:\n111 - {UNPAYED_RESP_PATTERN}\n222 - {UNPAYED_RESP_PATTERN}\n333 - {UNPAYED_RESP_PATTERN}\n444 - {UNPAYED_RESP_PATTERN}'

    total = [
        ('111', responses.payed_response),
        ('222', {}),
        ('444', {}),
    ]

    assert get_uin_total(total) == f'Итого:\n111 - {PAYED_RESP_PATTERN}\n222 - {UNKNOWN_RESP_PATTERN}\n444 - {UNKNOWN_RESP_PATTERN}'

