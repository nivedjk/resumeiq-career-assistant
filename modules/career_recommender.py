import ollama

def recommend_roles(resume_text, model_name="llama3"):

    prompt = f"""
You are a career advisor.

Analyze this resume and provide:

1. Top 5 suitable job roles
2. Reason for each role
3. Skills to improve

Resume:

{resume_text}
"""

    response = ollama.chat(
        model=model_name,
        messages=[
            {
                "role":"user",
                "content":prompt
            }
        ]
    )

    return response["message"]["content"]