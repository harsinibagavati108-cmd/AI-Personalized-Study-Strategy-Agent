# AI-Based Personalized Study Strategy Agent

> **Artificial Intelligence College Mini-Project**  
> An algorithmic Intelligent Agent implementation featuring State-Space Problem Formulation, Normalized Heuristic Evaluation, Prioritized Decision-Making, and Dynamic Adaptive Replanning.

---

## 1. Project Title
**AI-Based Personalized Study Strategy Agent**

---

## 2. Problem Statement
Students preparing for academic examinations face significant cognitive overload when attempting to prioritize their study time across multiple subjects. Traditional static study timetables fail because they:
1. Treat all topics equally regardless of student weakness or topic difficulty.
2. Ignore exam urgency and time constraints.
3. Cannot adapt when a student makes progress, masters a topic, or experiences schedule changes.

---

## 3. Motivation
Rather than relying on generic scheduling tools or black-box LLM chatbots, students require an **algorithmic AI agent** that transparently calculates topic priority using mathematical heuristics and continuously adapts as their learning state evolves.

---

## 4. Objective
To build a lightweight, working, demonstrable Intelligent Agent that answers two core questions:
1. **"What topic should I study first?"**
2. **"How much time should I allocate to it based on my available schedule?"**

---

## 5. Proposed Solution
An AI study assistant powered by a deterministic **Intelligent Agent Core**. The agent ingests student parameters, evaluates a multi-factor normalized heuristic function, ranks topics in descending order of priority, allocates study durations proportionally, and dynamically replans upon receiving student feedback.

---

## 6. Intelligent Agent Architecture
The system explicitly executes the classic 6-stage Intelligent Agent lifecycle:

```
    [ OBSERVE ]  ---> Ingest Student State (Topics, Understanding, Exam Days, Hours)
         |
    [  REASON  ]  ---> Calculate Normalized Heuristic Priority Scores
         |
    [  DECIDE  ]  ---> Rank Topics by Priority Score
         |
    [   ACT    ]  ---> Allocate Available Study Minutes Proportionally
         |
    [ FEEDBACK ]  ---> Student Updates Understanding / Progress / Schedule
         |
    [  REPLAN  ]  ---> Recalculate Heuristics & Update Strategy Dynamically
```

### Why This Qualifies as an AI Intelligent Agent
1. **Autonomy & Goal-Directed Behavior**: Operates autonomously to achieve the goal of optimal study efficiency given resource constraints (available hours).
2. **Perception-Reasoning-Action Loop**: Observes environment state, evaluates state using an internal heuristic reasoning model, and executes an actionable plan.
3. **Adaptive Learning State**: Demonstrates closed-loop feedback control and dynamic replanning when the environmental state changes.

---

## 7. Problem Formulation
- **Initial State**: Student has $N$ study topics with varying difficulty, understanding levels, exam deadlines, importance, and total available study time $T$.
- **State**: $S = \{ (T_1, U_1, D_1, E_1, I_1, P_1), (T_2, U_2, D_2, E_2, I_2, P_2), \dots, T_{\text{available}} \}$
- **Actions**: Select top-priority topic, allocate time duration $t_i \in [0, T_{\text{available}}]$.
- **Goal**: Maximize overall study efficacy $\sum (\text{Priority}_i \times t_i)$ subject to total time constraint $\sum t_i \le T_{\text{available}}$.
- **Constraints**: Limited study session duration, minimum session thresholds, strict priority ordering.

---

## 8. State Representation
Each topic $T_i$ is represented as a structured state tuple:
$$\text{Topic State} = \langle \text{Subject}, \text{Name}, \text{Difficulty } (1\text{--}5), \text{Understanding } (1\text{--}5), \text{Exam Days Remaining}, \text{Importance } (1\text{--}5), \text{Progress } (0\text{--}100\%) \rangle$$

---

## 9. Heuristic Function
The core decision engine evaluates a multi-factor weighted heuristic formula where all factors are normalized to the range $[0.0, 1.0]$:

$$\text{Priority Score} = 0.35 \times \text{Weakness} + 0.30 \times \text{Exam Urgency} + 0.20 \times \text{Difficulty} + 0.15 \times \text{Importance}$$

### Factor Definitions & Normalization:
1. **Weakness**: Derived from Understanding ($U \in [1, 5]$).
   $$\text{Weakness}_{\text{raw}} = 6 - U$$
   $$\text{Weakness}_{\text{norm}} = \frac{\text{Weakness}_{\text{raw}} - 1}{4} \times \left(1 - \frac{\text{Progress}}{100}\right)$$
2. **Exam Urgency**: Inverse non-linear decay based on exam days remaining ($E$):
   $$\text{Urgency}_{\text{norm}} = \frac{1}{1 + 0.12 \times (E - 1)} \quad \text{for } E \ge 1$$
