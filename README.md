import streamlit as st
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
import re

# Load environment variables and set OpenAI API key
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')

# Define the TicketState class
class TicketState(TypedDict):
    """Represents the state of the support ticket evaluation process."""
    response: str
    clarity_score: float
    politeness_score: float
    professionalism_score: float
    resolution_score: float
    effectiveness_score: float
    feedback: str

# Initialize the ChatOpenAI model
@st.cache_resource
def get_llm():
    return ChatOpenAI(model="gpt-4o-mini")

# Define evaluation functions
def parse_rating(content: str) -> float:
    """Extract the numeric rating from the LLM's response."""
    match = re.search(r'Rating:\s*(\d+(\.\d+)?)', content)
    if match:
        return float(match.group(1))
    raise ValueError(f"Could not extract rating from: {content}")

def evaluate_clarity(state: TicketState) -> TicketState:
    """Evaluate the clarity of the support response."""
    prompt = ChatPromptTemplate.from_template(
        "Analyze the clarity of the following customer support response. "
        "Is it easy to understand? Does it avoid jargon? Is it concise yet complete? "
        "Provide a clarity rating between 0 and 1. "
        "Your response should start with 'Rating: ' followed by the numeric score, "
        "then provide your explanation.\n\nResponse: {response}"
    )
    result = get_llm().invoke(prompt.format(response=state["response"]))
    try:
        state["clarity_score"] = parse_rating(result.content)
    except ValueError as e:
        st.error(f"Error in evaluate_clarity: {e}")
        state["clarity_score"] = 0.0
    return state

def assess_politeness(state: TicketState) -> TicketState:
    """Assess the politeness of the support response."""
    prompt = ChatPromptTemplate.from_template(
        "Analyze the politeness and tone in the following customer support response. "
        "Is it respectful? Does it use appropriate greetings and closings? "
        "Does it show empathy for the customer's issue? "
        "Provide a politeness rating between 0 and 1. "
        "Your response should start with 'Rating: ' followed by the numeric score, "
        "then provide your explanation.\n\nResponse: {response}"
    )
    result = get_llm().invoke(prompt.format(response=state["response"]))
    try:
        state["politeness_score"] = parse_rating(result.content)
    except ValueError as e:
        st.error(f"Error in assess_politeness: {e}")
        state["politeness_score"] = 0.0
    return state

def examine_professionalism(state: TicketState) -> TicketState:
    """Examine the professionalism of the support response."""
    prompt = ChatPromptTemplate.from_template(
        "Analyze the professionalism of the following customer support response. "
        "Does it maintain a professional tone? Is it free of slang or inappropriate language? "
        "Does it represent the company well? "
        "Provide a professionalism rating between 0 and 1. "
        "Your response should start with 'Rating: ' followed by the numeric score, "
        "then provide your explanation.\n\nResponse: {response}"
    )
    result = get_llm().invoke(prompt.format(response=state["response"]))
    try:
        state["professionalism_score"] = parse_rating(result.content)
    except ValueError as e:
        st.error(f"Error in examine_professionalism: {e}")
        state["professionalism_score"] = 0.0
    return state

def verify_resolution(state: TicketState) -> TicketState:
    """Verify if the response effectively resolves the customer's issue."""
    prompt = ChatPromptTemplate.from_template(
        "Evaluate how effectively the following customer support response resolves the issue. "
        "Does it address all parts of the customer's problem? "
        "Does it provide clear next steps or solutions? "
        "Provide a resolution rating between 0 and 1. "
        "Your response should start with 'Rating: ' followed by the numeric score, "
        "then provide your explanation.\n\nResponse: {response}"
    )
    result = get_llm().invoke(prompt.format(response=state["response"]))
    try:
        state["resolution_score"] = parse_rating(result.content)
    except ValueError as e:
        st.error(f"Error in verify_resolution: {e}")
        state["resolution_score"] = 0.0
    return state

def compute_effectiveness(state: TicketState) -> TicketState:
    """Calculate the overall effectiveness score based on individual component scores."""
    state["effectiveness_score"] = (
        state["clarity_score"] * 0.25 +
        state["politeness_score"] * 0.15 +
        state["professionalism_score"] * 0.15 +
        state["resolution_score"] * 0.45
    )
    return state

def generate_feedback(state: TicketState) -> TicketState:
    """Generate actionable feedback for the support agent."""
    prompt = ChatPromptTemplate.from_template(
        "Based on the following scores for a customer support response, "
        "provide specific, actionable feedback for improvement. "
        "Clarity: {clarity_score:.2f}, "
        "Politeness: {politeness_score:.2f}, "
        "Professionalism: {professionalism_score:.2f}, "
        "Resolution: {resolution_score:.2f}, "
        "Overall Effectiveness: {effectiveness_score:.2f}. "
        "Focus on 2-3 key areas for improvement and provide examples where possible. "
        "If scores are high, highlight strengths to maintain.\n\n"
        "The response being evaluated: {response}"
    )
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

