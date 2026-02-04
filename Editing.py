import streamlit as st 
from google import genai  # UPDATED LIBRARY
from PyPDF2 import PdfReader 
from reportlab.pdfgen import canvas 
from streamlit_pdf_viewer import pdf_viewer 
import io 
import time 

# --- 1. APP CONFIGURATION ---
st.set_page_config(layout="wide", page_title="SmartScan AI Pro", page_icon="📄")

# --- 2. SIDEBAR ---
with st.sidebar:
    st.title("Project Controls")
    night_mode = st.toggle("🌙 Enable Dark Mode")
    summary_size = st.select_slider("Summary Detail", options=["Brief", "Medium", "Detailed"])

# --- 3. THEME ---
bg, text = ("#0E1117", "#FFFFFF") if night_mode else ("#FFFFFF", "#31333F")
st.markdown(f"<style>.stApp {{ background-color: {bg}; color: {text}; }}</style>", unsafe_allow_html=True)

# --- 4. AI SETUP (NEW SYNTAX) ---
# Replace with your actual key or use st.secrets
client = genai.Client(api_key="AIzaSyC...") 

# --- 5. MAIN UI ---
st.title("📄 SmartScan AI Pro")
uploaded_file = st.file_uploader("Drop your PDF here", type="pdf")

if uploaded_file:
    # Extraction
    reader = PdfReader(uploaded_file)
    raw_text = "".join([page.extract_text() or "" for page in reader.pages])
    
    tab1, tab2 = st.tabs(["🔍 Workspace", "🤖 AI Analytics"])
    
    with tab1:
        col_l, col_r = st.columns(2)
        with col_l:
            pdf_viewer(uploaded_file.getvalue(), height=500)
        with col_r:
            edited_text = st.text_area("Edit Content:", value=raw_text, height=400)

    with tab2:
        if st.button("✨ Generate AI Insights"):
            with st.spinner("Gemini is analyzing..."):
                try:
                    # UPDATED CALL FOR GOOGLE-GENAI
                    response = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=f"Summarize this in a {summary_size} format: {edited_text[:5000]}"
                    )
                    st.success("✅ Done!")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"AI Error: {e}")