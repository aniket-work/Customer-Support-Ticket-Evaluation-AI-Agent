"""
Utility functions for the Customer Support Response Evaluator.
"""

import os
import re
import json
import yaml
import datetime
from typing import Dict, Any

import streamlit as st

from src.constants import RATING_PATTERN, CONFIG_PATH, SETTINGS_PATH, ERROR_EXTRACT_RATING


def parse_rating(content: str) -> float:
    """
    Extract the numeric rating from the LLM's response.

    Args:
        content: The response content from the LLM

    Returns:
        float: The extracted rating value

    Raises:
        ValueError: If no rating can be found in the content
    """
    match = re.search(RATING_PATTERN, content)
    if match:
        return float(match.group(1))
    raise ValueError(ERROR_EXTRACT_RATING.format(content))


def load_config() -> Dict[str, Any]:
    """
    Load the application configuration from the config file.

    Returns:
        Dict[str, Any]: The configuration dictionary
    """
    with open(CONFIG_PATH, 'r') as config_file:
        return json.load(config_file)


def load_settings() -> Dict[str, Any]:
    """
    Load the application settings from the settings file.

    Returns:
        Dict[str, Any]: The settings dictionary
    """
    with open(SETTINGS_PATH, 'r') as settings_file:
        return yaml.safe_load(settings_file)


def get_score_color(score: float, settings: Dict[str, Any]) -> str:
    """
    Get the color for a score based on thresholds.

    Args:
        score: The score value
        settings: The application settings

    Returns:
        str: The color name ('green', 'orange', or 'red')
    """
    thresholds = settings['evaluation']['thresholds']['color']
    if score >= thresholds['good']:
        return "green"
    elif score >= thresholds['average']:
        return "orange"
    else:
        return "red"


def generate_report(result: Dict[str, Any], ticket_id: str, response_text: str) -> str:
    """
    Generate a markdown report from the evaluation results.

    Args:
        result: The evaluation result dictionary
        ticket_id: The ID of the ticket being evaluated
        response_text: The original response text

    Returns:
        str: The markdown report content
    """
    from src.constants import REPORT_TEMPLATE

    return REPORT_TEMPLATE.format(
        ticket_id=ticket_id,
        effectiveness_score=result['effectiveness_score'],
        clarity_score=result['clarity_score'],
        politeness_score=result['politeness_score'],
        professionalism_score=result['professionalism_score'],
        resolution_score=result['resolution_score'],
        feedback=result['feedback'],
        response_text=response_text
    )


def get_timestamp() -> str:
    """
    Get the current timestamp in a formatted string.

    Returns:
        str: Formatted timestamp
    """
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")