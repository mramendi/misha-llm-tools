"""
title: Smart Web Scrape
author: Misha Ramendik
version: 0.0.1
"""

import asyncio
from smart_scrape import smart_scraper


class Tools:
    def __init__(self):
        pass

    async def web_scrape_smart(self, url: str) -> str:
        """
        Scrape a web page.

        :param url: The URL of the web page to scrape.
        :return: The scraped and processed content as Markdown, or an error message.
        """
        try:
            return await smart_scraper(url)

        except Exception as e:
            return f"Error scraping web page: {str(e)}"
