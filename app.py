
import streamlit as st
import random
import re
import json

st.set_page_config(
    page_title="Quiz Generator Online",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 Quiz Generator Online")
st.write("Transform your learning materials into interactive quizzes.")

st.sidebar.header("⚙️ Quiz Settings")

question_type = st.sidebar.selectbox(
    "Question Type",
    ["Multiple Choice", "True / False", "Fill in the Blank", "Mixed"]
)

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Medium", "Hard"]
)

num_questions = st.sidebar.slider(
    "Number of Questions", 1, 10, 5
)

st.subheader("📚 Learning Material")

default_text = (
    "Python is a popular programming language. "
    "Machine learning allows computers to learn from data. "
    "Artificial intelligence enables machines to perform tasks "
    "that normally require human intelligence. "
    "A database stores and organizes information. "
    "Data visualization presents information using charts and graphs. "
    "A function is a reusable block of code. "
    "An algorithm is a sequence of steps used to solve a problem. "
    "Supervised learning uses labeled training data."
)

material = st.text_area(
    "Paste your notes here:",
    value=default_text,
    height=200
)

STOP_WORDS = {
    "which", "their", "there", "these", "those", "where",
    "using", "normally", "allows", "enables", "that", "from",
    "with", "into", "this", "then", "than", "have", "been",
    "used", "uses", "they", "what", "when", "while", "popular",
    "about", "after", "before", "between", "because", "through",
    "your", "yourself", "also", "such", "some", "many", "more",
    "most", "very", "each", "both", "only", "other", "does",
    "will", "would", "could", "should", "being", "task", "tasks"
}


def split_sentences(text):
    return [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", text.strip())
        if len(re.findall(r"\b[A-Za-z][A-Za-z-]*\b", sentence)) >= 5
    ]


def get_keywords(text):
    words = re.findall(r"\b[A-Za-z][A-Za-z-]*\b", text)
    return list(dict.fromkeys(
        word for word in words
        if len(word) >= 4 and word.lower() not in STOP_WORDS
    ))


