"""
Core evaluation functions for the Customer Support Response Evaluator.
"""

import os
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from src.evaluator.models import TicketState
from src.utils.helpers import parse_rating, load_config, load_settings
from src.constants import ERROR_NO_API_KEY


def get_llm() -> ChatOpenAI:
    """
    Initialize the LLM with appropriate settings.

    Returns:
        ChatOpenAI: Configured LLM instance

    Raises:
        SystemExit: If no API key is found
    """
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        st.error(ERROR_NO_API_KEY)
        st.stop()

    settings = load_settings()
    llm_settings = settings['llm']

    return ChatOpenAI(
        model=llm_settings['model'],
        temperature=llm_settings['temperature'],
        request_timeout=llm_settings['timeout'],
        api_key=api_key
    )


def evaluate_clarity(state: TicketState) -> TicketState:
    """
    Evaluate the clarity of the support response.

    Args:
        state: The current evaluation state

    Returns:
        TicketState: Updated state with clarity score
    """
    config = load_config()
    prompt = ChatPromptTemplate.from_template(config['prompts']['clarity']['template'])

    result = get_llm().invoke(prompt.format(response=state["response"]))
    try:
        state["clarity_score"] = parse_rating(result.content)
    except ValueError as e:
        st.error(f"Error in evaluate_clarity: {e}")
        state["clarity_score"] = 0.0
    return state


def assess_politeness(state: TicketState) -> TicketState:
    """
    Assess the politeness of the support response.

    Args:
        state: The current evaluation state

    Returns:
        TicketState: Updated state with politeness score
    """
    config = load_config()
    prompt = ChatPromptTemplate.from_template(config['prompts']['politeness']['template'])

    result = get_llm().invoke(prompt.format(response=state["response"]))
    try:
        state["politeness_score"] = parse_rating(result.content)
    except ValueError as e:
        st.error(f"Error in assess_politeness: {e}")
        state["politeness_score"] = 0.0
    return state


def examine_professionalism(state: TicketState) -> TicketState:
    """
    Examine the professionalism of the support response.

    Args:
        state: The current evaluation state

    Returns:
        TicketState: Updated state with professionalism score
    """
    config = load_config()
    prompt = ChatPromptTemplate.from_template(config['prompts']['professionalism']['template'])

    result = get_llm().invoke(prompt.format(response=state["response"]))
    try:
        state["professionalism_score"] = parse_rating(result.content)
    except ValueError as e:
        st.error(f"Error in examine_professionalism: {e}")
        state["professionalism_score"] = 0.0
    return state


def verify_resolution(state: TicketState) -> TicketState:
    """
    Verify if the response effectively resolves the customer's issue.

    Args:
        state: The current evaluation state

    Returns:
        TicketState: Updated state with resolution score
    """
    config = load_config()
    prompt = ChatPromptTemplate.from_template(config['prompts']['resolution']['template'])

    result = get_llm().invoke(prompt.format(response=state["response"]))
    try:
        state["resolution_score"] = parse_rating(result.content)
    except ValueError as e:
        st.error(f"Error in verify_resolution: {e}")
        state["resolution_score"] = 0.0
    return state


def compute_effectiveness(state: TicketState) -> TicketState:
    """
    Calculate the overall effectiveness score based on individual component scores.

    Args:
        state: The current evaluation state

    Returns:
        TicketState: Updated state with effectiveness score
    """
    settings = load_settings()
    weights = settings['evaluation']['weights']

    state["effectiveness_score"] = (
            state["clarity_score"] * weights['clarity'] +
            state["politeness_score"] * weights['politeness'] +
            state["professionalism_score"] * weights['professionalism'] +
            state["resolution_score"] * weights['resolution']
    )
    return state


def generate_feedback(state: TicketState) -> TicketState:
    """
    Generate actionable feedback for the support agent.

    Args:
        state: The current evaluation state

    Returns:
        TicketState: Updated state with feedback
    """
    config = load_config()
    prompt = ChatPromptTemplate.from_template(config['prompts']['feedback']['template'])

    result = get_llm().invoke(prompt.format(
        clarity_score=state["clarity_score"],
        politeness_score=state["politeness_score"],
        professionalism_score=state["professionalism_score"],
        resolution_score=state["resolution_score"],
        effectiveness_score=state["effectiveness_score"],
        response=state["response"]
    ))
    state["feedback"] = result.content
    return state