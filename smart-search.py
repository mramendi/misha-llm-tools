"""
title: Smart search
author: Misha Ramendik
version: 0.0.1
"""

import asyncio
import os
from smart_scrape import smart_scraper
import openai
from openai import AsyncOpenAI
import datetime
import yaml
import json

SYSTEM_PROMPT_SEARCH = """
You are a highly specialized, high quality web search agent. Your ONLY function is to ALWAYS RELIABLY return search results in a valid YAML format.

**TASK:**
1.  Receive the user's query.
2.  Perform a web search using the available tools.
3.  Identify the **top 5 most relevant results**, EXCLUDING any videos. For these 5 results ONLY, extract the following three items:
    a. The final, public-facing URL.
    b. The page title.
    c. A summary of the page as relevant to the query.
    DO NOT INCLUDE video results, such as YouTube and other sources that are primarily just videos.

**RULES:**
- Your ENTIRE response MUST be a single YAML code block.
- The response MUST start with `results:` and nothing else.
- The response MUST include at least 1 result, and NEVER more than 5 results.
- **CRITICAL:** Never use URLs from `vertexaisearch.cloud.google.com`. You must always find and provide the direct link to the actual public website.
- **GUARDRAIL:** Each result (page, title, summary) in the list MUST be unique. Do not repeat any results.
- **IMPORTANT FORMATTING RULE**: You MUST enclose ALL string values for `page`, `title`, and `summary` in double quotes (").
- Do NOT include ANY introductory text, explanations, apologies, or conversation.
- Do NOT write any text before or after the YAML block.
- Use a 2-space indent for all nested items.

**YAML FORMAT:**
```yaml
results:
  - page: "<the final public URL of the webpage>"
    title: "<page title>"
    summary: "<summary of the page as relevant to the query>"
```

**EXAMPLE:**
```yaml
results:
  - page: "https://www.example.com/"
    title: "Example Domain"
    summary: "The example domain for use in illustrative examples in documents."
  - page: "https://en.wikipedia.org/wiki/Example.com"
    title: "Example.com - Wikipedia"
    summary: "The Wikipedia article detailing the history and purpose of the domain \"example.com\"."
```"""


async def call_model(
    system_prompt: str,
    user_prompt: str,
    api_base: str,
    model: str,
    api_key: str,
) -> str:
    """
    Calls an OpenAI-compatible Chat Completions endpoint.

    Args:
        system_prompt: The content for the 'system' role message.
        user_prompt: The user's question, which will be prefixed to the page content.
        api_base: The base URL of the API endpoint.
        model: The name of the model to use (e.g., "Qwen/Qwen2-7B-Instruct").
        api_key: The API key for authentication.

    Returns:
        The content of the model's response as a string, or an error message.
    """
    try:
        # 1. Instantiate the AsyncOpenAI client with your credentials

        #        print(
        #            "CHECKPOINT 1 =========================================================================================================="
        #        )
        client = AsyncOpenAI(
            api_key=api_key,
            base_url=api_base,
        )

        # 2. Make the asynchronous API call
        print(f"Sending request to model: {model} on base URL: {api_base}")
        chat_completion = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            # Optional: Add other parameters like temperature if needed
            temperature=0.5,
        )
        #        print(
        #            "CHECKPOINT 2 =========================================================================================================="
        #        )

        # 3. Extract and return the response content
        if chat_completion.choices:
            #            print(chat_completion.choices[0])
            return chat_completion.choices[0].message.content.strip()
        else:
            return ""
    except openai.APIConnectionError as e:
        return f"Error: Connection to the API failed for model {model}. Details: {e.__cause__}"
    except Exception as e:
        # 5. Handle potential errors during the API call
        return f"Error: Failed to get a response from the API for model {model}. Details: {e}"


class Tools:
    def __init__(self):
        pass

    async def smart_search(self, query: str) -> str:
        """
        Search the web.

        :param query: The query for which yoy want to search the web
        :return: A list of URLs with summaries, or an error message.
        """

        error_messages = ""
        for model in [
            "gemini-2.5-flash-lite-search",
            "gemini-2.5-flash-search",
            "gemini-2.5-flash-lite-search",
            "gemini-2.5-flash-search",
        ]:
            try:
                yaml_candidate = await call_model(
                    SYSTEM_PROMPT_SEARCH,
                    query,
                    "http://host.containers.internal:4000",
                    model,
                    os.environ.get("OPENAI_API_KEY"),
                )

                yaml_candidate = yaml_candidate.strip()

                if yaml_candidate == "":
                    error_messages = (
                        error_messages + "Empty return from " + model + "\n\n"
                    )
                    continue

                if yaml_candidate.startswith("Error:"):
                    error_messages = error_messages + yaml_candidate + "\n\n"
                    continue

                # backtick removal
                lines = yaml_candidate.splitlines()
                index_start = 0
                if lines[0].startswith("```"):
                    index_start = 1
                index_end = len(lines)
                if lines[-1].startswith("```"):
                    index_end = index_end - 1

                yaml_candidate_clean = "\n".join(lines[index_start:index_end])
                data = yaml.safe_load(yaml_candidate_clean)
                json_result = json.dumps(data, indent=2)
                return json_result
            except Exception as e:
                error_messages = error_messages + str(e) + "\n\n"

        return "Search failed. Accumulated error messages:\n" + error_messages
