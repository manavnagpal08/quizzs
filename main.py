import streamlit as st
from PyPDF2 import PdfReader
import re

st.title("📄 Upload MCQ PDF & Take Quiz")

# Upload PDF
uploaded_file = st.file_uploader("Upload your MCQ PDF", type=["pdf"])

if uploaded_file:
    # Read PDF
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"

    # Parse questions and options
    pattern = r'(\d+\..*?)\nA\.\s(.*?)\nB\.\s(.*?)\nC\.\s(.*?)\nD\.\s(.*?)\nAnswer:\s([A-D])'
    mcqs = re.findall(pattern, text, re.DOTALL)

    if mcqs:
        st.success(f"✅ Found {len(mcqs)} questions!")
        score = 0

        for i, mcq in enumerate(mcqs):
            question, optA, optB, optC, optD, ans = mcq
            options = [optA, optB, optC, optD]

            st.subheader(question)
            user_answer = st.radio("Select your answer:", options, key=f"q{i}")

            if st.button("Check Answer", key=f"btn{i}"):
                if user_answer == options[ord(ans)-65]:  # Convert A-D to 0-3 index
                    st.success("✅ Correct!")
                    score += 1
                else:
                    st.error(f"❌ Wrong! Correct answer: {options[ord(ans)-65]}")

        st.write(f"### Your score: {score}/{len(mcqs)}")
    else:
        st.warning("⚠️ Could not find questions in this PDF. Make sure it's in the correct format!")
