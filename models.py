import json
import random

class Question:
    """
    Represents a single quiz question.
    - question: The question text.
    - choices: List of possible answers.
    - correct: List of correct answers.
    - mode: 'single' or 'multiple'.
    - tags: List of fields/tags for filtering.
    """
    def __init__(self, question, choices, correct, mode, tags):
        self.question = question
        self.choices = choices
        self.correct = correct
        self.mode = mode
        self.tags = tags
    
    def __repr__(self):
        return f"Question(mode={self.mode}, tags={self.tags})"


class QuestionDataset:
    """
    Singleton class to load quiz questions from a JSON file.
    - Loads all questions as Question objects.
    - Provides a method to get all unique tags for filtering.
    """
    _instance = None
    
    def __new__(cls, filepath=None):
        if cls._instance is None:
            cls._instance = super(QuestionDataset, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, filepath=None):
        if self._initialized:
            return
        
        if filepath is None:
            raise ValueError("Filepath must be provided on first initialization")
        
        self.filepath = filepath
        self.questions = []
        self._load_questions()
        self._initialized = True
    
    def _load_questions(self):
        """Load questions from JSON file"""
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for item in data:
                question = Question(
                    question=item['question'],
                    choices=item['choices'],
                    correct=item['correct'],
                    mode=item['mode'],
                    tags=item['tags']
                )
                self.questions.append(question)
        except FileNotFoundError:
            raise FileNotFoundError(f"Quiz dataset file not found: {self.filepath}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON format in file: {self.filepath}")
    
    def get_all_tags(self):
        """Get all unique tags from all questions"""
        tags = set()
        for question in self.questions:
            tags.update(question.tags)
        return sorted(list(tags))
    
    def get_questions(self):
        """Return all questions"""
        return self.questions


class QuizGenerator:
    """
    Generates a quiz from a dataset filtered by fields/tags.
    """
    def __init__(self, dataset):
        self.dataset = dataset
    
    def generate_quiz(self, selected_tags=None, num_questions=10):
        """
        Generate a quiz with questions filtered by tags.
        
        Args:
            selected_tags: List of tags to filter questions
            num_questions: Number of questions to include in quiz
        
        Returns:
            List of Question objects
        """
        all_questions = self.dataset.get_questions()
        
        if selected_tags and len(selected_tags) > 0:
            filtered_questions = [
                q for q in all_questions 
                if any(tag in q.tags for tag in selected_tags)
            ]
        else:
            filtered_questions = all_questions
        
        if len(filtered_questions) <= num_questions:
            return random.sample(filtered_questions, len(filtered_questions))
        
        return random.sample(filtered_questions, num_questions)


class QuizCorrector:
    """
    Corrects a quiz and calculates scores.
    """
    @staticmethod
    def correct_quiz(questions, user_answers):
        """
        Correct quiz and calculate scores.
        
        Args:
            questions: List of Question objects
            user_answers: Dict mapping question index to user's answer(s)
        
        Returns:
            Dict containing scores, total_score, and detailed results
        """
        results = []
        total_score = 0
        max_score = len(questions)
        
        for idx, question in enumerate(questions):
            user_answer = user_answers.get(idx, None)
            
            if question.mode == 'single':
                score = QuizCorrector._score_single_choice(
                    question.correct, user_answer
                )
            else:  
                score = QuizCorrector._score_multiple_choice(
                    question.correct, user_answer
                )
            
            total_score += score
            
            result = {
                'question': question.question,
                'mode': question.mode,
                'correct_answers': question.correct,
                'user_answer': user_answer,
                'score': score,
                'is_correct': score == 1.0
            }
            results.append(result)
        
        return {
            'results': results,
            'total_score': total_score,
            'max_score': max_score,
            'percentage': (total_score / max_score * 100) if max_score > 0 else 0
        }
    
    @staticmethod
    def _score_single_choice(correct_answers, user_answer):
        """
        Score a single choice question.
        Returns 1 if correct, 0 if wrong.
        """
        if user_answer is None:
            return 0
        
        return 1 if user_answer in correct_answers else 0
    
    @staticmethod
    def _score_multiple_choice(correct_answers, user_answers):
        """
        Score a multiple choice question using proportional scoring.
        
        Formula: max(0, |correct ∩ selected| / |correct| - |selected - correct| / |correct|)
        """
        if user_answers is None or len(user_answers) == 0:
            return 0
        
        correct_set = set(correct_answers)
        selected_set = set(user_answers)
        
        correct_selected = len(correct_set.intersection(selected_set))
        wrong_selected = len(selected_set - correct_set)
        
        score = correct_selected / len(correct_set) - wrong_selected / len(correct_set)
        
        return max(0, score)