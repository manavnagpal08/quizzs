import streamlit as st

# Sample MCQs
mcqs = [
    {"question": "1. What is the maximum height of a Red-Black Tree with n nodes?",
     "options": ["2*log(n+1)", "log(n)", "n-1", "n/2"], "answer": "2*log(n+1)"},
    {"question": "2. Which of the following is true about Red-Black Trees?",
     "options": ["Every red node must have red children", "All leaves are black", "Root must be red", "Black height can vary"], "answer": "All leaves are black"},
    {"question": "3. What is the color of leaves in a Red-Black Tree?",
     "options": ["Red", "Black", "Can be either", "Depends on parent"], "answer": "Black"},
    {"question": "4. In a Red-Black Tree, a red node can have how many red children?",
     "options": ["0", "1", "2", "3"], "answer": "0"},
]

st.title("Red-Black Tree Quiz")

score = 0

for i, mcq in enumerate(mcqs):
    st.subheader(mcq["question"])
    user_answer = st.radio("Select your answer:", mcq["options"], key=f"q{i}")
    if user_answer:
        if st.button("Check Answer", key=f"btn{i}"):
            if user_answer == mcq["answer"]:
                st.success("✅ Correct!")
                score += 1
            else:
                st.error(f"❌ Wrong! Correct answer: {mcq['answer']}")

st.write(f"Your score: {score}/{len(mcqs)}")
