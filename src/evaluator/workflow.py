"""
Workflow definition for the customer support evaluation process.
"""

import streamlit as st
from langgraph.graph import StateGraph, END

from src.evaluator.models import TicketState
from src.evaluator.evaluator import (
    evaluate_clarity,
    assess_politeness,
    examine_professionalism,
    verify_resolution,
    compute_effectiveness,
    generate_feedback
)
from src.utils.helpers import load_settings
from src.constants import (
    ERROR_EVALUATION,
    SUCCESS_EVALUATION,
    METRIC_CLARITY,
    METRIC_POLITENESS,
    METRIC_PROFESSIONALISM,
    METRIC_RESOLUTION,
    METRIC_EFFECTIVENESS
)


def create_workflow() -> StateGraph:
    """
    Create the LangGraph workflow for ticket evaluation.

    Returns:
        StateGraph: Compiled workflow graph
    """
    workflow = StateGraph(TicketState)
    settings = load_settings()
    thresholds = settings['evaluation']['thresholds']

    # Add nodes to the graph
    workflow.add_node("evaluate_clarity", evaluate_clarity)
    workflow.add_node("assess_politeness", assess_politeness)
    workflow.add_node("examine_professionalism", examine_professionalism)
    workflow.add_node("verify_resolution", verify_resolution)
    workflow.add_node("compute_effectiveness", compute_effectiveness)
    workflow.add_node("generate_feedback", generate_feedback)

    # Define and add conditional edges
    workflow.add_conditional_edges(
        "evaluate_clarity",
        lambda x: "assess_politeness"
        if x[METRIC_CLARITY] > thresholds['clarity']
        else "compute_effectiveness"
    )
    workflow.add_conditional_edges(
        "assess_politeness",
        lambda x: "examine_professionalism"
        if x[METRIC_POLITENESS] > thresholds['politeness']
        else "compute_effectiveness"
    )
    workflow.add_conditional_edges(
        "examine_professionalism",
        lambda x: "verify_resolution"
        if x[METRIC_PROFESSIONALISM] > thresholds['professionalism']
        else "compute_effectiveness"
    )
    workflow.add_conditional_edges(
        "verify_resolution",
        lambda x: "compute_effectiveness"
    )
    workflow.add_conditional_edges(
        "compute_effectiveness",
        lambda x: "generate_feedback"
    )

    # Set the entry point
    workflow.set_entry_point("evaluate_clarity")

    # Set the exit point
    workflow.add_edge("generate_feedback", END)

    # Compile the graph
    return workflow.compile()


def evaluate_ticket(response: str):
    """
    Evaluate a customer support response using the workflow.

    Args:
        response: The support response to evaluate

    Returns:
        dict: The evaluation result or None if an error occurred
    """
    app = create_workflow()
    initial_state = TicketState(
        response=response,
        clarity_score=0.0,
        politeness_score=0.0,
        professionalism_score=0.0,
        resolution_score=0.0,
        effectiveness_score=0.0,
        feedback=""
    )

    with st.spinner("Evaluating response..."):
        # Create progress bar
        progress_bar = st.progress(0)

        try:
            # Evaluate the response
            result = app.invoke(initial_state)

            # Log results for debugging
            print(f"Final Effectiveness Score: {result[METRIC_EFFECTIVENESS]:.2f}")
            print(f"Clarity Score: {result[METRIC_CLARITY]:.2f}")
            print(f"Politeness Score: {result[METRIC_POLITENESS]:.2f}")
            print(f"Professionalism Score: {result[METRIC_PROFESSIONALISM]:.2f}")
            print(f"Resolution Score: {result[METRIC_RESOLUTION]:.2f}")
            print(f"Feedback:\n{result['feedback']}")

            # Update progress
            progress_bar.progress(100)
            st.success(SUCCESS_EVALUATION)
            return result
        except Exception as e:
            st.error(ERROR_EVALUATION.format(str(e)))
            return None