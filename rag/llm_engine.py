import ollama

LANGUAGE_MODEL = 'hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF'

def build_prompt(context_chunks):
    return (
        "You are a helpful chatbot.\n"
        "Use only the following pieces of context to answer the question. Don't make up any new information:\n" +
        '\n'.join([f' - {chunk}' for chunk in context_chunks])
    )

def get_response(query, context_chunks):
    prompt = build_prompt(context_chunks)
    response = ollama.chat(
        model=LANGUAGE_MODEL,
        messages=[
            {'role': 'system', 'content': prompt},
            {'role': 'user', 'content': query}
        ],
        stream=True,
    )
    return response
