import streamlit as st
import os
from dotenv import load_dotenv
from pypdf import PdfReader
import google.generativeai as genai
import json

# --------------------------
# Suppress gRPC warnings
# --------------------------
os.environ["GRPC_VERBOSITY"] = "ERROR"

# --------------------------
# Load environment variables
# --------------------------
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    st.error("Please set your GOOGLE_API_KEY in a .env file!")
    st.stop()

genai.configure(api_key=API_KEY)

# --------------------------
# Load resume and summaries
# --------------------------
def load_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

summary_text = load_file("data/summary.txt")
bio_text = load_file("data/bio.txt")

with open("data/questions.json", "r", encoding="utf-8") as f:
    custom_questions = json.load(f)

# --------------------------
# Extract resume text
# --------------------------
def extract_resume_text(pdf_path="data/resume.pdf"):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

resume_text = extract_resume_text()

# --------------------------
# Streamlit UI
# --------------------------
st.set_page_config(page_title="Snehal Thorat Resume Assistant", page_icon="💼", layout="wide")
st.title("💼 Snehal Thorat - Resume Q&A Chatbot")

# --------------------------
# Profile card
# --------------------------
st.markdown(
    f"""
**Snehal Thorat**  
📍 Dallas, TX | 📧 sxt2265@mavs.uta.edu | [LinkedIn](https://www.linkedin.com/in/snehalthoratt/)  
**Education:** M.S. Computer Science, UT Arlington | B.E. Information Technology, Pune University  

**About Snehal:**  
{summary_text[:300]}... *ask below to read more*
"""
)

# --------------------------
# Initialize session state for chat
# --------------------------
if "history" not in st.session_state:
    st.session_state.history = []

# --------------------------
# Sidebar with interactive buttons
# --------------------------
st.sidebar.header("📌 Explore Snehal's Profile")

selected_question = None

with st.sidebar.expander("📄 Summary & Bio"):
    if st.button("View Summary"):
        selected_question = "Give me a summary of Snehal Thorat's profile"
    if st.button("View Bio"):
        selected_question = "Tell me about Snehal Thorat's background and experience"

with st.sidebar.expander("💻 Skills & Projects"):
    if st.button("Technical Skills"):
        selected_question = "What are Snehal's technical skills?"
    if st.button("Projects"):
        selected_question = "Tell me about Snehal's academic and professional projects"

with st.sidebar.expander("🏆 Awards & Certifications"):
    if st.button("Awards"):
        selected_question = "What awards has Snehal received?"
    if st.button("Certifications"):
        selected_question = "List Snehal's certifications"

st.sidebar.markdown("💻 **Skills:** Python 🐍, Java ☕, SQL 🗄, React ⚛️, AWS ☁️")

st.sidebar.download_button(
    label="📥 Download Resume",
    data=open("data/resume.pdf", "rb").read(),
    file_name="Snehal_Thorat_Resume.pdf"
)

# --------------------------
# Input field for user question with suggested questions
# --------------------------
st.subheader("❓ Ask a question")
user_question = st.text_input("Type your question here:", value=selected_question or "")

st.markdown("**Suggested Questions:**")
for q in custom_questions:
    if st.button(q):
        user_question = q

# --------------------------
# Get a valid Gemini model
# --------------------------
def get_valid_model():
    models = genai.list_models()
    for m in models:
        if "generateContent" in m.supported_generation_methods:
            return m.name
    return None

MODEL_NAME = get_valid_model()
if not MODEL_NAME:
    st.error("No valid Gemini model with generateContent found for your API key.")
    st.stop()

# --------------------------
# Function to generate answer immediately
# --------------------------
def generate_answer(question):
    prompt = f"""
You are a professional AI assistant answering questions about Snehal Thorat.

Resume Sections:
- Summary: {summary_text}
- Bio: {bio_text}
- Full Resume Text: {resume_text}

Answer the user's question based on the context above.  
Be professional, engaging, and concise. If the question is unrelated, politely say you cannot answer.  

Q: {question}
A:
"""
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        answer = response.text
        st.session_state.history.append((question, answer))
    except Exception as e:
        st.error(f"Error generating response: {e}")

# --------------------------
# Trigger answer generation automatically if a question is selected
# --------------------------
if user_question.strip():
    generate_answer(user_question)

# --------------------------
# Display chat history
# --------------------------
if st.session_state.history:
    st.subheader("💬 Chat History")
    for q, a in reversed(st.session_state.history):
        st.markdown(f"**Q:** 💡 {q}")
        st.markdown(f"**A:** 📝 {a}\n---")
