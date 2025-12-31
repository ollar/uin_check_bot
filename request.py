import aiohttp
import asyncio


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


async def make_request(uin_number):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f'https://www.gosuslugi.ru/api/pay/public/v1/paygate/bill/create?billNumber={uin_number}&interfaceTypeCode=BETA_NOAUTH', 
            headers=headers,
        ) as resp:
            if resp.status == 429:
                return 'неудача, включили капчу, повтори через 5 минут :('
            return await parse_response(resp)


async def check_uin(uin_number, update):
    uin_info = make_request(uin_number)

    await update.message.reply_text(f"{uin_number} - {uin_info}")


def get_bill_info(bill):
    bill_name = bill.get('billName', '')
    bill_amount = bill.get('amount', 0)
    is_bill_paid = bill.get('isPaid', False)

    return f"""
        {bill_name}
        {bill_amount}P
        {'оплачен' if is_bill_paid  else 'не оплачен'}
    """


async def parse_response(resp) -> str:
    try:
        resp_data = await resp.json()
    except:
        return 'неудача';

    error = resp_data.get('error', {})
    error_code = error.get('errorCode', 0)
    error_message = error.get('errorMessage', '')

    if error_code != 0:
        return error_message

    bills = resp_data.get('bills', [])
    bills_info = '\n\n'.join(list(map(get_bill_info, bills)))

    return bills_info
     

if __name__ == '__main__':
    print(asyncio.run(make_request('32167872758206987868')))
