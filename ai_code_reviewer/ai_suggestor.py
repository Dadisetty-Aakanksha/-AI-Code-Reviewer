"""
ai_suggestor.py
Handles AI-powered code review using Groq's LLaMA model via LangChain.
"""

import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()


def get_ai_suggestions(code: str, language: str = "python") -> dict:
    """
    Send code to Groq LLaMA for AI-powered review.
    Returns a dict with suggestions, security issues, and optimizations.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return {
            "suggestions": ["⚠️ GROQ_API_KEY not found. Please add it to your .env file."],
            "security_issues": [],
            "optimizations": [],
            "summary": "API key missing.",
        }

    try:
        llm = ChatGroq(
            groq_api_key=api_key,
            model_name="llama-3.1-8b-instant",
            temperature=0.3,
        )

        system_prompt = """You are an expert code reviewer. Analyze the given code and respond ONLY in the following JSON format (no markdown, no extra text):
{
  "suggestions": ["suggestion1", "suggestion2"],
  "security_issues": ["issue1", "issue2"],
  "optimizations": ["opt1", "opt2"],
  "summary": "A brief 2-sentence overall review."
}"""

        user_prompt = f"Review this {language} code:\n\n```{language}\n{code}\n```"

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]

        response = llm.invoke(messages)
        raw = response.content.strip()

        # Clean up markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        result = json.loads(raw)
        return result

    except Exception as e:
        return {
            "suggestions": [f"AI review failed: {str(e)}"],
            "security_issues": [],
            "optimizations": [],
            "summary": "Could not complete AI review.",
        }


def get_chat_response(user_message: str, code_context: str = "") -> str:
    """
    Interactive AI assistant — answers questions about the code.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "⚠️ GROQ_API_KEY not set. Please add it to your .env file."

    try:
        llm = ChatGroq(
            groq_api_key=api_key,
            model_name="llama-3.1-8b-instant",
            temperature=0.5,
        )

        system = "You are a helpful Python code assistant. Be concise and clear."
        context = f"\nCode context:\n```python\n{code_context}\n```\n" if code_context else ""
        full_message = f"{context}\nUser: {user_message}"

        messages = [
            SystemMessage(content=system),
            HumanMessage(content=full_message),
        ]

        response = llm.invoke(messages)
        return response.content.strip()

    except Exception as e:
        return f"Error: {str(e)}"
