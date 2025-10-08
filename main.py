import streamlit as st
import random

st.set_page_config(page_title="Resume Trust Score Demo", page_icon="🛡️", layout="centered")

st.title("🛡️ Resume Trust Score – Sample Demo")

# ---- Simulated Candidate Data ----
sample_candidates = [
    {
        "name": "Priya Sharma",
        "metadata_check": "clean",
        "profile_match_score": 0.9,
        "skill_test_score": 0.88,
        "id_verified": True,
        "text_realism_score": 0.85
    },
    {
        "name": "Rohit Kumar",
        "metadata_check": "suspicious",
        "profile_match_score": 0.45,
        "skill_test_score": 0.55,
        "id_verified": False,
        "text_realism_score": 0.4
    },
    {
        "name": "Ananya Rao",
        "metadata_check": "clean",
        "profile_match_score": 0.95,
        "skill_test_score": 0.9,
        "id_verified": True,
        "text_realism_score": 0.92
    }
]

# ---- Trust Score Function ----
def calculate_resume_trust_score(candidate):
    score = 0

    # 1. Metadata authenticity
    if candidate["metadata_check"] == "clean":
        score += 15
    elif candidate["metadata_check"] == "suspicious":
        score += 7

    # 2. Profile verification (weighted 25%)
    score += candidate.get("profile_match_score", 0) * 25

    # 3. Skill validation (weighted 25%)
    score += candidate.get("skill_test_score", 0) * 25

    # 4. Identity verification (weighted 20%)
    if candidate.get("id_verified"):
        score += 20

    # 5. Text authenticity (weighted 15%)
    score += candidate.get("text_realism_score", 0) * 15

    return round(min(score, 100), 2)


# ---- Badge Generator ----
def get_badge(score):
    if score >= 85:
        return "🏆 Trusted"
    elif score >= 65:
        return "✅ Verified"
    elif score >= 45:
        return "⚠️ Suspicious"
    else:
        return "❌ Fake/Unverified"


# ---- Display Section ----
st.subheader("Candidate Verification Results")

for c in sample_candidates:
    c["trust_score"] = calculate_resume_trust_score(c)
    c["badge"] = get_badge(c["trust_score"])

    st.markdown(f"### 👤 {c['name']}")
    st.progress(c["trust_score"] / 100)
    st.markdown(f"**Trust Score:** {c['trust_score']} / 100  &nbsp;&nbsp;|&nbsp;&nbsp; **Badge:** {c['badge']}")
    with st.expander("View Verification Summary"):
        st.json({
            "Metadata": c["metadata_check"],
            "Profile Match": c["profile_match_score"],
            "Skill Test": c["skill_test_score"],
            "Identity Verified": c["id_verified"],
            "AI Authenticity": c["text_realism_score"]
        })
    st.divider()

# Optional: random test button
if st.button("🔄 Generate Random Candidate"):
    st.toast("Simulated random candidate score generated!", icon="🧠")
    rand_cand = {
        "name": f"Candidate {random.randint(1,100)}",
        "metadata_check": random.choice(["clean", "suspicious"]),
        "profile_match_score": random.random(),
        "skill_test_score": random.random(),
        "id_verified": random.choice([True, False]),
        "text_realism_score": random.random()
    }
    rand_cand["trust_score"] = calculate_resume_trust_score(rand_cand)
    rand_cand["badge"] = get_badge(rand_cand["trust_score"])
    st.write(rand_cand)
