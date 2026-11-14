"""ARES Health AI — pre-hackathon placeholder, NOT a health monitoring tool.

Replace this screen with your original, attributed hackathon implementation
when the event begins. No health metrics are processed here.
"""
import streamlit as st

st.set_page_config(page_title="ARES Health AI | Planning", page_icon="🛰️", layout="wide")
st.title("ARES Health AI")
st.caption("Astronaut Risk Evaluation System · NASA Space Apps 2026 · Universal Event")
st.info("Preparation scaffold only. No monitoring, AI model, or medical advice is active.")
st.markdown("""
### Planned challenge response
A local-first, explainable prototype to visualize simulated health data,
identify changes worth reviewing, and link to appropriate protocols.

**Planned modules**
- Data import and quality checks
- Trends and astronaut-specific reference patterns
- Explainable alert review
- Scenario-based validation and export

**Not a medical device.** Do not enter personal health information into this demo.
""")
