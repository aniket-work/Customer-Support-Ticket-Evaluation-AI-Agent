"""
Customer Support Response Evaluator - Main Application Entry Point

This application evaluates customer support responses using LangGraph and LLM technology
to provide actionable feedback for support agents.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ensure OpenAI API key is set
if not os.getenv('OPENAI_API_KEY'):
    print("ERROR: No OpenAI API key found. Please set OPENAI_API_KEY in your .env file.")
    exit(1)

# Import after environment setup
from src.ui.app import run_app


if __name__ == "__main__":
    run_app()