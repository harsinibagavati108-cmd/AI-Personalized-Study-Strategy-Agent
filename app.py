"""
Flask Web Application for AI-Based Personalized Study Strategy Agent.
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify

import secrets
from agent import StudyAgent

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Default sample topics for instant demonstration
DEFAULT_TOPICS = [
    {
        'id': 1,
        'subject': 'Mathematics',
        'name': 'Probability & Statistics',
        'difficulty': 5,
        'understanding': 2,
        'exam_days': 3,
        'importance': 5,
        'progress': 10
    },
    {
        'id': 2,
        'subject': 'Computer Science',
        'name': 'Data Structures & Algorithms',
        'difficulty': 4,
        'understanding': 3,
        'exam_days': 5,
        'importance': 5,
        'progress': 25
    },
    {
        'id': 3,
        'subject': 'Programming',
        'name': 'Python & OOP Concepts',
        'difficulty': 3,
        'understanding': 4,
        'exam_days': 10,
        'importance': 4,
        'progress': 60
    },
    {
        'id': 4,
        'subject': 'Systems',
        'name': 'Operating Systems & Memory',
        'difficulty': 4,
        'understanding': 2,
        'exam_days': 8,
        'importance': 3,
        'progress': 0
    }
]


@app.route('/')
def index():
    """Home Page: Title, Problem Statement, Intelligent Agent Overview."""
    return render_template('index.html')


@app.route('/input', methods=['GET'])
def input_page():
    """Student Input Page: Add/edit topics and available study hours."""
    # Prefill with session topics or default sample
    topics = session.get('topics', DEFAULT_TOPICS)
    available_hours = session.get('available_hours', 3.0)
    return render_template('input.html', topics=topics, available_hours=available_hours)


@app.route('/plan', methods=['POST'])
def generate_plan():
    """Process topic input and trigger Agent decision-making."""
    try:
        available_hours = float(request.form.get('available_hours', 2.0))
    except ValueError:
        available_hours = 2.0

    # Extract dynamic list of topics from form
    subjects = request.form.getlist('subject[]')
    names = request.form.getlist('name[]')
    difficulties = request.form.getlist('difficulty[]')
    understandings = request.form.getlist('understanding[]')
    exam_days_list = request.form.getlist('exam_days[]')
    importances = request.form.getlist('importance[]')

    topics = []
    for i in range(len(names)):
        if not names[i].strip():
            continue
        topics.append({
            'id': i + 1,
            'subject': subjects[i] if i < len(subjects) else 'General',
            'name': names[i],
            'difficulty': int(difficulties[i]) if i < len(difficulties) else 3,
            'understanding': int(understandings[i]) if i < len(understandings) else 3,
            'exam_days': int(exam_days_list[i]) if i < len(exam_days_list) else 7,
            'importance': int(importances[i]) if i < len(importances) else 3,
            'progress': 0
        })

    if not topics:
        topics = DEFAULT_TOPICS

    agent = StudyAgent()
    strategy = agent.generate_strategy(topics, available_hours)

    # Store state in session
    session['topics'] = topics
    session['available_hours'] = available_hours
    session['current_plan'] = strategy['plan']
    session['is_replanned'] = False

    return redirect(url_for('recommendation'))


@app.route('/preset')
def load_preset():
    """Load default preset topics for quick demonstration."""
    agent = StudyAgent()
    available_hours = 3.0
    strategy = agent.generate_strategy(DEFAULT_TOPICS, available_hours)

    session['topics'] = DEFAULT_TOPICS
    session['available_hours'] = available_hours
    session['current_plan'] = strategy['plan']
    session['is_replanned'] = False

    return redirect(url_for('recommendation'))


@app.route('/recommendation')
def recommendation():
    """Display generated AI Study Strategy recommendation."""
    current_plan = session.get('current_plan', [])
    available_hours = session.get('available_hours', 2.0)
    is_replanned = session.get('is_replanned', False)

    if not current_plan:
        return redirect(url_for('input_page'))

    total_minutes = int(available_hours * 60)

    return render_template(
        'recommendation.html',
        plan=current_plan,
        available_hours=available_hours,
        total_minutes=total_minutes,
        is_replanned=is_replanned
    )


@app.route('/feedback', methods=['GET'])
def feedback_page():
    """Feedback & Replanning Interface."""
    current_plan = session.get('current_plan', [])
    available_hours = session.get('available_hours', 2.0)

    if not current_plan:
        return redirect(url_for('input_page'))

    return render_template('feedback.html', plan=current_plan, available_hours=available_hours)


@app.route('/replan', methods=['POST'])
def execute_replan():
    """Process feedback, trigger Agent dynamic replanning, and render updated state."""
    try:
        new_available_hours = float(request.form.get('available_hours', session.get('available_hours', 2.0)))
    except ValueError:
        new_available_hours = session.get('available_hours', 2.0)

    current_plan = session.get('current_plan', [])
    updated_topics = []

    for item in current_plan:
        topic_id = str(item['id'])
        
        # Read feedback updates
        new_understanding = request.form.get(f'understanding_{topic_id}')
        new_progress = request.form.get(f'progress_{topic_id}')
        new_exam_days = request.form.get(f'exam_days_{topic_id}')

        updated_topic = {
            'id': item['id'],
            'subject': item['subject'],
            'name': item['name'],
            'difficulty': item['difficulty'],
            'understanding': int(new_understanding) if new_understanding else item['understanding'],
            'exam_days': int(new_exam_days) if new_exam_days else item['exam_days'],
            'importance': item['importance'],
            'progress': int(new_progress) if new_progress else item.get('progress', 0)
        }
        updated_topics.append(updated_topic)

    agent = StudyAgent()
    replan_result = agent.replan(updated_topics, new_available_hours, previous_plan=current_plan)

    new_plan = replan_result['strategy']['plan']

    # Update session state
    session['topics'] = updated_topics
    session['available_hours'] = new_available_hours
    session['previous_plan'] = current_plan
    session['current_plan'] = new_plan
    session['is_replanned'] = True

    return redirect(url_for('recommendation'))


if __name__ == '__main__':
    app.run(debug=True, port=5000)
