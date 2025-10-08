import streamlit as st
from PyPDF2 import PdfReader
from docx import Document
from odf.opendocument import load
from odf.text import P
import random
import re
from io import BytesIO

# -------------------------------
# 🎯 Page Setup
# -------------------------------
st.set_page_config(page_title="Resume Trust Score", page_icon="🛡️", layout="centered")
st.title("🛡️ Resume Trust Score Analyzer")
st.write("Upload a resume file (PDF, DOCX, or ODT) to check authenticity indicators and compute a trust score.")

# -------------------------------
# 📤 File Upload
# -------------------------------
uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx", "odt"])

# -------------------------------
# 🧩 Helper Functions
# -------------------------------
def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    metadata = reader.metadata
    return text, metadata

def extract_text_from_docx(file):
    doc = Document(file)
    text = "\n".join([p.text for p in doc.paragraphs])
    metadata = {"author": doc.core_properties.author, "created": doc.core_properties.created}
    return text, metadata

def extract_text_from_odt(file):
    odt_doc = load(file)
    paragraphs = odt_doc.getElementsByType(P)
    text = "\n".join([str(p.firstChild.data) if p.firstChild else "" for p in paragraphs])
    metadata = {"generator": odt_doc.meta.generator, "initial_creator": odt_doc.meta.initial_creator}
    return text, metadata

def analyze_resume_text(text):
    """Basic heuristic checks for simplicity"""
    word_count = len(text.split())
    keyword_hits = sum(1 for kw in ["python", "machine", "project", "experience", "intern", "data", "developer"] if kw.lower() in text.lower())
    ai_like_phrases = len(re.findall(r"\b(passio[n|t]ate|motivated|detail-oriented|team player|dynamic professional)\b", text.lower()))

    # Simple heuristic scoring
    text_score = min(1.0, (keyword_hits * 0.1 + word_count / 1000) - (ai_like_phrases * 0.05))
    return round(max(0.0, text_score), 2)

def calculate_trust_score(metadata, text_score):
    score = 0

    # Metadata authenticity (15%)
    if metadata:
        meta_str = str(metadata).lower()
        if any(x in meta_str for x in ["microsoft", "libreoffice", "google docs", "word", "writer"]):
            score += 12
        else:
            score += 7
    else:
        score += 5

    # Profile/skills simulated (25%)
    score += random.uniform(10, 25)

    # Skill validation simulated (25%)
    score += random.uniform(10, 25)

    # Identity verification simulated (20%)
    score += random.uniform(5, 20)

    # Text authenticity (15%)
    score += text_score * 15

    return round(min(score, 100), 2)

def get_badge(score):
    if score >= 85:
        return "🏆 Trusted"
    elif score >= 65:
        return "✅ Verified"
    elif score >= 45:
        return "⚠️ Suspicious"
    else:
        return "❌ Fake/Unverified"

# -------------------------------
# 🧮 Main Logic
# -------------------------------
if uploaded_file:
    st.success(f"File uploaded: {uploaded_file.name}")
    file_type = uploaded_file.name.split(".")[-1].lower()

    try:
        if file_type == "pdf":
            text, metadata = extract_text_from_pdf(uploaded_file)
        elif file_type == "docx":
            text, metadata = extract_text_from_docx(uploaded_file)
        elif file_type == "odt":
            text, metadata = extract_text_from_odt(uploaded_file)
        else:
            st.error("Unsupported file type.")
            st.stop()

        if not text.strip():
            st.warning("No readable text found in the file. Please upload a text-based resume.")
        else:
            text_score = analyze_resume_text(text)
            trust_score = calculate_trust_score(metadata, text_score)
            badge = get_badge(trust_score)

            # Display results
            st.divider()
            st.markdown(f"### 🧾 Resume Summary")
            st.write(f"**Total Words:** {len(text.split())}")
            st.write(f"**Detected Keywords:** {text_score * 10:.0f}")
            st.write(f"**AI-like Phrases:** Heuristic applied automatically")

            st.divider()
            st.markdown(f"### 🔐 Trust Score Results")
            st.progress(trust_score / 100)
            st.markdown(f"**Score:** `{trust_score} / 100`")
            st.markdown(f"**Badge:** {badge}")

            with st.expander("🔍 View Extracted Metadata"):
                st.json({k: str(v) for k, v in metadata.items() if v})

            with st.expander("🧠 Raw Extracted Text (first 500 chars)"):
                st.text(text[:500] + ("..." if len(text) > 500 else ""))

    except Exception as e:
        st.error(f"Error reading file: {e}")

else:
    st.info("Please upload a resume file to start analysis.")
