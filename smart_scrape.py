import os
import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import stealth
from markdownify import markdownify as md
import trafilatura


async def smart_scraper(url: str) -> str:
    """
    A smart scraper using a browser context and a proxy.
    """
    playwright_ws_url = os.environ.get("PLAYWRIGHT_WS_URL")
    if not playwright_ws_url:
        raise ValueError("PLAYWRIGHT_WS_URL environment variable is not set.")

#    f=open("call-logged","w")
#    f.write("URL:\n\n"+url+"\n")


    html_content = ""
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect(playwright_ws_url)

            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
            )

            # Apply stealth measures to the entire context
            await stealth.stealth_async(context)

            page = await context.new_page()

            #           print(f"Navigating to {url} via proxy...")
            await page.goto(url, wait_until="domcontentloaded", timeout=90000)
            await page.wait_for_selector('body', timeout=15000)
            await page.wait_for_load_state("networkidle", timeout=30000)
            html_content = await page.content()
#            f.write("HTML RAW:\n\n"+html_content+"\n")

            # Close the context, which also closes the page
            await context.close()
        #            print("Scraping complete.")
        except Exception as e:
            raise
    #            print(f"An error occurred during Playwright operation: {e}")
    #            return ""

    if not html_content:
        return "NO CONTENT FOUND"

#    open("dog-save.html","w").write(html_content)

    #    print("Extracting content with Trafilatura...")
    extracted_html = trafilatura.extract(
        html_content,
        favor_recall=True,
        include_tables=True,
        include_comments=True,
        include_links=False,
        deduplicate=True,
        output_format="html",
    )

#    f.write("HTML EXTRACTED:\n\n"+extracted_html+"\n")


    if not extracted_html:
        return "Trafilatura could not find a main content block."

    #    print("Converting to Markdown...")
    markdown_text = md(extracted_html, heading_style="ATX")

    return markdown_text
