import streamlit as st
import fitz  # PyMuPDF
import re
from io import BytesIO

st.set_page_config(page_title="Smart Quiz Extractor", layout="centered")

st.title("📘 AI Quiz Extractor from PDF")
st.caption("Upload a PDF containing MCQs — the app will extract, display, and let you play interactively!")

# --- Upload PDF ---
uploaded_pdf = st.file_uploader("📂 Upload your PDF file with MCQs", type=["pdf"])

if uploaded_pdf:
    # --- Read PDF text ---
    pdf_doc = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
    text = ""
    for page in pdf_doc:
        text += page.get_text("text")

    # --- Basic MCQ Parsing Logic ---
    # Expected format:
    # 1. Question text
    # A. Option 1
    # B. Option 2
    # C. Option 3
    # D. Option 4
    # Answer: B

    pattern = re.compile(
        r"(\d+\.\s*.+?)(?:\n\s*[A-D]\..+?){4,}\n\s*Answer\s*[:\-]?\s*([A-D])",
        re.DOTALL
    )

    matches = pattern.findall(text)

    if not matches:
        st.error("❌ No valid MCQs found. Please check your PDF format.")
    else:
        st.success(f"✅ Found {len(matches)} questions!")
        score = st.session_state.get("score", 0)
        total = len(matches)

        # --- Display Questions ---
        for i, (block, answer) in enumerate(matches, 1):
            st.markdown(f"### Q{i}. {block.splitlines()[0]}")
            options = re.findall(r"[A-D]\.\s*(.+)", block)
            
            # Create radio buttons for each question
            user_choice = st.radio(
                f"Select answer for Question {i}",
                options,
                key=f"q_{i}"
            )

            # Check correctness
            correct_option = ord(answer.strip()) - 65  # Convert A->0, B->1...
            if user_choice:
                if options.index(user_choice) == correct_option:
                    st.markdown("✅ **Correct!**", unsafe_allow_html=True)
                else:
                    st.markdown(f"❌ **Wrong!** Correct Answer: {answer}. {options[correct_option]}")

        st.info("💡 Tip: Format your PDF with clear 'Answer: A/B/C/D' after each question.")

else:
    st.markdown("👆 Upload a PDF file to start the quiz.")
