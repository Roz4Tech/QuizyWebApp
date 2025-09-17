import os
import random
import time
from datetime import timedelta
from flask import Flask, render_template, request, redirect, url_for, session, abort, flash
from flask_wtf.csrf import CSRFProtect
from functools import wraps
from quiz import Quiz, Question

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-key-for-testing-only')
app.permanent_session_lifetime = timedelta(hours=1)  # Session expires after 1 hour

# Enable CSRF protection
csrf = CSRFProtect(app)

# Rate limiting decorator
def rate_limit(limit=10, per=60):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'last_request' in session:
                time_since = time.time() - session['last_request']
                if time_since < per and session.get('request_count', 0) >= limit:
                    abort(429)  # Too Many Requests
                elif time_since >= per:
                    session['request_count'] = 0
            
            session['last_request'] = time.time()
            session['request_count'] = session.get('request_count', 0) + 1
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def create_quiz():
    """Initialize and return a Quiz instance with questions."""
    quiz = Quiz()
    questions = [
        ("Who is the fastest runner?", ["Yohan Blake", "Asafa Powell", "Usain Bolt"], 2),
        ("Ghana was first called?", ["Salaga", "Gold Coast", "Shinning Coast"], 1),
        ("What is 2 + 2?", ["3", "4", "5"], 1),
        ("What is the capital of France?", ["London", "Paris", "Berlin"], 1),
        ("Which planet is known as the Red Planet?", ["Venus", "Mars", "Jupiter"], 1),
        ("Who painted the Mona Lisa?", ["Leonardo da Vinci", "Pablo Picasso", "Vincent van Gogh"], 0),
        ("What is the largest ocean on Earth?", ["Atlantic Ocean", "Indian Ocean", "Pacific Ocean"], 2),
        ("In which year did the Titanic sink?", ["1912", "1920", "1898"], 0),
        ("Which country is famous for the Great Wall?", ["India", "China", "Japan"], 1),
        ("Who wrote 'Romeo and Juliet'?", ["William Shakespeare", "Charles Dickens", "Jane Austen"], 0),
        ("What is the chemical symbol for gold?", ["Ag", "Au", "Gd"], 1),
        ("Which continent is the Sahara Desert located in?", ["Asia", "Africa", "Australia"], 1),
        ("What is the tallest mountain in the world?", ["K2", "Mount Everest", "Kilimanjaro"], 1),
        ("Which animal is known as the King of the Jungle?", ["Tiger", "Lion", "Elephant"], 1),
        ("How many players are there in a football (soccer) team on the field?", ["9", "10", "11"], 2),
        ("What is the boiling point of water at sea level?", ["90°C", "100°C", "120°C"], 1),
        ("Who was the first man to walk on the Moon?", ["Neil Armstrong", "Buzz Aldrin", "Yuri Gagarin"], 0),
        ("Which is the smallest country in the world?", ["Vatican City", "Monaco", "Malta"], 0),
        ("Which language has the most native speakers?", ["English", "Mandarin Chinese", "Spanish"], 1),
        ("What is the national currency of Japan?", ["Yuan", "Yen", "Won"], 1),
        ("Which organ in the human body pumps blood?", ["Liver", "Lungs", "Heart"], 2),
        ("Which country hosted the 2016 Summer Olympics?", ["China", "Brazil", "Russia"], 1),
        ("What gas do humans need to breathe to survive?", ["Carbon Dioxide", "Oxygen", "Nitrogen"], 1),
        ("Which symbol is used to write comments in Python?", ["//", "#", "/* */"], 1),
        ("Which data type is used to store True or False values in Python?", ["int", "bool", "str"], 1),
        ("Which of these is a loop in Python?", ["for", "if", "print"], 0),
        ("What is the correct file extension for Python files?", [".py", ".java", ".cpp"], 0),
        ("Which function is used to display output in Python?", ["print()", "echo()", "show()"], 0),
        ("Which keyword is used to define a function in Python?", ["function", "def", "fun"], 1),
        ("What symbol is used for multiplication in Python?", ["*", "x", "%"], 0),
        ("Which of these is used to create a list in Python?", ["{}", "[]", "()"], 1),
        ("What is the index of the first element in a Python list?", ["0", "1", "-1"], 0)
    ]
    
    for text, options, correct in questions:
        quiz.add_question(Question(text, options, correct))
    
    return quiz

quiz = create_quiz()


@app.route("/")
def index():
    session["current_question"] = 0
    session["score"] = 0
    session["user_answers"] = {}

    # randomly pick 20 questions from all
    selected = random.sample(range(len(quiz.questions)), 20)
    session["selected"] = selected

    return redirect(url_for("quiz_view"))


@app.route("/quiz", methods=["GET", "POST"])
def quiz_view():
    current_question_index = session.get("current_question", 0)
    selected = session.get("selected", [])

    # stop after 20
    if current_question_index >= len(selected):
        return redirect(url_for("results"))

    if request.method == "POST":
        selected_option = request.form.get("option")
        if selected_option is not None:
            question_index = selected[current_question_index]
            correct_option = quiz.questions[question_index].correct_option
            # Store the user's answer
            if "user_answers" not in session:
                session["user_answers"] = {}
            session["user_answers"][str(question_index)] = int(selected_option)
            # Update score if answer is correct
            if int(selected_option) == correct_option:
                session["score"] += 1
        session["current_question"] += 1

        return redirect(url_for("quiz_view"))

    else:
        question_index = selected[current_question_index]
        question = quiz.questions[question_index]

        return render_template(
            "quiz.html",
            question=question,
            question_index=session["current_question"] + 1,
            total_questions=len(selected)
        )


@app.route("/results")
def results():
    if 'selected' not in session:
        flash('No quiz session found. Please start a new quiz.', 'error')
        return redirect(url_for('index'))
    
    score = session.get("score", 0)
    total = len(session.get("selected", []))
    return render_template("results.html", score=score, total=total)


@app.route("/solutions")
@rate_limit()
def solutions():
    """Display the solutions page with user's answers and correct answers for all 20 quiz questions."""
    if 'selected' not in session:
        flash('No quiz session found. Please start a new quiz.', 'error')
        return redirect(url_for('index'))
    
    try:
        selected_indices = session["selected"]
        if not isinstance(selected_indices, list) or not all(isinstance(i, int) for i in selected_indices):
            raise ValueError("Invalid session data")
        
        # Ensure we have exactly 20 questions (as set in the quiz initialization)
        if len(selected_indices) != 20:
            app.logger.warning(f"Expected 20 questions, got {len(selected_indices)}")
            
        # Get all 20 questions with their original indices
        questions_with_indices = []
        for i in selected_indices:
            if not 0 <= i < len(quiz.questions):
                continue
            questions_with_indices.append((i, quiz.questions[i]))
            
        user_answers = session.get("user_answers", {})
        if not isinstance(user_answers, dict):
            user_answers = {}
        
        # Get score and total for the template (should be 20)
        score = session.get("score", 0)
        total_questions = len(selected_indices)
            
        return render_template(
            "solution.html",
            questions_with_indices=questions_with_indices,
            user_answers=user_answers,
            score=score,
            total_questions=total_questions
        )
        
    except Exception as e:
        app.logger.error(f"Error in solutions route: {str(e)}")
        flash('An error occurred while loading the solutions. Please try again.', 'error')
        return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)