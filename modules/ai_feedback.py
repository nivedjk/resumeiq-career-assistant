import ollama

def get_feedback(resume, jd, model_name="llama3"):

    prompt = f"""
Resume:
{resume}

Job Description:
{jd}

Analyze the resume against the job description.

Provide:

1. Match Summary
2. Strengths
3. Missing Skills
4. Suggestions to Improve
"""

    response = ollama.chat(
        model=model_name,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]