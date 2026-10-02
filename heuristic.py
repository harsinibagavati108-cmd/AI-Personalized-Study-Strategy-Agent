"""
Heuristic Evaluation Engine for Personalized Study Strategy Agent.

Priority Score Formula:
    Priority Score = 0.35 * Weakness + 0.30 * Exam Urgency + 0.20 * Difficulty + 0.15 * Importance

Factors are normalized to the range [0.0, 1.0].
- Weakness: Derived as (6 - Understanding), normalized from 1..5 to 0.0..1.0
- Exam Urgency: Normalized inverse of exam days remaining
- Difficulty: Normalized from 1..5 to 0.0..1.0
- Importance: Normalized from 1..5 to 0.0..1.0
"""

def normalize_scale(val, min_val=1, max_val=5):
    """Normalize a value on a 1-5 scale to [0.0, 1.0]."""
    val = float(val)
    if max_val == min_val:
        return 1.0
    return max(0.0, min(1.0, (val - min_val) / (max_val - min_val)))


def calculate_exam_urgency(days):
    """
    Calculate exam urgency score between 0.0 and 1.0.
    1 day or less -> 1.0 (Maximum urgency)
    30 days or more -> ~0.05 (Low urgency)
    """
    days = float(days)
    if days <= 1:
        return 1.0
    # Non-linear decay function: urgency drops as exam date is further away
    urgency = 1.0 / (1.0 + 0.12 * (days - 1))
    return max(0.0, min(1.0, urgency))


def evaluate_topic_heuristic(topic):
    """
    Evaluate heuristic priority score and return detailed breakdowns for a topic dictionary.
    
    Topic dict format:
    {
        'id': str/int,
        'subject': str,
        'name': str,
        'difficulty': int (1-5),
        'understanding': int (1-5),
        'exam_days': int,
        'importance': int (1-5),
        'progress': int (0-100, optional)
    }
    """
    difficulty = int(topic.get('difficulty', 3))
    understanding = int(topic.get('understanding', 3))
    exam_days = int(topic.get('exam_days', 7))
    importance = int(topic.get('importance', 3))
    progress = int(topic.get('progress', 0))

    # Weakness calculation: Weakness = 6 - Understanding (Range 1 to 5)
    raw_weakness = 6 - understanding
    weakness_norm = normalize_scale(raw_weakness, 1, 5)

    # If progress has been made (e.g. 50%), weakness is reduced proportionally
    progress_factor = max(0.0, 1.0 - (progress / 100.0))
    effective_weakness_norm = weakness_norm * progress_factor

    # Exam urgency score
    urgency_norm = calculate_exam_urgency(exam_days)

    # Difficulty & Importance score
    difficulty_norm = normalize_scale(difficulty, 1, 5)
    importance_norm = normalize_scale(importance, 1, 5)

    # Composite Heuristic Formula
    weight_weakness = 0.35
    weight_urgency = 0.30
    weight_difficulty = 0.20
    weight_importance = 0.15

    raw_score = (
        weight_weakness * effective_weakness_norm +
        weight_urgency * urgency_norm +
        weight_difficulty * difficulty_norm +
        weight_importance * importance_norm
    )

    score_percentage = round(raw_score * 100, 1)

    # Categorize Priority Level
    if score_percentage >= 70:
        priority_level = 'HIGH'
        badge_class = 'danger'
    elif score_percentage >= 45:
        priority_level = 'MEDIUM'
        badge_class = 'warning'
    else:
        priority_level = 'LOW'
        badge_class = 'success'

    # Generate reasoning
    reasons = []
    if understanding <= 2:
        reasons.append(f"understanding is low ({understanding}/5)")
    elif understanding >= 4:
        reasons.append(f"understanding is high ({understanding}/5)")

    if exam_days <= 3:
        reasons.append(f"exam is extremely urgent ({exam_days} day{'s' if exam_days != 1 else ''} left)")
    elif exam_days <= 7:
        reasons.append(f"exam is approaching ({exam_days} days left)")

    if difficulty >= 4:
        reasons.append(f"topic difficulty is high ({difficulty}/5)")

    if importance >= 4:
        reasons.append(f"topic weightage/importance is high ({importance}/5)")

    if not reasons:
        reasons.append("balanced factor weights across parameters")

    reason_str = f"{topic.get('name', 'Topic')} has {priority_level.lower()} priority because " + ", ".join(reasons) + "."

    return {
        'priority_score': score_percentage,
        'raw_score': raw_score,
        'priority_level': priority_level,
        'badge_class': badge_class,
        'reason': reason_str,
        'factors': {
            'weakness': round(effective_weakness_norm * 100, 1),
            'urgency': round(urgency_norm * 100, 1),
            'difficulty': round(difficulty_norm * 100, 1),
            'importance': round(importance_norm * 100, 1),
            'raw_weakness': raw_weakness
        }
    }
