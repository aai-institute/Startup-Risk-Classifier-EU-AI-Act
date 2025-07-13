import os

from dotenv import load_dotenv
from pathlib import Path

import anthropic

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent.parent / ".env")

def claude_search(web_search_model, url):
    """Uses the Claude web search tool to get AI use cases from a given URL.\n
    Inputs: A supported claude model and the URL to search.\n
    Outputs: Full answer text from the web search response. Contains some thinking steps.
    """


    client = anthropic.Anthropic(api_key=os.getenv("MY_ANTHROPIC_KEY"))

    response = client.messages.create(
        model=web_search_model,
        max_tokens=12000,
        messages=[
            {
                "role": "user",
                "content": f"""Identify and list the top 5 AI use cases, AI systems, or artificial intelligence applications on {url} as individual entries (provide fewer if less than 5 exist). For each distinct AI system (treat each AI module, tool, or application as separate even if part of the same platform), provide comprehensive details including:
- What specific data is collected and processed (including biometric, personal, behavioral data)
- How automated decisions are made and what decisions the AI makes
- Level of human oversight (fully automated vs human-in-the-loop vs human review)
- Who is directly affected by the AI system's outputs and decisions
- Specific business impact and consequences of the AI's decisions
- Technical implementation details about functionality, scope, and processing methods
- Whether users/affected parties are informed about AI usage
- Any compliance, privacy, or safety measures mentioned

Present each AI system as a separate, standalone use case with its own complete description, even if they're components of a larger platform. Start each use case with ###### followed by the use case name."""
            }
        ],
        tools=[{
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": 5,
            "allowed_domains": [f"{url}"],

            "user_location": {
                "type": "approximate",
                "city": "Berlin",
                "region": "Berlin",
                "country": "DE",
                "timezone": "Europe/Berlin"
            }
        }]
    )


    # Extract final answer text from response
    text_blocks = [block.text for block in response.content if block.type == 'text' and block.text]
    full_answer = ''.join(text_blocks)

    return full_answer


