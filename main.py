import streamlit as st
from PyPDF2 import PdfReader
from docx import Document
from odf.opendocument import load
from odf.text import P
import re

# -------------------------------
# Page Setup
# -------------------------------
st.set_page_config(page_title="Resume Trust Score", page_icon="🛡️", layout="centered")
st.title("🛡️ Effective Resume Trust Score Analyzer")
st.write("Upload a resume (PDF, DOCX, ODT) and get a realistic trust score based on text, metadata, and skill verification.")

# -------------------------------
# File Upload
# -------------------------------
uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx", "odt"])

# -------------------------------
# Helper Functions
# -------------------------------
def extract_text_pdf(file):
    reader = PdfReader(file)
    text = "".join([page.extract_text() or "" for page in reader.pages])
    metadata = reader.metadata
    return text, metadata

def extract_text_docx(file):
    doc = Document(file)
    text = "\n".join([p.text for p in doc.paragraphs])
    metadata = {"author": doc.core_properties.author, "created": doc.core_properties.created}
    return text, metadata

def extract_text_odt(file):
    odt_doc = load(file)
    paragraphs = odt_doc.getElementsByType(P)
    text = "\n".join([str(p.firstChild.data) if p.firstChild else "" for p in paragraphs])
    metadata = {"generator": odt_doc.meta.generator, "initial_creator": odt_doc.meta.initial_creator}
    return text, metadata

def analyze_text(text):
    """Realistic text analysis: keyword hits, AI-like phrases, length"""
    keywords = ["python", "java", "machine", "data", "project", "analysis", "developer", "internship"]
    ai_like_phrases = ["passionate", "motivated", "detail-oriented", "team player", "dynamic professional"]

    word_count = len(text.split())
    keyword_hits = sum(1 for kw in keywords if kw.lower() in text.lower())
    ai_hits = sum(1 for ph in ai_like_phrases if ph.lower() in text.lower())

    # Text score 0–1
    text_score = min(1.0, (keyword_hits * 0.1 + word_count / 2000) - (ai_hits * 0.05))
    return max(0.0, text_score)

def calculate_trust_score(metadata, text_score, skill_score=0.0, profile_score=0.0, identity_verified=False):
    """Weighted trust score calculation based on real metrics"""
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

    # Profile verification (25%)
    score += profile_score * 25

    # Skill verification (25%)
    score += skill_score * 25

    # Identity verification (20%)
    if identity_verified:
        score += 20

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
# Main Logic
# -------------------------------
if uploaded_file:
    st.success(f"File uploaded: {uploaded_file.name}")
    file_type = uploaded_file.name.split(".")[-1].lower()

    # Extract text + metadata
    try:
        if file_type == "pdf":
            text, metadata = extract_text_pdf(uploaded_file)
        elif file_type == "docx":
            text, metadata = extract_text_docx(uploaded_file)
        elif file_type == "odt":
            text, metadata = extract_text_odt(uploaded_file)
        else:
            st.error("Unsupported file type.")
            st.stop()
    except Exception as e:
        st.error(f"Failed to read resume: {e}")
        st.stop()

    if not text.strip():
        st.warning("No readable text found in the file.")
        st.stop()

    # Text analysis
    text_score = analyze_text(text)

    # Simulate Skill Test Score (0–1) input
    skill_score = st.slider("Simulated Skill Test Score (0–1)", 0.0, 1.0, 0.8, 0.01)

    # Simulate Profile Verification Score (0–1) input
    profile_score = st.slider("Simulated Profile Verification Score (0–1)", 0.0, 1.0, 0.85, 0.01)

    # Identity Verification Checkbox
    identity_verified = st.checkbox("Identity Verified?", value=True)

    # Calculate final trust score
    trust_score = calculate_trust_score(metadata, text_score, skill_score, profile_score, identity_verified)
    badge = get_badge(trust_score)

    # Display results
    st.divider()
    st.markdown("### 🔐 Trust Score Results")
    st.progress(trust_score / 100)
    st.markdown(f"**Score:** `{trust_score} / 100`  &nbsp;&nbsp; **Badge:** {badge}")

    st.divider()
    st.markdown("### 🧾 Resume Summary")
    st.write(f"**Total Words:** {len(text.split())}")
    st.write(f"**Keyword & AI-like Phrase Analysis Score:** {text_score}")
    st.write(f"**Skill Test Score:** {skill_score}")
    st.write(f"**Profile Verification Score:** {profile_score}")
    st.write(f"**Identity Verified:** {identity_verified}")

    with st.expander("🔍 View Extracted Metadata"):
        st.json({k: str(v) for k, v in metadata.items() if v})

    with st.expander("🧠 Raw Extracted Text (first 500 chars)"):
        st.text(text[:500] + ("..." if len(text) > 500 else ""))
else:
    st.info("Please upload a resume to start analysis.")