3. **Difficulty**: Normalized 1--5 rating:
   $$\text{Difficulty}_{\text{norm}} = \frac{D - 1}{4}$$
4. **Importance**: Normalized 1--5 weightage:
   $$\text{Importance}_{\text{norm}} = \frac{I - 1}{4}$$

---

## 10. Decision-Making Process
1. **Score Calculation**: Compute $\text{Priority Score} \in [0, 100\%]$ for each topic.
2. **Ranking**: Sort topics in descending order of Priority Score.
3. **Categorization**:
   - $\ge 70\%$: **HIGH Priority**
   - $45\% \text{--} 69\%$: **MEDIUM Priority**
   - $< 45\%$: **LOW Priority**
4. **Time Allocation**: Allocate available study minutes $T_{\text{mins}} = H_{\text{available}} \times 60$ proportionally based on priority weight:
   $$t_i = \left( \frac{\text{Priority}_i}{\sum \text{Priority}} \right) \times T_{\text{mins}}$$

---

## 11. Adaptive Replanning
When the student provides post-study feedback:
- **Scenario A (Understanding Improvement)**: Studying *Probability* increases understanding from $2/5 \to 4/5$. The agent recalculates weakness factor ($35\% \to 15\%$), dropping its priority score and promoting other weak topics like *Data Structures*.
- **Scenario B (Schedule Shift)**: Available time decreases from $3.0\text{ hours} \to 1.0\text{ hour}$. The agent re-allocates total time dynamically while preserving priority rank ordering.

---

## 12. System Workflow
1. **Student Input** $\to$
2. **State Vector Construction** $\to$
3. **Heuristic Evaluation (`heuristic.py`)** $\to$
4. **Agent Decision (`agent.py`)** $\to$
5. **Study Strategy Output (`recommendation.html`)** $\to$
6. **Student Feedback (`feedback.html`)** $\to$
7. **Adaptive Replanning (`replan`)**

---

## 13. Technology Stack
- **Backend Core**: Python 3 (Agent & Heuristic Logic)
- **Web Framework**: Flask
- **Frontend**: HTML5, Vanilla CSS3 (Custom Glassmorphism Theme), JavaScript (ES6)
- **Templating**: Jinja2

---

## 14. Project Structure
```
PersonalizedStudyAgent/
│
├── app.py              # Flask server & route handlers
├── agent.py            # Intelligent Agent core (OBSERVE, REASON, DECIDE, ACT, REPLAN)
├── heuristic.py        # Heuristic formula calculation & natural language explanations
├── requirements.txt    # Python dependencies
├── README.md           # Project documentation
│
├── templates/
│   ├── index.html          # Home landing page & AI concepts
│   ├── input.html          # Student input form
│   ├── recommendation.html # AI recommendation & plan dashboard
│   └── feedback.html       # Adaptive feedback & replanning page
│
└── static/
    ├── style.css       # Clean college project CSS styling
    └── script.js       # Dynamic UI interactions & form validation
```

---

## 15. Installation

1. Ensure Python 3.8+ is installed on your system.
2. Clone or download the project files.
3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

---

## 16. How to Run

1. Start the Flask application:
   ```bash
   python app.py
   ```
2. Open your web browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```
3. Click **"Start Planning"** to input custom topics or **"Quick Demo"** to load pre-configured sample topics.

---

## 17. Example Input/Output

### Input:
- **Available Time**: 2.0 hours (120 minutes)
- **Topic 1**: Probability & Statistics (Difficulty: 5, Understanding: 2, Exam Days: 3, Importance: 5)
- **Topic 2**: Data Structures (Difficulty: 4, Understanding: 3, Exam Days: 5, Importance: 5)
- **Topic 3**: Python OOP (Difficulty: 3, Understanding: 4, Exam Days: 10, Importance: 4)

### Agent Output:
1. **Probability & Statistics** — **60 minutes** (HIGH Priority — Score: 82.5%)  
   *Reason*: Understanding is low (2/5), exam is urgent (3 days left), difficulty is high (5/5).
2. **Data Structures** — **40 minutes** (MEDIUM Priority — Score: 58.2%)  
   *Reason*: Moderate understanding (3/5), exam approaching (5 days left).
3. **Python OOP** — **20 minutes** (LOW Priority — Score: 36.4%)  
   *Reason*: Understanding is high (4/5), exam date is further away (10 days left).

---

## 18. Limitations
- Deterministic heuristic relies on accurate student self-assessment ratings.
- Time allocation rounds to standard 5-minute increments.

---

## 19. Future Enhancements
- Integration of spaced repetition decay curves (Ebbinghaus forgetting curve).
- Calendar export (.ics) for automated mobile reminder scheduling.
- Empirical performance tracking over multiple study sessions.
