from bs4 import BeautifulSoup
import httpx

async def crawl_links(urls: list):
    content = []
    async with httpx.AsyncClient() as client:
        for url in urls:
            response = await client.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            text = soup.get_text()
            content.append({"url": url, "text": text})
    return content