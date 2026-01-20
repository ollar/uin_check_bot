import pytest
from aioresponses import aioresponses
import aiohttp
from tests.fixtures import aiohttp_response, url_pattern, responses
from app.request import get_bill_info, make_request, parse_response 


SUCCESS_RESP_PATTERN = '**оплачен**'
FAILURE_RESP_PATTERN = '**не оплачен**'


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

    resp = aiohttp_response(status=500)
    assert await parse_response(resp) == 'неудача'

    resp = aiohttp_response(status=200, json=responses.get_payed_json)
    assert SUCCESS_RESP_PATTERN in await parse_response(resp) 

    resp = aiohttp_response(status=200, json=responses.get_unpayed_json)
    assert FAILURE_RESP_PATTERN in await parse_response(resp) 

    resp = aiohttp_response(status=429)
    assert await parse_response(resp) == 'неудача, включили капчу, повтори через 5 минут :('


@pytest.mark.asyncio
async def test_get_bill_info(responses):
    bills = responses.payed_response.get('bills', [])
    bill = bills[0]
    bill_info = get_bill_info(bill)
    assert SUCCESS_RESP_PATTERN in bill_info

    bills = responses.unpayed_response.get('bills', [])
    bill = bills[0]
    bill_info = get_bill_info(bill)
    assert FAILURE_RESP_PATTERN in bill_info

