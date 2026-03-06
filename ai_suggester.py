from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    groq_api_key=api_key
)

def get_ai_suggestions(code):
    """
    Send code to AI model and get suggestions.
    """
    prompt = f"""
    You are a code reviewer.

    Review the following Python code and give suggestions
    for improvement, best practices, and potential issues.

    Code:
    {code}
    """

    response = llm.invoke(prompt)

    return response.content


if __name__ == "__main__":

    print("Paste your Python code below (Press ENTER twice to finish):")

    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)

    user_code = "\n".join(lines)

    suggestions = get_ai_suggestions(user_code)

    print("\n🤖 AI Suggestions:\n")
    print(suggestions)