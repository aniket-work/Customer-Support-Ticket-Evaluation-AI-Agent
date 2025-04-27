"""
Streamlit UI implementation for the Customer Support Response Evaluator.
"""

import streamlit as st

from src.evaluator.workflow import evaluate_ticket
from src.utils.helpers import load_config, load_settings, get_score_color, generate_report, get_timestamp
from src.constants import (
    FORM_TICKET_ID_LABEL,
    FORM_TICKET_ID_PLACEHOLDER,
    FORM_RESPONSE_LABEL,
    FORM_RESPONSE_PLACEHOLDER,
    FORM_CUSTOMER_QUERY_LABEL,
    FORM_CUSTOMER_QUERY_PLACEHOLDER,
    FORM_SAMPLE_RESPONSE_LABEL,
    FORM_SUBMIT_LABEL,
    FORM_DOWNLOAD_LABEL,
    SECTION_FEEDBACK_TITLE,
    SECTION_SCORES_TITLE,
    SECTION_EFFECTIVENESS_TITLE,
    SECTION_METRICS_TITLE,
    METRIC_FRIENDLY_NAMES,
    FOOTER_CONTENT,
    METRIC_CLARITY,
    METRIC_POLITENESS,
    METRIC_PROFESSIONALISM,
    METRIC_RESOLUTION,
    METRIC_EFFECTIVENESS
)


def setup_page():
    """Configure the Streamlit page settings."""
    settings = load_settings()
    app_settings = settings['app']

    st.set_page_config(
        page_title=app_settings['title'],
        page_icon=app_settings['icon'],
        layout=app_settings['layout']
    )

    st.title(app_settings['title'])
    st.markdown(app_settings['description'])


def initialize_session_state():
    """Initialize the session state variables."""
    if 'evaluated' not in st.session_state:
        st.session_state.evaluated = False
    if 'result' not in st.session_state:
        st.session_state.result = None
    if 'ticket_id' not in st.session_state:
        st.session_state.ticket_id = ""
    if 'response_text' not in st.session_state:
        st.session_state.response_text = ""


def render_input_form():
    """Render the input form for ticket evaluation."""
    config = load_config()

    with st.form("support_form"):
        ticket_id = st.text_input(
            FORM_TICKET_ID_LABEL,
            placeholder=FORM_TICKET_ID_PLACEHOLDER
        )

        # Option to use sample response or enter custom response
        use_sample = st.checkbox(FORM_SAMPLE_RESPONSE_LABEL, value=True)

        if use_sample:
            response_text = st.text_area(
                FORM_RESPONSE_LABEL,
                value=config['sample_response'],
                height=300
            )
        else:
            response_text = st.text_area(
                FORM_RESPONSE_LABEL,
                height=300,
                placeholder=FORM_RESPONSE_PLACEHOLDER
            )

        # Add customer query info (optional)
        with st.expander("Customer Query (Optional)"):
            customer_query = st.text_area(
                FORM_CUSTOMER_QUERY_LABEL,
                placeholder=FORM_CUSTOMER_QUERY_PLACEHOLDER
            )

        # Submit button
        submit_button = st.form_submit_button(FORM_SUBMIT_LABEL)

    return submit_button, ticket_id, response_text


def display_results(result, ticket_id, response_text):
    """Display the evaluation results in the UI."""
    settings = load_settings()

    # Create two columns for the results
    col1, col2 = st.columns([3, 2])

    with col1:
        st.subheader(SECTION_FEEDBACK_TITLE)
        st.markdown(result["feedback"])

    with col2:
        st.subheader(SECTION_SCORES_TITLE)

        # Display overall effectiveness with gauge meter
        st.markdown(f"### {SECTION_EFFECTIVENESS_TITLE}")
        st.progress(result[METRIC_EFFECTIVENESS])
        st.markdown(f"**Score: {result[METRIC_EFFECTIVENESS]:.2f}**")

        st.markdown(f"### {SECTION_METRICS_TITLE}")

        # Display individual metrics
        metrics = [METRIC_CLARITY, METRIC_POLITENESS, METRIC_PROFESSIONALISM, METRIC_RESOLUTION]

        for metric in metrics:
            score = result[metric]
            friendly_name = METRIC_FRIENDLY_NAMES[metric]
            score_color = get_score_color(score, settings)

            st.markdown(
                f"**{friendly_name}: <span style='color:{score_color}'>{score:.2f}</span>**",
                unsafe_allow_html=True
            )
            st.progress(score)

    # Provide a downloadable report
    st.download_button(
        label=FORM_DOWNLOAD_LABEL,
        data=generate_report(result, ticket_id, response_text),
        file_name=f"evaluation_report_{ticket_id}_{get_timestamp().replace(':', '-').replace(' ', '_')}.md",
        mime="text/markdown",
    )


def render_footer():
    """Render the application footer."""
    st.markdown("---")
    st.markdown(FOOTER_CONTENT)


def run_app():
    """Main application logic."""
    setup_page()
    initialize_session_state()

    # Input form for ticket ID and response
    submit_button, ticket_id, response_text = render_input_form()

    # Process the evaluation when submit button is clicked
    if submit_button and response_text:
        result = evaluate_ticket(response_text)
        if result:
            st.session_state.result = result
            st.session_state.ticket_id = ticket_id
            st.session_state.response_text = response_text
            st.session_state.evaluated = True

    # Display results if evaluation has been performed
    if st.session_state.evaluated and st.session_state.result:
        display_results(
            st.session_state.result,
            st.session_state.ticket_id,
            st.session_state.response_text
        )

    render_footer()