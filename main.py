import streamlit as st
import pdfplumber
import re

st.set_page_config(page_title="PDF Quiz App", layout="centered")
st.title("📘 Interactive Quiz from PDF")

uploaded_pdf = st.file_uploader("Upload your PDF file with MCQs", type=["pdf"])

if uploaded_pdf:
    with pdfplumber.open(uploaded_pdf) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"

    # --- Basic MCQ Parsing ---
    # Expected format:
    # 1. Question
    # A. Option 1
    # B. Option 2
    # C. Option 3
    # D. Option 4
    # Answer: B

    pattern = re.compile(
        r"(\d+\..+?)(?:\n\s*[A-D]\..+?){4,}\n\s*Answer\s*[:\-]?\s*([A-D])",
        re.DOTALL
    )
    matches = pattern.findall(text)

    if not matches:
        st.error("❌ No MCQs found. Check PDF format.")
    else:
        st.success(f"✅ Found {len(matches)} questions!")

        for i, (block, answer) in enumerate(matches, 1):
            st.markdown(f"### Q{i}. {block.splitlines()[0]}")
            options = re.findall(r"[A-D]\.\s*(.+)", block)

            user_choice = st.radio(f"Select answer for Question {i}", options, key=f"q_{i}")

            correct_option = ord(answer.strip()) - 65
            if user_choice:
                if options.index(user_choice) == correct_option:
                    st.markdown("✅ **Correct!**")
                else:
                    st.markdown(f"❌ **Wrong!** Correct Answer: {answer}. {options[correct_option]}")
else:
    st.info("👆 Upload a PDF file to start the quiz.")
