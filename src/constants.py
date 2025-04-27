"""
Constants for the Customer Support Response Evaluator.
"""

# Application paths
CONFIG_DIR = "config"
SETTINGS_PATH = f"{CONFIG_DIR}/settings.yaml"
CONFIG_PATH = f"{CONFIG_DIR}/config.json"

# Regular expressions
RATING_PATTERN = r'Rating:\s*(\d+(\.\d+)?)'

# UI labels
APP_TITLE = "Customer Support Response Evaluator"
FORM_TICKET_ID_LABEL = "Ticket ID"
FORM_TICKET_ID_PLACEHOLDER = "e.g., TICKET-12345"
FORM_RESPONSE_LABEL = "Response Content"
FORM_RESPONSE_PLACEHOLDER = "Enter the customer support response here..."
FORM_CUSTOMER_QUERY_LABEL = "Original Customer Query"
FORM_CUSTOMER_QUERY_PLACEHOLDER = "Enter the original customer query for additional context..."
FORM_SAMPLE_RESPONSE_LABEL = "Use sample response"
FORM_SUBMIT_LABEL = "Evaluate Response"
FORM_DOWNLOAD_LABEL = "Download Report"

# UI section titles
SECTION_FEEDBACK_TITLE = "Feedback"
SECTION_SCORES_TITLE = "Scores"
SECTION_EFFECTIVENESS_TITLE = "Overall Effectiveness"
SECTION_METRICS_TITLE = "Individual Metrics"

# Metric names
METRIC_EFFECTIVENESS = "effectiveness_score"
METRIC_CLARITY = "clarity_score"
METRIC_POLITENESS = "politeness_score"
METRIC_PROFESSIONALISM = "professionalism_score"
METRIC_RESOLUTION = "resolution_score"

# Friendly names for metrics
METRIC_FRIENDLY_NAMES = {
    METRIC_CLARITY: "Clarity",
    METRIC_POLITENESS: "Politeness",
    METRIC_PROFESSIONALISM: "Professionalism",
    METRIC_RESOLUTION: "Resolution",
    METRIC_EFFECTIVENESS: "Overall Effectiveness"
}

# Error messages
ERROR_NO_API_KEY = "No OpenAI API key found. Please set your OPENAI_API_KEY in the .env file."
ERROR_EVALUATION = "An error occurred during evaluation: {}"
ERROR_EXTRACT_RATING = "Could not extract rating from: {}"

# Success messages
SUCCESS_EVALUATION = "Evaluation complete!"

# Report template
REPORT_TEMPLATE = """# Support Response Evaluation Report

## Ticket: {ticket_id}

### Scores
- Overall Effectiveness: {effectiveness_score:.2f}
- Clarity: {clarity_score:.2f}
- Politeness: {politeness_score:.2f}
- Professionalism: {professionalism_score:.2f}
- Resolution: {resolution_score:.2f}

### Feedback
{feedback}

### Response Evaluated
```
{response_text}
```
"""

# Footer content
FOOTER_CONTENT = "Built with Streamlit, LangGraph, and LangChain"