So here's a three-step search, which works in OpenWebUI but is a bit overfit to my setup. PRs welcome to make this more universal.

Two of the tools use the same scraper and also some libraries are required. I sorted this by creatind /app/backend/data/site-packages (on mounted storage as part of /app/backend/data), setting PYTHONPATH to this directory, installing stuff into it - by running pip **within the container** (`podman exec -ti container-name bash`). BTW this is what I installed, note verion of playwright-stealth needed to not disrupt OWUI's plder Playwright library:

```
pip install --target /app/backend/data/site-packages playwright-stealth==1.0.5 markdownify trafilatura
```

And then I dropped smart_scrape.py into that same directory, which is on PYTHONPATH so the tools can import it.

My setup uses a local LiteLLM proxy which is why in the search tool I can use the openai library to call to the search-enabled Gemini Flash models. An excerpt of the LiteLLM proxy config is provided. The bug advantage is that Gemini has a generous free tier (500 searches a day! That is, you get 1000 RPD Gemini 2,5 Flash Lite, 250 RPD Gemini Flash, but inly 500 tootal with Web "grounding". Flash Lite fails much of the time so I fall back to Flash while still trying to use the generous Flash Lite allowance first.

