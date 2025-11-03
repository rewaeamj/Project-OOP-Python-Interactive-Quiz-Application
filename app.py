import streamlit as st
import matplotlib.pyplot as plt
from models import QuestionDataset, QuizGenerator, QuizCorrector

class QuizView:
    """
    Handles all Streamlit rendering and user interactions.
    """
    def __init__(self, dataset):
        self.dataset = dataset
        self.all_tags = dataset.get_all_tags()
        
        if 'quiz_generated' not in st.session_state:
            st.session_state.quiz_generated = False
        if 'questions' not in st.session_state:
            st.session_state.questions = []
        if 'user_answers' not in st.session_state:
            st.session_state.user_answers = {}
        if 'quiz_corrected' not in st.session_state:
            st.session_state.quiz_corrected = False
        if 'correction_results' not in st.session_state:
            st.session_state.correction_results = None
        if 'num_questions' not in st.session_state:
            st.session_state.num_questions = 10

    def reset_quiz(self):
        """Reset the quiz state"""
        st.session_state.quiz_generated = False
        st.session_state.questions = []
        st.session_state.user_answers = {}
        st.session_state.quiz_corrected = False
        st.session_state.correction_results = None
        st.success("Quiz reset successfully!")
        st.rerun()

    def select_fields(self):
        """Display field selection UI and return selected fields"""
        st.sidebar.markdown("### Quiz Configuration")
        st.sidebar.markdown("---")
        
        # Multi-select for tags
        st.sidebar.markdown("**Choose tags:**")
        selected_tags = st.sidebar.multiselect(
            "Select tags",
            options=self.all_tags,
            default=None,
            label_visibility="collapsed",
            help="Select one or more tags"
        )
        
        if selected_tags:
            st.sidebar.success(f"Selected: {', '.join(selected_tags)}")
        
        st.sidebar.markdown("")

        # Number of questions
        st.sidebar.markdown("""Number of Questions""")

        col1, col2, col3 = st.sidebar.columns([1, 2, 1])

        with col1:
            if st.button("➖", key="minus", use_container_width=True):
                if st.session_state.num_questions > 5:
                    st.session_state.num_questions -= 5
                    st.rerun()

        with col2:
            st.markdown(
                f"""
                <div style="
                    text-align:center;
                    font-size:22px;
                    font-weight:600;
                    padding:6px;
                    background-color:#f0f2f6;
                    border-radius:8px;
                    margin-top:4px;">
                    {st.session_state.num_questions}
                </div>
                """,
                unsafe_allow_html=True
            )

        with col3:
            if st.button("➕", key="plus", use_container_width=True):
                if st.session_state.num_questions < 50:
                    st.session_state.num_questions += 5
                    st.rerun()

        return selected_tags, st.session_state.num_questions


    def generate_quiz(self, selected_tags, num_questions):
        """Generate a new quiz based on selected criteria"""
        generator = QuizGenerator(self.dataset)
        questions = generator.generate_quiz(selected_tags, num_questions)
        
        if len(questions) == 0:
            st.error("No questions found for selected topics.")
            return
        
        # Store generated questions and reset previous answers
        st.session_state.questions = questions
        st.session_state.user_answers = {}
        st.session_state.quiz_generated = True
        st.session_state.quiz_corrected = False
        st.session_state.correction_results = None
        
        st.success(f"Quiz generated with {len(questions)} questions!")
        st.rerun()

    def show_quiz(self):
        """Display quiz questions and collect answers"""
        if not st.session_state.quiz_generated or len(st.session_state.questions) == 0:
            st.info("Please generate a quiz using the sidebar.")
            return
        
        st.header("Quiz Questions")
        st.markdown("---")
        
        for idx, question in enumerate(st.session_state.questions):
            with st.container():
                st.markdown(f"### Question {idx + 1}")
                st.markdown(f"**{question.question}**")
                
                # Display tags and question mode (single/multiple choice)
                col1, col2 = st.columns([4, 1])
                with col1:
                    tags_badges = " ".join([f"<span style='background-color: #2196F3; color: white; padding: 5px 12px; border-radius: 15px; font-size: 12px; margin-right: 5px; display: inline-block; font-weight: 600;'>{tag}</span>" for tag in question.tags])
                    st.markdown(tags_badges, unsafe_allow_html=True)
                
                with col2:
                    mode_color = "#4CAF50" if question.mode == "single" else "#FF9800"
                    mode_text = "Single" if question.mode == "single" else "Multiple"
                    st.markdown(f"<div style='text-align: right;'><span style='background-color: {mode_color}; color: white; padding: 5px 12px; border-radius: 15px; font-size: 11px; font-weight: 600;'>{mode_text}</span></div>", 
                               unsafe_allow_html=True)
                
                st.markdown("")

                # Show correct/incorrect if quiz has been corrected
                if st.session_state.quiz_corrected:
                    result = st.session_state.correction_results['results'][idx]
                    
                    if result['is_correct']:
                        st.success(f"Correct! Score: {result['score']:.2f}")
                    else:
                        st.markdown(f"""
                        <div style='padding: 12px; background-color: #ffebee; border-left: 5px solid #f44336; border-radius: 5px; margin: 10px 0;'>
                            <strong style='color: #d32f2f; font-size: 15px;'>Incorrect - Score: {result['score']:.2f}</strong>
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown(f"""
                        <div style='padding: 10px; background-color: #e3f2fd; border-left: 4px solid #2196F3; border-radius: 5px; margin: 10px 0;'>
                            <strong style='color: #1976d2;'>Correct answer: {', '.join(result['correct_answers'])}</strong>
                        </div>
                        """, unsafe_allow_html=True)
                                
                # the input option : radio for single choice, multiselect for multiple choice
                if question.mode == 'single':
                    st.markdown("<div style='font-weight:600; margin-bottom:6px;'>Your answer:</div>", unsafe_allow_html=True)
                    
                    default_value = st.session_state.user_answers.get(idx, None)
                    
                    if default_value and default_value in question.choices:
                        default_index = question.choices.index(default_value)
                        answer = st.radio(
                            "options",
                            options=question.choices,
                            index=default_index,
                            key=f"q_{idx}",
                            disabled=st.session_state.quiz_corrected,
                            label_visibility="collapsed"
                        )
                    else:
                        answer = st.radio(
                            "options",
                            options=question.choices,
                            key=f"q_{idx}",
                            disabled=st.session_state.quiz_corrected,
                            label_visibility="collapsed"
                        )
                    
                    st.session_state.user_answers[idx] = answer

                else:
                    st.markdown("<div style='font-weight:600; margin-bottom:6px;'>Your answers:</div>", unsafe_allow_html=True)

                    default_values = st.session_state.user_answers.get(idx, [])

                    answers = st.multiselect(
                        "Choose options",
                        options=question.choices,
                        default=default_values,
                        key=f"q_{idx}",
                        placeholder="Choose options",
                        disabled=st.session_state.quiz_corrected,
                        label_visibility="collapsed"
                    )

                    st.session_state.user_answers[idx] = answers


    def submit_and_correct(self):
        """Submit quiz and show results"""
        if not st.session_state.quiz_generated:
            st.warning("Please generate a quiz first!")
            return
        
        if st.session_state.quiz_corrected:
            st.info("Quiz already corrected. Reset to try again.")
            return
        
        corrector = QuizCorrector()
        results = corrector.correct_quiz(
            st.session_state.questions,
            st.session_state.user_answers
        )
        
        st.session_state.correction_results = results
        st.session_state.quiz_corrected = True
        
        self.show_results(results)
        st.rerun()

    def show_results(self, results):
        """Display quiz results with visualizations"""
        st.header("Quiz Results")
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div style='text-align: center; padding: 25px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                <h3 style='margin: 0; font-size: 16px; color: white;'>Total Score</h3>
                <h1 style='margin: 10px 0 0 0; font-size: 40px; color: white;'>{results['total_score']:.1f}/{results['max_score']}</h1>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            percentage = results['percentage']
            color1 = "#4CAF50" if percentage >= 70 else "#FF9800" if percentage >= 50 else "#F44336"
            
            st.markdown(f"""
            <div style='text-align: center; padding: 25px; background: {color1}; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                <h3 style='margin: 0; font-size: 16px; color: white;'>Percentage</h3>
                <h1 style='margin: 10px 0 0 0; font-size: 40px; color: white;'>{percentage:.1f}%</h1>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            correct_count = sum(1 for r in results['results'] if r['is_correct'])
            st.markdown(f"""
            <div style='text-align: center; padding: 25px; background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                <h3 style='margin: 0; font-size: 16px; color: white;'>Correct</h3>
                <h1 style='margin: 10px 0 0 0; font-size: 40px; color: white;'>{correct_count}/{results['max_score']}</h1>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        
        st.subheader("Performance Analysis")
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        fig.patch.set_facecolor('white')
        
        scores = [r['score'] for r in results['results']]
        question_nums = [f"Q{i+1}" for i in range(len(scores))]
        
        colors = ['#4CAF50' if s == 1.0 else '#FF9800' if s > 0 else '#F44336' for s in scores]
        bars = ax1.bar(question_nums, scores, color=colors, alpha=0.85, edgecolor='black', linewidth=1.5)
        
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                    f'{height:.2f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        ax1.set_xlabel('Question', fontsize=13, fontweight='bold')
        ax1.set_ylabel('Score', fontsize=13, fontweight='bold')
        ax1.set_title('Score per Question', fontsize=15, fontweight='bold', pad=15)
        ax1.set_ylim(0, 1.2)
        ax1.axhline(y=1.0, color='#4CAF50', linestyle='--', alpha=0.6, linewidth=2)
        ax1.tick_params(axis='x', rotation=45)
        ax1.grid(axis='y', alpha=0.3, linestyle='--')
        ax1.set_facecolor('#fafafa')
        
        correct = sum(1 for r in results['results'] if r['is_correct'])
        partial = sum(1 for r in results['results'] if 0 < r['score'] < 1.0)
        incorrect = sum(1 for r in results['results'] if r['score'] == 0)
        
        pie_data = [correct, partial, incorrect]
        pie_labels = [f'Correct\n({correct})', f'Partial\n({partial})', f'Incorrect\n({incorrect})']
        pie_colors = ['#4CAF50', '#FF9800', '#F44336']
        
        wedges, texts, autotexts = ax2.pie(pie_data, labels=pie_labels, colors=pie_colors, 
                                            autopct='%1.1f%%', startangle=90,
                                            textprops={'fontsize': 12, 'fontweight': 'bold'},
                                            shadow=True)
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(13)
        
        ax2.set_title('Answer Distribution', fontsize=15, fontweight='bold', pad=15)
        
        plt.tight_layout()
        st.pyplot(fig)
        
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("Detailed Breakdown", expanded=False):
            for idx, result in enumerate(results['results']):
                color = "#4CAF50" if result['is_correct'] else "#F44336"
                bg = "#e8f5e9" if result['is_correct'] else "#ffebee"
                
                st.markdown(f"""
                <div style='padding: 15px; margin: 12px 0; border-left: 5px solid {color}; background-color: {bg}; border-radius: 8px;'>
                    <p style='margin: 8px 0; color: #000;'><strong>{result['question']}</strong></p>
                    <p style='margin: 5px 0; color: #333;'><strong>Mode:</strong> {result['mode']}</p>
                    <p style='margin: 5px 0; color: #333;'><strong>Your answer:</strong> {result['user_answer']}</p>
                    <p style='margin: 5px 0; color: #333;'><strong>Correct:</strong> {', '.join(result['correct_answers'])}</p>
                    <p style='margin: 8px 0 0 0; color: {color};'><strong>Score: {result['score']:.2f}/1.00</strong></p>
                </div>
                """, unsafe_allow_html=True)


st.set_page_config(
    page_title="Quiz Generator", 
    layout="wide",
    initial_sidebar_state="expanded"
)

try:
    import streamlit.components.v1 as components
    components.html(
        """
        <script>
        const doc = window.parent.document;
        doc.body.style.backgroundColor = 'white';
        const stApp = doc.querySelector('.stApp');
        if (stApp) stApp.style.backgroundColor = 'white';
        </script>
        """,
        height=0,
    )
except:
    pass

st.markdown("""
<style>
    @media (prefers-color-scheme: dark) {
        :root {
            color-scheme: light !important;
        }
    }
    
    :root, html, body {
        background-color: #ffffff !important;
    }
    
    .stApp {
        background-color: #ffffff !important;
        background: #ffffff !important;
    }
    
    .main {
        background-color: #ffffff !important;
        background: #ffffff !important;
    }
    
    .block-container {
        background-color: #ffffff !important;
        background: #ffffff !important;
    }
    
    div:not([class*="gradient"]) {
        background-color: transparent !important;
    }
    
    [data-testid="stSidebar"], 
    [data-testid="stSidebar"] > div,
    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"] > div {
        background-color: #ffffff !important;
        background: #ffffff !important;
    }
    
    header, [data-testid="stHeader"] {
        background-color: #ffffff !important;
        background: #ffffff !important;
    }
    
    [class*="css-"], 
    [data-testid*="column"],
    [data-testid*="block"],
    .element-container,
    .stMarkdown,
    section {
        background-color: transparent !important;
    }
    
    body, .main, p, span, div, label {
        color: #000000 !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #000000 !important;
    }
    
    [data-baseweb="select"] {
        background-color: #ffffff !important;
    }
    
    [data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    .stMultiSelect [data-baseweb="tag"] {
        background-color: #2196F3 !important;
        color: white !important;
        font-weight: 600;
    }
    
    [role="listbox"], [role="option"] {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    .stButton>button {
        border-radius: 10px;
        font-weight: 600;
        background-color: #f0f2f6 !important;
        color: #000000 !important;
        border: 2px solid #e0e0e0 !important;
    }
    
    .stButton>button:hover {
        background-color: #e0e0e0 !important;
    }
    
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
    }
    
    input, textarea, select {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #e0e0e0 !important;
    }
    
    .stRadio > label, 
    .stCheckbox > label {
        color: #000000 !important;
    }
    
    /* Style pour les options radio - effet de sélection */
    .stRadio > div[role="radiogroup"] > label {
        padding: 10px 15px;
        margin: 5px 0;
        border-radius: 8px;
        border: 2px solid #e0e0e0;
        background-color: #ffffff;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .stRadio > div[role="radiogroup"] > label:hover {
        border-color: #2196F3;
        background-color: #f0f8ff;
    }
    
    /* Style pour l'option sélectionnée */
    .stRadio > div[role="radiogroup"] > label[data-checked="true"] {
        border-color: #2196F3;
        background-color: #e3f2fd;
        font-weight: 600;
    }
    
    .stRadio input[type="radio"]:checked + div {
        background-color: #e3f2fd !important;
        border-color: #2196F3 !important;
    }
    
    .stCaption, 
    [data-testid="stCaptionContainer"] {
        color: #666666 !important;
    }
    
    .stAlert {
        background-color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #000000 !important;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p {
        color: #000000 !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style='text-align: center; padding: 30px 0; 
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            color: white; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);'>
    <h1 style='font-size: 44px; font-weight: 800; margin-bottom: 0;'>Quiz Generator</h1>
</div>
""", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

try:
    dataset = QuestionDataset("quiz_dataset.json")
    quiz_view = QuizView(dataset)
    
    selected_tags, num_questions = quiz_view.select_fields()
    
    st.sidebar.markdown("---")
    
    if st.sidebar.button("Generate Quiz", type="primary", use_container_width=True):
        quiz_view.generate_quiz(selected_tags, num_questions)
    
    if st.sidebar.button("Reset Quiz", use_container_width=True):
        quiz_view.reset_quiz()
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        quiz_view.show_quiz()
    
    with col2:
        if st.session_state.quiz_generated:
            status = "Corrected" if st.session_state.quiz_corrected else "In Progress"
            color = "#4CAF50" if st.session_state.quiz_corrected else "#FF9800"
            
            st.markdown(f"""
            <div style='padding: 20px; background-color: white; border-radius: 12px; border: 3px solid {color}; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                <h3 style='margin: 0 0 15px 0; color: {color};'>Quiz Info</h3>
                <p style='margin: 8px 0; color: #000;'><strong>Questions:</strong> {len(st.session_state.questions)}</p>
            </div>
            """, unsafe_allow_html=True)
    
    if st.session_state.quiz_generated and not st.session_state.quiz_corrected:
        st.markdown("---")
        if st.button("Submit & Correct Quiz", type="primary", use_container_width=True):
            quiz_view.submit_and_correct()
    
    if st.session_state.quiz_corrected and st.session_state.correction_results:
        st.markdown("---")
        quiz_view.show_results(st.session_state.correction_results)

except FileNotFoundError as e:
    st.error(f"Error: {str(e)}")
except Exception as e:
    st.error(f"Error: {str(e)}")
    st.exception(e)