# Create the workflow graph
@st.cache_resource
def create_workflow():
    workflow = StateGraph(TicketState)

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
        lambda x: "assess_politeness" if x["clarity_score"] > 0.4 else "compute_effectiveness"
    )
    workflow.add_conditional_edges(
        "assess_politeness",
        lambda x: "examine_professionalism" if x["politeness_score"] > 0.5 else "compute_effectiveness"
    )
    workflow.add_conditional_edges(
        "examine_professionalism",
        lambda x: "verify_resolution" if x["professionalism_score"] > 0.5 else "compute_effectiveness"
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

# Evaluate function
def evaluate_ticket(response: str):
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
    return app.invoke(initial_state)

# Sample response
sample_response = """
Dear valued customer,

Thank you for contacting our support team about the issue with your account login.

I've investigated the matter and found that your account was temporarily locked due to 
multiple failed login attempts. This is a security measure we have in place to protect 
your account from unauthorized access.

I've reset your account security status, and you should now be able to log in without any issues. 
For security purposes, I recommend updating your password after logging in. You can do this
by navigating to "Account Settings" > "Security" > "Change Password".

If you continue to experience login problems or have any other questions, 
please don't hesitate to reply to this ticket or contact us at support@example.com.

Best regards,
John Smith
Customer Support Team
"""

# Streamlit UI
st.set_page_config(
    page_title="Support Response Evaluator",
    page_icon="📝",
    layout="wide"
)

st.title("Customer Support Response Evaluator")
st.markdown("This tool evaluates customer support responses based on clarity, politeness, professionalism, and issue resolution.")

# Input for ticket ID and response
with st.form("support_form"):
    ticket_id = st.text_input("Ticket ID", placeholder="e.g., TICKET-12345")
    
    # Option to use sample response or enter custom response
    use_sample = st.checkbox("Use sample response", value=True)
    
    if use_sample:
        response_text = st.text_area("Response Content", value=sample_response, height=300)
    else:
        response_text = st.text_area("Response Content", height=300, 
                                      placeholder="Enter the customer support response here...")
    
    # Add customer query info (optional)
    with st.expander("Customer Query (Optional)"):
        customer_query = st.text_area("Original Customer Query", 
                                     placeholder="Enter the original customer query for additional context...")
    
    # Submit button
    submit_button = st.form_submit_button("Evaluate Response")

# Process the evaluation when submit button is clicked
if submit_button and response_text:
    with st.spinner("Evaluating response..."):
        # Create progress bar
        progress_bar = st.progress(0)
        
        # Evaluate the response
        result = evaluate_ticket(response_text)
        
        # Update progress
        progress_bar.progress(100)
    
    # Display the results
    st.success("Evaluation complete!")
    
    # Create two columns for the results
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("Feedback")
        st.markdown(result["feedback"])
    
    with col2:
        st.subheader("Scores")
        
        # Display overall effectiveness with gauge meter
        st.markdown("### Overall Effectiveness")
        st.progress(result["effectiveness_score"])
        st.markdown(f"**Score: {result['effectiveness_score']:.2f}**")
        
        st.markdown("### Individual Metrics")
        
        # Clarity
        score_color = "green" if result["clarity_score"] >= 0.8 else "orange" if result["clarity_score"] >= 0.6 else "red"
        st.markdown(f"**Clarity: <span style='color:{score_color}'>{result['clarity_score']:.2f}</span>**", unsafe_allow_html=True)
        st.progress(result["clarity_score"])
        
        # Politeness
        score_color = "green" if result["politeness_score"] >= 0.8 else "orange" if result["politeness_score"] >= 0.6 else "red"
        st.markdown(f"**Politeness: <span style='color:{score_color}'>{result['politeness_score']:.2f}</span>**", unsafe_allow_html=True)
        st.progress(result["politeness_score"])
        
        # Professionalism
        score_color = "green" if result["professionalism_score"] >= 0.8 else "orange" if result["professionalism_score"] >= 0.6 else "red"
        st.markdown(f"**Professionalism: <span style='color:{score_color}'>{result['professionalism_score']:.2f}</span>**", unsafe_allow_html=True)
        st.progress(result["professionalism_score"])
        
        # Resolution
        score_color = "green" if result["resolution_score"] >= 0.8 else "orange" if result["resolution_score"] >= 0.6 else "red"
        st.markdown(f"**Resolution: <span style='color:{score_color}'>{result['resolution_score']:.2f}</span>**", unsafe_allow_html=True)
        st.progress(result["resolution_score"])
    
    # Provide a downloadable report
    st.download_button(
        label="Download Report",
        data=f"""# Support Response Evaluation Report

## Ticket: {ticket_id}

### Scores
- Overall Effectiveness: {result['effectiveness_score']:.2f}
- Clarity: {result['clarity_score']:.2f}
- Politeness: {result['politeness_score']:.2f}
- Professionalism: {result['professionalism_score']:.2f}
- Resolution: {result['resolution_score']:.2f}

### Feedback
{result['feedback']}

### Response Evaluated
```
{response_text}
```
""",
        file_name=f"evaluation_report_{ticket_id}.md",
        mime="text/markdown",
    )

# Footer with information
st.markdown("---")
st.markdown("Built with Streamlit, LangGraph, and LangChain")