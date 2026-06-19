import ollama

def career_chat(
    messages,
    model_name="llama3"
):
    response = ollama.chat(
        model=model_name,
        messages=messages
    )

    return response["message"]["content"]