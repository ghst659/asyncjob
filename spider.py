import asyncio
import dataclasses
import re
import urllib.parse

import aiohttp
import bs4

async def fetch(session: aiohttp.ClientSession,
                url: str) -> bs4.BeautifulSoup:
    """Returns the prettified webpage contents at URL."""
    parts = crack_url(url)
    # logging.info("cracked: %s", parts)f
    async with session.get(url) as response:
        html = await response.text()
        return bs4.BeautifulSoup(html, "html.parser")

def canonurl(url: str) -> str:
    """Returns a canonical url."""
    u = url.casefold()
    if u.startswith(r"http://") or u.startswith(r"https://"):
        return u
    return f"http://{u}"
