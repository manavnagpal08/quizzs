import streamlit as st
from PyPDF2 import PdfReader
from docx import Document
from odf.opendocument import load
from odf.text import P
import re
from datetime import datetime

# -------------------------------
# Configuration & Setup
# -------------------------------
st.set_page_config(page_title="Resume Trust Score", page_icon="🛡️", layout="centered")
st.title("🛡️ High-Accuracy Resume Trust Score Analyzer")
st.write("Upload a resume (PDF, DOCX, ODT) and get a realistic trust score based on deep text, metadata, and simulated verification.")

# -------------------------------
# File Upload (FIXED: Added missing file uploader component)
# -------------------------------
uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx", "odt"])

# -------------------------------
# Helper Functions for File Extraction
# -------------------------------
def extract_text_pdf(file):
    reader = PdfReader(file)
    text = "".join([page.extract_text() or "" for page in reader.pages])
    metadata = reader.metadata
    return text, metadata

def extract_text_docx(file):
    doc = Document(file)
    text = "\n".join([p.text for p in doc.paragraphs])
    metadata = {"author": doc.core_properties.author, "created": doc.core_properties.created, "modified": doc.core_properties.modified}
    return text, metadata

def extract_text_odt(file):
    odt_doc = load(file)
    paragraphs = odt_doc.getElementsByType(P)
    text = "\n".join([str(p.firstChild.data) if p.firstChild else "" for p in paragraphs])
    metadata = {"generator": odt_doc.meta.generator, "initial_creator": odt_doc.meta.initial_creator}
    return text, metadata

# -------------------------------
# New & Improved Analysis Logic
# -------------------------------
def analyze_content(text):
    """
    Analyzes resume content for quantification, specific skills, and generic fluff.
    Returns a Text Authenticity Score (0-100).
    """
    text_lower = text.lower()
    word_count = len(text.split())

    # Factor 1: Domain Relevance & Depth (Weight 40%) - Scores technical specificity
    tech_keywords = [
        "deep learning", "kubernetes", "tensorflow", "agile methodology", "microservices", 
        "sql", "aws", "azure", "docker", "react native", "solidity", "api gateway"
    ]
    
    # Check for specific, high-value technical keywords
    domain_relevance_hits = sum(1 for kw in tech_keywords if kw in text_lower)
    
    # Factor 2: Quantification and Action (Weight 40%) - Scores impact/results
    # Strong action verbs suggest ownership and impact
    action_verbs = ["spearheaded", "optimized", "reduced", "increased", "managed", "deployed", "architected", "delivered"]
    
    # Regex to find numbers followed by common units or symbols (e.g., 20%, $5k, 3 million)
    quantifiable_pattern = r'\d{1,3}[,.\d]*\s*([%kK$]|million|billion|times|users|projects)' 
    
    action_hit_score = sum(1 for av in action_verbs if av in text_lower) * 4 # More weight for strong verbs
    quant_hits = len(re.findall(quantifiable_pattern, text)) * 6 # Highest weight for numbers/metrics
    
    quantification_score = action_hit_score + quant_hits
    
    # Factor 3: AI/Fluff Detection (Penalty) - Penalizes generic, meaningless filler
    ai_like_phrases = [
        "highly motivated", "passionate and driven", "synergy", "seamlessly integrated", 
        "go-getter", "dynamic professional", "results-driven", "fast learner"
    ]
    fluff_penalty = sum(1 for ph in ai_like_phrases if ph in text_lower) * 15 # Heavy penalty

    # Combine factors into an Authenticity Score
    raw_authenticity_score = (
        (domain_relevance_hits * 10) +
        (quantification_score) +
        (word_count / 15) # Small bonus for adequate length
    ) - fluff_penalty
    
    # Normalize and clamp score between 0 and 100
    authenticity_score = max(0, min(100, raw_authenticity_score))
    
    return {
        "score": authenticity_score,
        "metrics_hits": len(re.findall(quantifiable_pattern, text)),
        "action_verbs_hits": sum(1 for av in action_verbs if av in text_lower),
        "fluff_penalty_count": sum(1 for ph in ai_like_phrases if ph in text_lower),
    }

