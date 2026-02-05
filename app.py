import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from streamlit_pdf_viewer import pdf_viewer
import io

# --- 1. APP CONFIGURATION ---
st.set_page_config(layout="wide", page_title="SmartScan AI Pro", page_icon="📄")

# --- 2. THEME & UI ---
with st.sidebar:
    st.title("SmartScan Pro")
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=70)
    st.divider()
    night_mode = st.toggle("🌙 Night Mode", value=True)
    summary_size = st.select_slider("Summary Detail", options=["Brief", "Medium", "Detailed"])
    st.info("Created By Tayeeb Ansari , Powered by Gemini 3.0 - flash")

# Apply Theme
bg, text, card = ("#0E1117", "#E0E0E0", "#1d1e24") if night_mode else ("#F0F2F6", "#31333F", "#FFFFFF")
st.markdown(f"<style>.stApp {{ background-color: {bg}; color: {text}; }}</style>", unsafe_allow_html=True)

# --- 3. SECURE API SETUP ---
# Tomorrow, you will add "GEMINI_API_KEY" to your Streamlit Secrets dashboard
try:
    MY_API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    # Fallback for local testing before you set up secrets
    MY_API_KEY = "AIzaSyD12H7hndOcb0Wc--Z4g_-MNysXgRbDru8"

genai.configure(api_key=MY_API_KEY)

# --- 4. CORE FUNCTIONS ---
def extract_text(pdf_file):
    reader = PdfReader(pdf_file)
    return "".join([page.extract_text() or "" for page in reader.pages])

def create_styled_pdf(text_content):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = [Paragraph("SmartScan AI - Edited Export", styles['Heading1']), Spacer(1, 12)]
    for line in text_content.split('\n'):
        elements.append(Paragraph(line, styles['Normal']) if line.strip() else Spacer(1, 10))
    doc.build(elements)
    return buffer.getvalue()

# --- 5. MAIN INTERFACE ---
st.title("📄 SmartScan AI Hub")
uploaded_file = st.file_uploader("Upload PDF", type="pdf")

if uploaded_file:
    if "edited_text" not in st.session_state:
        st.session_state.edited_text = extract_text(uploaded_file)
    if "ai_summary" not in st.session_state:
        st.session_state.ai_summary = ""

    # --- THE TABBED SYSTEM ---
    tab_editor, tab_ai, tab_export = st.tabs(["🔍 Workspace", "🤖 AI Analysis", "📥 Export"])

    with tab_editor:
        col_pdf, col_edit = st.columns([1, 1], gap="large")
        with col_pdf:
            st.subheader("🖼️ Original PDF")
            pdf_viewer(uploaded_file.getvalue(), height=700)
            
        with col_edit:
            st.subheader("✍️ Live Editor")
            st.session_state.edited_text = st.text_area(
                "Modify text below:", 
                value=st.session_state.edited_text, 
                height=600,
                key="workspace_editor"
            )

    with tab_ai:
        st.subheader("🤖 Artificial Intelligence Insights")
        st.write("Click the button below to analyze your edited text.")
        
        # --- THE BUTTON IS NOW HERE ---
        if st.button("✨ Prepare AI Summary", type="primary"):
            with st.spinner("Gemini is reading your edits..."):
                try:
                    model = genai.GenerativeModel("gemini-1.5- flash")
                    prompt = f"Summarize these edits in {summary_size} detail: {st.session_state.edited_text[:4000]}"
                    response = model.generate_content(prompt)
                    st.session_state.ai_summary = response.text
                except Exception as e:
                    st.error(f"Error: {e}")

        # Display results
        if st.session_state.ai_summary:
            st.divider()
            st.markdown(st.session_state.ai_summary)
        else:
            st.info("Your summary will appear here after clicking the button above.")

    with tab_export:
        st.subheader("Ready to save?")
        st.write("This will create a new PDF with all your changes.")
        edited_pdf = create_styled_pdf(st.session_state.edited_text)
        st.download_button("📥 Download Edited PDF", edited_pdf, "Edited_Doc.pdf", "application/pdf")

else:
    st.info("Upload a PDF to start.")