from playwright.async_api import async_playwright


INPUT_SELECTOR = '#uin-filed-input'
SUBMIT_BUTTON_SELECTOR = '.lookup-button.active'


async def get_uin_result(uin_number, update):
    async with async_playwright() as p:
        browser = await p.firefox.launch()

        page = await browser.new_page()

        print(f'{uin_number=}')
    
        await page.set_viewport_size({"width": 1080, "height": 1024 })

        await page.goto('https://www.gosuslugi.ru/pay/forPayment?tab=UIN',
            wait_until='load'
        )

        try:
            await page.locator(INPUT_SELECTOR).fill(uin_number)
            await page.locator(SUBMIT_BUTTON_SELECTOR).click()

            # await page.screenshot(path=f'{uin_number}-request.png')

            await page.wait_for_load_state('networkidle')

            results = await page.locator('.unauth-bills-container').evaluate('el => el.innerText')

            # await page.screenshot(path=f'{uin_number}-result.png')
        except Exception as e:
            print(e)
            # await page.screenshot(path=f'{uin_number}-fail.png')

            results = 'неудача' 

        await browser.close()

        await update.message.reply_text(f"{uin_number} - {results}")

