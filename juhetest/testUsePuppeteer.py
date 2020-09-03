import asyncio
from pyppeteer import launch
import ssl
ssl._create_default_https_context = ssl._create_unverified_context


async def test():
    browser = await launch()
    page = await browser.newPage()
    await page.goto('http://10.0.32.28:7001/memberAnalysis/groups')
    await page.pdf({'path': 'out.pdf'})
    await browser.close()


asyncio.get_event_loop().run_until_complete(test())
