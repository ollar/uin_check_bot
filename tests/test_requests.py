import pytest
import json
import os
from aioresponses import aioresponses
import aiohttp
from tests.fixtures import aiohttp_response
from app.request import get_bill_info, make_request, parse_response, url


URL_PATTERN = url('123') 
SUCCESS_RESP_PATTERN = '**оплачен**'
FAILURE_RESP_PATTERN = '**не оплачен**'

payed_response = {}
with open(os.path.join(os.getcwd(), 'tests/responses/payed_response.json'), 'r') as file:
    payed_response = json.loads(file.read())

async def payed_json():
    return payed_response

unpayed_response = {}
with open(os.path.join(os.getcwd(), 'tests/responses/unpayed_response.json'), 'r') as file:
    unpayed_response = json.loads(file.read())

async def unpayed_json():
    return unpayed_response

@pytest.mark.asyncio
async def test_make_request():
    with aioresponses() as m:
        m.post(URL_PATTERN)
        m.post(URL_PATTERN, status=500)
        m.post(URL_PATTERN, status=429)

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
async def test_parse_response(aiohttp_response):

    resp = aiohttp_response(status=500)
    assert await parse_response(resp) == 'неудача'

    resp = aiohttp_response(status=200, json=payed_json)
    assert SUCCESS_RESP_PATTERN in await parse_response(resp) 

    resp = aiohttp_response(status=200, json=unpayed_json)
    assert FAILURE_RESP_PATTERN in await parse_response(resp) 

    resp = aiohttp_response(status=429)
    assert await parse_response(resp) == 'неудача, включили капчу, повтори через 5 минут :('


@pytest.mark.asyncio
async def test_get_bill_info():
    bills = payed_response.get('bills', [])
    bill = bills[0]
    bill_info = get_bill_info(bill)
    assert SUCCESS_RESP_PATTERN in bill_info

    bills = unpayed_response.get('bills', [])
    bill = bills[0]
    bill_info = get_bill_info(bill)
    assert FAILURE_RESP_PATTERN in bill_info

