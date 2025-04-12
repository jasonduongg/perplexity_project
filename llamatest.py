import ollama

model = 'hf.co/CompendiumLabs/bge-base-en-v1.5-gguf'
text = "This is a test."

response = ollama.embed(model=model, input=text)
print(response)