def choose_answer(sentence, difficulty):
    words = get_keywords(sentence)

    if not words:
        words = re.findall(r"\b[A-Za-z][A-Za-z-]*\b", sentence)

    if difficulty == "Easy":
        return words[-1]
    elif difficulty == "Medium":
        return words[len(words) // 2]
    else:
        return max(words, key=len)



def make_questions(text, selected_type, count, difficulty):
    sentences = split_sentences(text)

    if not sentences:
        return []

    questions = []
    shuffled_sentences = sentences[:]
    random.shuffle(shuffled_sentences)

    # Related options for common AI, programming, and data science terms
    related_terms = {
        "algorithm": ["function", "database", "programming", "dataset"],
        "problem": ["dataset", "algorithm", "function", "database"],
        "database": ["dataset", "algorithm", "function", "program"],
        "information": ["data", "knowledge", "database", "algorithm"],
        "language": ["algorithm", "database", "function", "dataset"],
        "programming": ["algorithm", "database", "visualization", "learning"],
        "learning": ["algorithm", "database", "visualization", "programming"],
        "data": ["information", "algorithm", "function", "database"],
        "charts": ["graphs", "tables", "algorithms", "functions"],
        "graphs": ["charts", "tables", "databases", "functions"],
        "function": ["algorithm", "database", "variable", "dataset"],
        "intelligence": ["learning", "programming", "visualization", "database"],
        "computers": ["databases", "algorithms", "functions", "datasets"],
        "training": ["testing", "programming", "visualization", "database"],
    }

    all_keywords = get_keywords(text)

    for sentence in shuffled_sentences:
        if len(questions) >= count:
            break

        current_type = selected_type

        if current_type == "Mixed":
            current_type = random.choice([
                "Multiple Choice",
                "True / False",
                "Fill in the Blank"
            ])

        answer = choose_answer(sentence, difficulty)

        blanked_sentence = re.sub(
            r"\b" + re.escape(answer) + r"\b",
            "__________",
            sentence,
            count=1,
            flags=re.IGNORECASE
        )

        if current_type == "True / False":
            question = {
                "type": current_type,
                "question": sentence,
                "answer": "True",
                "options": ["True", "False"]
            }

        elif current_type == "Fill in the Blank":
            question = {
                "type": current_type,
                "question": blanked_sentence,
                "answer": answer,
                "options": []
            }

        else:
            # Find related distractors instead of random words from the notes
            distractors = related_terms.get(answer.lower(), [])

            # Add other meaningful keywords if the related list is too short
            for word in all_keywords:
                if word.lower() != answer.lower() and word.lower() not in {
                    item.lower() for item in distractors
                }:
                    distractors.append(word)

            options = [answer]

            for word in distractors:
                if word.lower() not in {
                    option.lower() for option in options
                }:
                    options.append(word)

                if len(options) == 4:
                    break

            random.shuffle(options)

            question = {
                "type": current_type,
                "question": blanked_sentence,
                "answer": answer,
                "options": options
            }

        questions.append(question)

    return questions



if "quiz" not in st.session_state:
    st.session_state.quiz = []

if "submitted" not in st.session_state:
    st.session_state.submitted = False


if st.button("✨ Generate Quiz", type="primary"):
    if not material.strip():
        st.warning("Please enter learning material.")
    else:
        new_quiz = make_questions(
            material,
            question_type,
            num_questions,
            difficulty
        )

        if new_quiz:
            st.session_state.quiz = new_quiz
            st.session_state.submitted = False

            # Clear answers from the previous quiz.
            for key in list(st.session_state.keys()):
                if key.startswith("answer_"):
                    del st.session_state[key]

            st.success(f"Generated {len(new_quiz)} questions!")
        else:
            st.session_state.quiz = []
            st.session_state.submitted = False
            st.warning(
                "Please enter a few complete sentences "
                "with enough words to generate questions."
            )


if st.session_state.quiz:
    st.divider()
    st.subheader("📝 Your Quiz")

    for index, question in enumerate(st.session_state.quiz):
        st.markdown(
            f"**Question {index + 1} ({question['type']}):** "
            f"{question['question']}"
        )

        if question["type"] in ["Multiple Choice", "True / False"]:
            st.radio(
                "Choose your answer:",
                question["options"],
                key=f"answer_{index}",
                index=None
            )
        else:
            st.text_input(
                "Your answer:",
                key=f"answer_{index}"
            )

    if st.button("✅ Submit Answers"):
        st.session_state.submitted = True

    if st.session_state.submitted:
        score = 0
        total = len(st.session_state.quiz)
        results = []

        st.subheader("📊 Quiz Results")

        for index, question in enumerate(st.session_state.quiz):
            user_answer = str(
                st.session_state.get(f"answer_{index}", "")
            ).strip()

            correct_answer = str(question["answer"]).strip()

            is_correct = (
                user_answer.casefold() == correct_answer.casefold()
            )

            if is_correct:
                score += 1
                st.success(f"Question {index + 1}: Correct!")
            else:
                st.error(
                    f"Question {index + 1}: Incorrect. "
                    f"Correct answer: {correct_answer}"
                )

            results.append({
                "question_number": index + 1,
                "question": question["question"],
                "question_type": question["type"],
                "your_answer": user_answer or "Not answered",
                "correct_answer": correct_answer,
                "result": "Correct" if is_correct else "Incorrect"
            })

        percentage = score / total * 100 if total else 0

        st.metric("Your Score", f"{score}/{total}")
        st.progress(percentage / 100)
        st.write(f"**Percentage:** {percentage:.1f}%")

        report_lines = [
            "QUIZ GENERATOR ONLINE",
            f"Difficulty: {difficulty}",
            f"Score: {score}/{total} ({percentage:.1f}%)",
            ""
        ]

        for result in results:
            report_lines.extend([
                f"Question {result['question_number']}: "
                f"{result['question']}",
                f"Your answer: {result['your_answer']}",
                f"Correct answer: {result['correct_answer']}",
                f"Result: {result['result']}",
                ""
            ])

        st.download_button(
            "📥 Download Answer Report",
            data="\n".join(report_lines),
            file_name="quiz_report.txt",
            mime="text/plain"
        )

        st.download_button(
            "📄 Download Answer Key (JSON)",
            data=json.dumps(results, indent=2),
            file_name="answer_key.json",
            mime="application/json"
        )

st.divider()
st.caption(
    "Quiz Generator Online | AI & Data Science Internship Project"
)
