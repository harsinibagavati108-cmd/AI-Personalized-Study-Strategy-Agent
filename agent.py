"""
Intelligent Agent Component for Personalized Study Strategy.

Agent Architecture:
  OBSERVE  -> Ingest student topics and available time
  REASON   -> Evaluate heuristic score for each topic
  DECIDE   -> Rank topics in descending order of priority
  ACT      -> Allocate study duration proportionally based on priority weight
  FEEDBACK -> Recalculate state updates (understanding/progress/time)
  REPLAN   -> Generate an updated personalized strategy dynamically
"""

from heuristic import evaluate_topic_heuristic


class StudyAgent:
    """
    Intelligent Agent for Personalizing Study Strategy.
    """

    def __init__(self):
        self.state = {
            'topics': [],
            'available_hours': 0.0,
            'plan': [],
            'total_minutes': 0
        }

    def observe(self, topics, available_hours):
        """
        OBSERVE STEP:
        Captures and structures the current environment/student state.
        """
        cleaned_topics = []
        for idx, t in enumerate(topics):
            topic_dict = {
                'id': t.get('id', idx + 1),
                'subject': str(t.get('subject', '')).strip(),
                'name': str(t.get('name', '')).strip(),
                'difficulty': int(t.get('difficulty', 3)),
                'understanding': int(t.get('understanding', 3)),
                'exam_days': int(t.get('exam_days', 7)),
                'importance': int(t.get('importance', 3)),
                'progress': int(t.get('progress', 0))
            }
            cleaned_topics.append(topic_dict)

        self.state['topics'] = cleaned_topics
        self.state['available_hours'] = max(0.25, float(available_hours))
        self.state['total_minutes'] = int(self.state['available_hours'] * 60)
        return self.state

    def reason(self):
        """
        REASON STEP:
        Evaluates heuristic functions for all observed topics.
        """
        evaluated_topics = []
        for topic in self.state['topics']:
            evaluation = evaluate_topic_heuristic(topic)
            topic_with_eval = {**topic, **evaluation}
            evaluated_topics.append(topic_with_eval)

        return evaluated_topics

    def decide(self, evaluated_topics):
        """
        DECIDE STEP:
        Ranks topics by priority score descending.
        """
        ranked_topics = sorted(evaluated_topics, key=lambda x: x['raw_score'], reverse=True)
        for rank, topic in enumerate(ranked_topics, 1):
            topic['rank'] = rank
        return ranked_topics

    def act(self, ranked_topics):
        """
        ACT STEP:
        Allocates available study minutes to ranked topics proportionally based on priority scores.
        Ensures realistic session durations (rounded to nearest 5 mins, minimum 10 mins if allocated).
        """
        total_minutes = self.state['total_minutes']
        if not ranked_topics or total_minutes <= 0:
            return []

        total_raw_score = sum(t['raw_score'] for t in ranked_topics)

        # Handle case where all scores are 0
        if total_raw_score <= 0:
            total_raw_score = 1.0

        allocated_plan = []
        minutes_remaining = total_minutes

        for idx, topic in enumerate(ranked_topics):
            if idx == len(ranked_topics) - 1:
                # Last topic gets remaining minutes to make exact total
                duration_mins = max(0, minutes_remaining)
            else:
                proportion = topic['raw_score'] / total_raw_score
                raw_duration = proportion * total_minutes
                # Round to nearest 5 minutes
                duration_mins = int(round(raw_duration / 5.0) * 5)
                # Enforce minimum allocation if duration > 0
                if raw_duration > 0 and duration_mins == 0:
                    duration_mins = 5
                duration_mins = min(duration_mins, minutes_remaining)

            minutes_remaining -= duration_mins

            # Format duration string
            if duration_mins >= 60:
                hrs = duration_mins // 60
                mins = duration_mins % 60
                duration_str = f"{hrs}h {mins}m" if mins > 0 else f"{hrs}h"
            else:
                duration_str = f"{duration_mins} mins"

            plan_item = {
                **topic,
                'allocated_minutes': duration_mins,
                'duration_str': duration_str,
                'time_percentage': round((duration_mins / total_minutes) * 100, 1) if total_minutes > 0 else 0
            }
            allocated_plan.append(plan_item)

        self.state['plan'] = allocated_plan
        return allocated_plan

    def generate_strategy(self, topics, available_hours):
        """
        Execute full agent cycle: OBSERVE -> REASON -> DECIDE -> ACT
        """
        self.observe(topics, available_hours)
        evaluated = self.reason()
        ranked = self.decide(evaluated)
        plan = self.act(ranked)
        return {
            'topics_count': len(plan),
            'available_hours': self.state['available_hours'],
            'total_minutes': self.state['total_minutes'],
            'plan': plan
        }

    def replan(self, updated_topics, new_available_hours, previous_plan=None):
        """
        FEEDBACK & REPLAN STEP:
        Recalculate priorities and generate a new study plan after student updates understanding, progress, or time.
        Highlights changes compared to previous plan.
        """
        new_strategy = self.generate_strategy(updated_topics, new_available_hours)
        
        # Calculate diff/changes if previous plan provided
        changes = []
        if previous_plan:
            prev_map = {t['name']: t for t in previous_plan}
            for new_item in new_strategy['plan']:
                name = new_item['name']
                if name in prev_map:
                    prev_item = prev_map[name]
                    rank_diff = prev_item['rank'] - new_item['rank'] # Positive means improved rank (moved up)
                    score_diff = round(new_item['priority_score'] - prev_item['priority_score'], 1)
                    time_diff = new_item['allocated_minutes'] - prev_item['allocated_minutes']
                    
                    change_desc = []
                    if prev_item['understanding'] != new_item['understanding']:
                        change_desc.append(f"Understanding: {prev_item['understanding']}/5 -> {new_item['understanding']}/5")
                    if prev_item['progress'] != new_item['progress']:
                        change_desc.append(f"Progress: {prev_item['progress']}% -> {new_item['progress']}%")
                    if rank_diff != 0:
                        change_desc.append(f"Rank: #{prev_item['rank']} -> #{new_item['rank']}")
                    if time_diff != 0:
                        change_desc.append(f"Time: {prev_item['duration_str']} -> {new_item['duration_str']}")

                    new_item['replan_info'] = {
                        'prev_rank': prev_item['rank'],
                        'prev_score': prev_item['priority_score'],
                        'prev_time': prev_item['duration_str'],
                        'rank_diff': rank_diff,
                        'score_diff': score_diff,
                        'time_diff': time_diff,
                        'change_summary': ", ".join(change_desc) if change_desc else "No major state changes"
                    }

        return {
            'strategy': new_strategy,
            'has_replanned': True
        }
