"""
title: Web page query
author: Misha Ramendik
version: 0.0.1
"""

import asyncio
import os
from smart_scrape import smart_scraper
import openai
from openai import AsyncOpenAI
import datetime

SYSTEM_PROMPT_VERBATIM = """
You are a precise text-extraction tool. From the provided page, extract the LITERAL text snippets that DIRECTLY ANSWER the user's query.

- You MUST return ONLY EXACT text from the page. Do not summarize, paraphrase, or alter it.
- Be highly selective. Only extract the paragraphs, lists, or tables that contain the specific answer.
- AVOID including paragraphs that only provide general context or tangential information.
- If no part of the text directly answers the query, return only the phrase: "No direct answer found in the provided text."
"""

SYSTEM_PROMPT_NON_VERBATIM = """
You are a document analysis system. Your task is to answer the user's query based ONLY on the provided text.

- YOU MUST NOT use your internal knowledge or any information not present in the text.
- For every statement you make, you MUST back it up with a direct quote from the text.
- Format the quote on a new line immediately after the statement, using Markdown blockquotes.
- Example of the required format:
  The study found that proxies were a key factor for success.
  > "The study suggests that a multi-layered approach using residential proxies is key to comprehensive website recovery."
"""


async def call_model_with_page(
    system_prompt: str,
    user_prompt: str,
    page: str,
    api_base: str,
    model: str,
    api_key: str,
) -> str:
    """
    Calls an OpenAI-compatible Chat Completions endpoint with structured prompts.

    Args:
        system_prompt: The content for the 'system' role message.
        user_prompt: The user's question, which will be prefixed to the page content.
        page: The large string of web page content.
        api_base: The base URL of the API endpoint.
        model: The name of the model to use (e.g., "Qwen/Qwen2-7B-Instruct").
        api_key: The API key for authentication.

    Returns:
        The content of the model's response as a string, or an error message.
    """
    try:
        # 1. Instantiate the AsyncOpenAI client with your credentials
        client = AsyncOpenAI(
            api_key=api_key,
            base_url=api_base,
        )

        # 2. Construct the full user-role prompt with a clear divider
        full_user_prompt = f"QUERY:\n{user_prompt}\n\n---\n\nPAGE:\n\n{page}"

        # 3. Make the asynchronous API call
        print(f"Sending request to model: {model}...")
        chat_completion = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": full_user_prompt},
            ],
            # Optional: Add other parameters like temperature if needed
            temperature=0.5,
        )

        # 4. Extract and return the response content
        if chat_completion.choices:
            #            print(chat_completion.choices[0])
            return chat_completion.choices[0].message.content.strip()
        else:
            return "Error: The API returned no response choices."
    except openai.APIConnectionError as e:
        return f"Error: Connection to the API failed. Details: {e.__cause__}"
    except Exception as e:
        # 5. Handle potential errors during the API call
        print(f"An error occurred: {e}")
        return f"Error: Failed to get a response from the API. Details: {e}"


class Tools:
    def __init__(self):
        pass

    async def web_page_query(self, url: str, query: str, verbatim: bool = False) -> str:
        """
        Get citations or answers from a web page. If possible, YOU MUST use this instead of a full scrape to save context space

        :param url: The URL of the web page to explore
        :param query: The query that you want answered based on the web page
        :param verbatim: True to get verbatim quotes from the page that directly answer the query, False to get an answer with citations
        :return: The scraped and processed content as Markdown, or an error message.
        """

        timestamp = (
            datetime.datetime.now().replace(microsecond=0).isoformat().replace(":", "_")
        )
        scraped_page = ""
        try:
            scraped_page = await smart_scraper(url)

        except Exception as e:
            return f"Error scraping web page: {str(e)}"

        print("SCRAPED: " + scraped_page)

        system_prompt = (
            SYSTEM_PROMPT_VERBATIM if verbatim else SYSTEM_PROMPT_NON_VERBATIM
        )

        result = ""
        try:
            result = await call_model_with_page(
                system_prompt,
                query,
                scraped_page,
                "http://host.containers.internal:4000",
                "Qwen3 235B A22B Thinking 2507",
                os.environ.get("OPENAI_API_KEY"),
            )
        except Exception as e:
            return f"Error calling secretary model: {str(e)}"

        print("RESULT: " + result)

        #        print(result)

        return result
