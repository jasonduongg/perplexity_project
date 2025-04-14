from openai import OpenAI
from dotenv import load_dotenv
import os
from typing import List

# Load env and set API key
load_dotenv()
client = OpenAI()  # Uses OPENAI_API_KEY from environment

CHAT_MODEL = "gpt-3.5-turbo"

def get_response(query: str, context_chunks: List[str]):
    context = "\n\n".join(context_chunks)
    prompt = f"""You are a helpful assistant. Use the following information to answer the question.

Context:
{context}

Question: {query}
Answer:"""

    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "user", "content": prompt}
        ],
        stream=True
    )

    for chunk in response:
        if chunk.choices and chunk.choices[0].delta.content:
            yield {"message": {"content": chunk.choices[0].delta.content}}
