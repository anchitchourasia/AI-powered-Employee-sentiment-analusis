import os
import streamlit as st
import json
import re
from dotenv import load_dotenv
import google.generativeai as genai

# Load API key from .env file
load_dotenv()
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Helper function to clean and parse JSON from model response
def clean_and_parse_json(text):
    try:
        # Find the first '{' and last '}' to extract JSON substring
        start = text.index('{')
        end = text.rindex('}') + 1
        json_str = text[start:end]
        return json.loads(json_str)
    except (ValueError, json.JSONDecodeError):
        return None


# Function to call Gemini API with prompt to analyze employee feedback
def analyze_employee_feedback(feedback_text):
    prompt = f"""
You are an HR analyst AI assistant.

Analyze the following employee feedback and provide a JSON response with these fields:

1. attrition_risk: one of [no, low, medium, high]
2. explanation: brief explanation for the risk level
3. engagement_strategies: a list of 3 practical strategies to improve employee engagement and reduce attrition risk

Employee Feedback:
\"\"\"{feedback_text}\"\"\"

Respond ONLY in JSON format.
"""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"API call error: {e}"

# Streamlit UI
st.title("📝 Employee Sentiment and Attrition Risk Analysis")
st.write("Enter free-text employee feedback to analyze attrition risk and get engagement strategy suggestions.")

feedback = st.text_area("Enter Employee Feedback", height=200)

if st.button("Analyze") and feedback.strip():
    with st.spinner("Analyzing feedback..."):
        result = analyze_employee_feedback(feedback)
    
    st.subheader("Analysis Result (Raw Output)")
    st.code(result, language="json")

    parsed = clean_and_parse_json(result)
    if parsed:
        st.subheader("Parsed Result")
        st.markdown(f"**Attrition Risk:** {parsed.get('attrition_risk', 'N/A').title()}")
        st.markdown(f"**Explanation:** {parsed.get('explanation', 'N/A')}")
        st.markdown("**Engagement Strategies:**")
        strategies = parsed.get('engagement_strategies', [])
        for i, strat in enumerate(strategies, 1):
            st.markdown(f"{i}. {strat}")
    else:
        st.error("Failed to parse JSON from the model response. Showing raw output above.")
else:
    st.info("Please enter employee feedback and click Analyze.")
