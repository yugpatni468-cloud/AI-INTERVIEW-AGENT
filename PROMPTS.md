# AI Usage Log — VicoDathon 2026

## Project

**AI Interview Agent** — an AI-powered technical interview system that personalizes interviews using a candidate's learning journey.

The project consists of a FastAPI backend and a React/Vite frontend. The backend handles candidate analysis, curriculum selection, interview sessions, adaptive questioning, answer classification, deterministic scoring, and AI-generated feedback.

---

## AI Tools Used

During development, the team used the following AI-assisted development tools:

- **ChatGPT** — architecture guidance, debugging, code explanations, API testing guidance, prompt design, and implementation planning.
- **Claude** — repository/code review, architecture review, implementation planning, and assistance with backend/frontend integration.
- **Cursor** — codebase inspection and AI-assisted code modifications/integration.

AI tools were used as development assistants. Final code was reviewed, tested, and validated by the team.

---

## Major AI-Assisted Tasks

### 1. Project Architecture Review

AI was asked to inspect the existing AI Interview Agent architecture and identify missing functionality.

Representative prompt:

> Review the existing FastAPI backend against the hackathon requirements. Identify what is already implemented, what is missing, bugs in the current implementation, and provide a prioritized implementation plan.

This resulted in identification of the main gaps:

- No complete multi-turn interview loop
- Missing session/memory layer
- Missing adaptive interview orchestration
- Missing `/interview/answer`
- Missing `/interview/finish`
- Missing deterministic scoring
- Frontend/backend integration gaps
- Candidate personalization issues

---

### 2. Candidate Personalization

AI identified an issue where failed missions could be lost during candidate analysis.

Representative requirement:

> Make sure PASSED, FAILED, and SKIPPED missions are treated as separate states because failed topics are important weak-concept signals.

The candidate analyzer was updated to preserve failed-topic information and make it available to the interview engine.

---

### 3. Interview Session and Memory

AI was used to design an in-memory session architecture because the hackathon did not require a database.

The session design tracks information such as:

- Session ID
- Candidate ID
- Current day/topic
- Questions asked
- Distinct curriculum days
- Transcript
- Answer classifications
- Follow-up count
- Difficulty state
- Running scores
- Coverage information

This enables the interview to continue across multiple API requests instead of generating only one independent question.

---

### 4. Adaptive Interviewing

AI helped design the adaptive questioning logic.

The intended behavior is:

```text
STRONG answer
    → increase difficulty / move forward

PARTIAL answer
    → targeted follow-up

WEAK answer
    → simpler or foundational follow-up
```

A follow-up limit is used so that the interview continues to cover multiple curriculum days.

---

### 5. Hackathon Constraints

The interview was designed around the required minimum:

- At least **8 questions**
- At least **4 distinct curriculum days**

AI was used to reason about how follow-ups could accidentally consume the entire interview without reaching the required number of distinct days. The interview engine therefore prioritizes new days when necessary.

---

### 6. LLM Answer Classification

AI was used to design structured answer classification rather than relying on free-form LLM output.

Expected classification structure:

```json
{
  "quality": "STRONG | PARTIAL | WEAK",
  "gap_type": "...",
  "rationale": "..."
}
```

Malformed responses and LLM failures are intended to be handled safely rather than crashing the interview.

---

### 7. Deterministic Scoring

A key design decision was to keep numeric scoring in Python rather than asking the LLM to invent scores.

Conceptually:

```text
STRONG  → 2 points
PARTIAL → 1 point
WEAK    → 0 points
```

The LLM can generate the final narrative feedback, while the structured numerical results remain deterministic and reproducible.

---

### 8. Frontend / Backend Integration

AI was used to help connect the React/Vite frontend to the FastAPI backend.

The intended live flow is:

```text
React Candidate Selection
        ↓
GET /candidates
        ↓
POST /interview/start
        ↓
Display Question
        ↓
POST /interview/answer
        ↓
Adaptive Next Question
        ↓
8+ Questions / 4+ Days
        ↓
POST /interview/finish
        ↓
Scorecard + AI Feedback
```

The goal was to replace mocked interview behavior with the actual backend APIs.

---

### 9. Debugging and Development Support

AI was also used during development to diagnose issues including:

- FastAPI/Uvicorn startup errors
- Missing environment variables
- Gemini/Groq API configuration
- Git/GitHub workflow issues
- Python dependency problems
- API endpoint testing through Swagger
- Frontend/backend integration problems

The team manually applied and tested fixes rather than relying solely on AI-generated output.

---

## Human Review and Validation

AI-generated code and recommendations were not treated as automatically correct.

The team reviewed changes and used:

- FastAPI Swagger documentation
- Local API requests
- Python compilation checks
- Automated tests
- Frontend build checks
- Git diff/status review
- Manual end-to-end testing

API keys and other secrets were kept outside the source repository in environment variables.

---

## AI's Role in the Final Product

AI assisted with:

- Code generation
- Architecture analysis
- Debugging
- Prompt engineering
- API design
- Testing strategy
- Frontend/backend integration

The final implementation was reviewed and validated by the development team.

AI tools were therefore used as **development assistants**, while the team remained responsible for implementation decisions, integration, testing, and the final submitted product.
