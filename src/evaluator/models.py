"""
Data models for the Customer Support Response Evaluator.
"""

from typing import TypedDict, Optional


class TicketState(TypedDict):
    """Represents the state of the support ticket evaluation process."""
    response: str
    clarity_score: float
    politeness_score: float
    professionalism_score: float
    resolution_score: float
    effectiveness_score: float
    feedback: str


class EvaluationResult(TypedDict):
    """Represents the complete evaluation result including additional metadata."""
    ticket_id: Optional[str]
    response: str
    clarity_score: float
    politeness_score: float
    professionalism_score: float
    resolution_score: float
    effectiveness_score: float
    feedback: str
    timestamp: str