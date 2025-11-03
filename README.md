# OOP Python Quiz Application Generation with Streamlit

## 🎯 Objective

Develop an **interactive quiz application** in Python using **Object-Oriented Programming (OOP)** and **Streamlit**.
This project will help you practice OOP concepts, dynamic GUI creation, and scoring logic for quizzes.

---

## 🧠 Learning Goals

* Apply OOP concepts: classes, objects, singleton pattern, encapsulation.
* Handle **dynamic user input** in a GUI using Streamlit.
* Implement scoring logic for **single-choice** and **multiple-choice** questions.
* Use **session state** in Streamlit to persist quiz data.
* (Optional) Visualize quiz results using charts with **Seaborn** or **Matplotlib**.

---

## 📦 Provided Materials

* `app.py` – Starter Streamlit app (basic structure).
* `models.py` – Skeleton classes for quiz logic.
* `quiz_dataset.json` – Predefined quiz dataset in JSON format.

---

## 📝 Instructions

### Step 1: Complete the Models (`models.py`)

Implement the following classes:

1. `Question` – Represents a single quiz question.
2. `QuestionDataset` – Singleton to load JSON quiz data once.
3. `QuizGenerator` – Generates a random quiz filtered by tags.
4. `QuizCorrector` – Evaluates answers and calculates scores.

---

### Step 2: Complete the Streamlit App (`app.py`)

1. Import the models.
2. Implement a `QuizView` class to handle all Streamlit rendering and interactions:

   * Field selection for quiz generation.
   * Display questions dynamically:

     * **Single choice:** radio buttons
     * **Multiple choice:** multiselect
   * Submit & correct quiz.
   * Reset quiz functionality.
3. Use `st.session_state` to persist questions and answers.

---

### Step 3: Scoring Logic

* **Single choice:** 1 point if correct, 0 if wrong.
* **Multiple choice:** proportional score based on correct/incorrect selections:

$$
\text{score} = \max\left(0, \frac{|correct \cap selected|}{|correct|} - \frac{|selected - correct|}{|correct|}\right)
$$

---

### Step 4: Optional Enhancements

* Highlight correct/incorrect answers with colors.
* Show **per-question scores** and **total score** using charts (`matplotlib` or `seaborn`).
* Track **quiz history** in session state.
* Add hints or explanations for questions.

---

## 🎯 Deliverables

* `models.py` → Fully implemented classes.
* `app.py` → Working Streamlit app.
* Screenshots of the running app with charts.

---

## ✅ Evaluation Criteria

| Criteria                | Points    |
| ----------------------- | ----------|
| OOP Implementation      | 30        |
| Quiz Generation Logic   | 15        |
| Scoring Correctness     | 15        |
| Streamlit UI            | 20        |
| Optional Visualizations | 20        |
| **Total**               | 100       |

---

## ⏳ Submission

* Submit a **zip file** containing `models.py`, `app.py`, `classes.pdf` of Classes Diagram (UML or Visio) and `Readme-Solution.md` with screenshot (explain the logic how it works and illustrate it with images).
* **If you changed the requirments add the new requirments file to the zip file**
* **Deadline:** 2025-10-26
* **Late submissions:** -10% (2pts) per day.

---

## ⚡ Getting Started

1. Install requirements:

```bash
pip install -r requirements.txt
```

2. Run the app:

```bash
streamlit run app.py
#OR
python -m streamlit run app.py
```


3. Select fields and generate your quiz.
4. Answer the questions and submit to see your score!






