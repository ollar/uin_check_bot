import aiohttp
import asyncio

from app.exceptions import Exception_429, Exception_400, Exception_500, Exception_Json


headers = {
  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:146.0) Gecko/20100101 Firefox/146.0',
  'Accept': 'application/json, text/plain, */*',
  'Content-Type': 'application/json',
  'Accept-Language': 'ru,en-US;q=0.7,en;q=0.3',
  'Accept-Encoding': 'gzip, deflate, br, zstd',
  'Origin': 'https://www.gosuslugi.ru',
  'DNT': '1',
  'Connection': 'keep-alive',
  'Referer': 'https://www.gosuslugi.ru/pay/forPayment?tab=UIN',
  'Sec-Fetch-Dest': 'empty',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Site': 'same-origin',
  'Priority': 'u=0',
  'Pragma': 'no-cache',
  'Cache-Control': 'no-cache',
  'Content-Length': '0',
  'TE': 'trailers',
  # 'X-B3-ParentSpanId': '9cd1e942d752afb9',
  # 'X-B3-Sampled': '1',
  # 'X-B3-SpanId': '010f4a0bf6f57648',
  # 'X-B3-TraceId': '9dcdcb9ba179b927',
}


url = lambda uin_number: f'https://www.gosuslugi.ru/api/pay/public/v1/paygate/bill/create?billNumber={uin_number}&interfaceTypeCode=BETA_NOAUTH' 


async def make_request(uin_number) -> aiohttp.ClientResponse:
    async with aiohttp.ClientSession() as session:
        return await session.post(
            url(uin_number),
            headers=headers,
        )


async def check_uin(uin_number, update):
    resp = await make_request(uin_number)
    resp_data = {}
    
    try:
        resp_data = await parse_response(resp)
        uin_info = get_uin_info(resp_data)
    except Exception_429:
        uin_info = 'включили капчу, повторите через 1 - 2 часа'
    except (Exception_500, Exception_400, Exception_Json, Exception):
        uin_info = 'неудача'

    await update.message.reply_text(f"{uin_number} - {uin_info}")

    return (uin_number, resp_data)
    

def get_uin_info(resp_data):
    error = resp_data.get('error', {})
    error_code = error.get('errorCode', 0)
    error_message = error.get('errorMessage', '')

    if error_code != 0:
        return error_message

    bills = resp_data.get('bills', [])
    bills_info = '\n\n'.join(list(map(get_bill_info, bills)))

    return bills_info


def get_bill_info(bill):
    bill_name = bill.get('billName', '')
    bill_amount = bill.get('amount', 0)
    is_bill_paid = bill.get('isPaid', False)

    return f"{bill_name}\n{bill_amount}₽\n{'**оплачен**' if is_bill_paid  else '**не оплачен**'}"


def get_uin_total(uins: list[tuple[str, dict]]):
    def get_bill_info(bill):
        is_bill_paid = bill.get('isPaid', False)

        return f"{'**оплачен**' if is_bill_paid  else '**не оплачен**'}"

    def get_uin_info(uin_tuple: tuple[str, dict]):
        uin_number, uin_data = uin_tuple
        bills = uin_data.get('bills', [])

        if len(bills) == 0:
            return f'{uin_number} - **нет данных**'

        return f'{uin_number} - {'\n'.join(list(map(get_bill_info, bills)))}'

    return '\n'.join(list(map(get_uin_info, uins)))


async def parse_response(resp):
    if resp.status >= 500:
        raise Exception_500

    if resp.status == 429:
        raise Exception_429

    if resp.status >= 400: 
        raise Exception_400

    try:
        resp_data = await resp.json()
    except:
        raise Exception_Json

    return resp_data
     

if __name__ == '__main__':
    print(asyncio.run(make_request('32167872758206987868')))
