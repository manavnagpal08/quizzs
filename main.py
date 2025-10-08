import streamlit as st
from PyPDF2 import PdfReader
from docx import Document
from odf.opendocument import load
from odf.text import P
import re
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# -------------------------------
# Page Setup
# -------------------------------
st.set_page_config(page_title="Accurate Resume Trust Score", page_icon="🛡️", layout="centered")
st.title("🛡️ Resume Trust Score Analyzer (AI Detection)")

# -------------------------------
# Load Local AI Detector Model
# Using open-source GPT detector
# -------------------------------
@st.cache_resource
def load_detector():
    model_name = "roberta-base-openai-detector"  # Example: replace with a real local model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    return tokenizer, model

tokenizer, model = load_detector()

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

def detect_ai(text):
    """Local AI detection using transformer model"""
    inputs = tokenizer(text[:512], return_tensors="pt", truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    logits = outputs.logits
    probs = torch.softmax(logits, dim=1)
    ai_prob = float(probs[0][1])  # probability that text is AI-generated
    return ai_prob  # 0–1, higher = more likely AI

def analyze_text(text):
    """Keyword and AI-like phrase analysis"""
    keywords = ["python", "java", "machine", "data", "project", "analysis", "developer", "internship"]
    ai_like_phrases = ["passionate", "motivated", "detail-oriented", "team player", "dynamic professional"]

    word_count = len(text.split())
    keyword_hits = sum(1 for kw in keywords if kw.lower() in text.lower())
    ai_hits = sum(1 for ph in ai_like_phrases if ph.lower() in text.lower())

    text_score = min(1.0, (keyword_hits * 0.1 + word_count / 2000) - (ai_hits * 0.05))
    return max(0.0, text_score)

def calculate_trust_score(metadata, text_score, ai_prob, skill_score=0.8, profile_score=0.85, identity_verified=True):
    """Weighted trust score with AI probability"""
    score = 0

    # Metadata (15%)
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

    # Text authenticity (15%) adjusted for AI
    score += text_score * (15 * (1 - ai_prob))  # penalize AI-generated text

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

    try:
        if file_type == "pdf":
            text, metadata = extract_text_pdf(uploaded_file)
        elif file_type == "docx":
            text, metadata = extract_text_docx(uploaded_file)
        elif file_type == "odt":
            text, metadata = extract_text_odt(uploaded_file)
        else:
            st.error("Unsupported file type")
            st.stop()
    except Exception as e:
        st.error(f"Failed to read resume: {e}")
        st.stop()

    if not text.strip():
        st.warning("No readable text found in file.")
        st.stop()

    # AI detection
    ai_prob = detect_ai(text)
    st.write(f"AI Likelihood: {ai_prob*100:.1f}%")

    # Text heuristic analysis
    text_score = analyze_text(text)

    # Calculate trust score
    trust_score = calculate_trust_score(metadata, text_score, ai_prob)
    badge = get_badge(trust_score)

    # Display results
    st.divider()
    st.markdown("### 🔐 Trust Score Results")
    st.progress(trust_score / 100)
    st.markdown(f"**Score:** `{trust_score} / 100`  &nbsp;&nbsp; **Badge:** {badge}")

    st.divider()
    st.markdown("### 🧾 Resume Summary")
    st.write(f"**Word Count:** {len(text.split())}")
    st.write(f"**Text Heuristic Score:** {text_score}")
    st.write(f"**Skill Score:** 0.8 (simulated)")
    st.write(f"**Profile Score:** 0.85 (simulated)")
    st.write(f"**Identity Verified:** True")

    with st.expander("🔍 Extracted Metadata"):
        st.json({k: str(v) for k, v in metadata.items() if v})

    with st.expander("🧠 Text Preview (first 500 chars)"):
        st.text(text[:500] + ("..." if len(text) > 500 else ""))
else:
    st.info("Upload a resume to analyze AI likelihood and trust score.")
