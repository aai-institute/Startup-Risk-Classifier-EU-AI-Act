__all__ = ["gemini_api", "mistral_api"]

import os
import google.generativeai as genai
from mistralai import Mistral

from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

def gemini_api(model, prompt):

    genai.configure(api_key=os.getenv("GEMINI"))

    # Create the model
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
    model_name=model,
    generation_config=generation_config,
    )

    chat_session = model.start_chat(
        history=[
        ]
    )

    response = chat_session.send_message(prompt)

    # print(response.text)
    input_tokens = response.usage_metadata.prompt_token_count
    output_tokens = response.usage_metadata.candidates_token_count
    reponse_message = response.text

    return reponse_message, input_tokens, output_tokens


def mistral_api(model, prompt):
    client = Mistral(api_key=os.getenv("MISTRAL"))

    chat_response = client.chat.complete(
        model = model,
        messages = [
            {
                "role": "user",
                "content": prompt,
            },
        ]
    )

    input_tokens = chat_response.usage.prompt_tokens
    output_tokens = chat_response.usage.completion_tokens
    reponse_message = chat_response.choices[0].message.content

    return reponse_message, input_tokens, output_tokens