def calculate_trust_score(metadata, content_analysis, skill_score=0.0, profile_score=0.0, identity_verified=False):
    """
    Weighted trust score calculation based on deep analysis and external simulation.
    New Weights: Skill (35%), Profile (20%), Identity (15%), Text Authenticity (20%), Metadata (10%)
    """
    
    score = 0
    text_authenticity_score = content_analysis['score']
    
    # 1. Skill Verification (35%) - High weight for external testing
    score += skill_score * 35

    # 2. Profile Verification (20%) - Confirmed LinkedIn/GitHub/Portfolio
    score += profile_score * 20

    # 3. Text Authenticity (20%) - Depth of content (quantification, specificity)
    score += text_authenticity_score * 0.2

    # 4. Identity verification (15%) - Binary check
    if identity_verified:
        score += 15

    # 5. Metadata Authenticity (10%)
    metadata_score = 0
    if metadata:
        meta_str = str(metadata).lower()
        
        # Check for recognized creation tools (more trustworthy than generic online converters)
        if any(x in meta_str for x in ["microsoft", "libreoffice", "google docs", "word", "writer"]):
            metadata_score += 5
        
        # Check for presence of author/creator fields
        if 'creator' in meta_str or 'author' in meta_str:
            metadata_score += 3
        
        # Check if modified date is recent (suggests active management)
        if metadata.get('modified'):
            try:
                # Simple check: if modified in the last 365 days
                modified_date = metadata['modified']
                if isinstance(modified_date, datetime):
                     time_diff = datetime.now() - modified_date
                     if time_diff.days < 365:
                         metadata_score += 2
            except Exception:
                pass # Ignore if date format is invalid

    score += metadata_score # Max 10 points

    return round(min(score, 100), 2)

def get_badge(score):
    if score >= 90:
        return "🥇 Elite Trust"
    elif score >= 75:
        return "🏆 Verified"
    elif score >= 55:
        return "⚠️ Suspicious"
    else:
        return "❌ Unverified/High Risk"

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
        st.error(f"Failed to read resume. This might be a corrupted file: {e}")
        st.stop()

    if not text.strip():
        st.warning("No readable text found in the file. Score calculation will be based purely on simulations/metadata.")
        content_analysis = {"score": 0, "metrics_hits": 0, "action_verbs_hits": 0, "fluff_penalty_count": 0}
    else:
        # Deep Content analysis
        content_analysis = analyze_content(text)

    st.divider()
    st.markdown("### External Simulation Inputs")
    st.info("These simulate data from external verification platforms (e.g., skill tests, background checks).")

    # Simulate Skill Test Score (0–1) input
    skill_score = st.slider("Skill Test/Coding Assessment Score (Weight: 35%)", 0.0, 1.0, 0.85, 0.01, 
                            help="Simulates a score from an external, validated technical assessment.")

    # Simulate Profile Verification Score (0–1) input
    profile_score = st.slider("LinkedIn/GitHub Profile Verification Score (Weight: 20%)", 0.0, 1.0, 0.9, 0.01,
                              help="Simulates the completeness and consistency of external professional profiles.")

    # Identity Verification Checkbox
    identity_verified = st.checkbox("Identity Verified via 3rd Party Check? (Weight: 15%)", value=True)

    # Calculate final trust score
    trust_score = calculate_trust_score(metadata, content_analysis, skill_score, profile_score, identity_verified)
    badge = get_badge(trust_score)

    # -------------------------------
    # Display results
    # -------------------------------
    st.divider()
    st.markdown("## 🔐 Trust Score Summary")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.metric(label="Overall Trust Score", value=f"{trust_score} / 100")
        st.subheader(f"Status: {badge}")
    
    with col2:
        st.progress(trust_score / 100, text="Score Progression")
        
        st.markdown(f"""
        <div style="padding: 10px; border-radius: 8px; background-color: #f0f2f6; margin-top: 10px;">
            **Deep Content Authenticity Score:** {content_analysis['score']:.2f}/100 
            <br> (Weight: 20% of Final Score)
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown("### 🔎 Detailed Text Analysis (Internal Factors)")
    st.info("This section analyzes the *quality* of the claims made in the resume text.")
    
    
    metrics_col, action_col, fluff_col = st.columns(3)
    
    metrics_col.metric(
        label="Quantifiable Metrics Found",
        value=content_analysis['metrics_hits'],
        help="Higher scores for quantifiable data (e.g., 20% increase, $5k savings)."
    )
    
    action_col.metric(
        label="Strong Action Verbs Found",
        value=content_analysis['action_verbs_hits'],
        help="Higher scores for impactful verbs (e.g., 'architected', 'spearheaded')."
    )
    
    fluff_col.metric(
        label="Generic Fluff Penalty Hits",
        value=content_analysis['fluff_penalty_count'],
        help="Lower scores for generic phrases (e.g., 'highly motivated', 'dynamic professional')."
    )

    with st.expander("🔍 View Extracted Metadata"):
        st.json({k: str(v) for k, v in metadata.items() if v})

    with st.expander("🧠 Raw Extracted Text (first 500 chars)"):
        st.text(text[:500] + ("..." if len(text) > 500 else ""))
else:
    st.info("Please upload a resume (PDF, DOCX, ODT) to start the deep analysis.")
