# AI Usage Log — AI Interview Agent

## Hackathon
**VicoDathon 2026**

## Project
**AI Interview Agent**

## Purpose

AI was used during development to assist with application architecture, coding, debugging, UI improvements, interview logic, and deployment troubleshooting.

The final implementation was reviewed, integrated, tested, and deployed by the team.

---

## AI Tools Used

- **ChatGPT** — coding assistance, debugging, architecture discussions, UI improvements, deployment guidance, and documentation.
- **Google Gemini** — used by the application itself to generate interview questions and evaluate candidate answers.

---

# Development Prompt Log

## 1. Project Architecture

**Prompt:**

> Help design an AI-powered technical interview application where candidates are selected based on their learning journey and the interview questions are generated dynamically according to their completed curriculum.

**Purpose:**

Used to plan the overall candidate → interview → answer → evaluation workflow.

---

## 2. Candidate Analysis

**Prompt:**

> Create a candidate analyzer that reads candidate data, separates passed, failed, and skipped missions, and determines an attempts-based prior such as Strong, Moderate, or Fragile.

**Purpose:**

Used to build the candidate-analysis logic that determines which curriculum days are eligible for an interview.

---

## 3. Curriculum-Aware Interview Logic

**Prompt:**

> Implement an interview engine that selects eligible curriculum days, tracks the interview session, records questions and answers, and adapts question difficulty based on the candidate's previous performance.

**Purpose:**

Used to develop the deterministic interview-session and question-scheduling logic.

---

## 4. Adaptive Difficulty

**Prompt:**

> Design an adaptive difficulty system with recall, applied, and system-level question tiers, where the difficulty changes according to the candidate's previous performance.

**Purpose:**

Used for the `L1_RECALL`, `L2_APPLIED`, and `L3_SYSTEM` difficulty levels.

---

## 5. Follow-up Questions

**Prompt:**

> Implement interview follow-up logic where partial or weak answers can trigger a follow-up question on the same topic, while limiting the number of follow-ups.

**Purpose:**

Used to make the interview adaptive instead of simply asking a fixed sequence of questions.

---

## 6. Answer Evaluation

**Prompt:**

> Design structured answer classification for an AI interview. Classify answers as Strong, Partial, or Weak and identify possible gaps such as lack of depth, trade-off awareness, implementation grounding, hedging, or confidently incorrect answers.

**Purpose:**

Used for the structured answer-evaluation model.

---

## 7. Backend API

**Prompt:**

> Build FastAPI routes for starting an interview, submitting an answer, and finishing an interview. Return the current question, topic, progress, and readiness information to the frontend.

**Purpose:**

Used to implement the main interview API endpoints.

---

## 8. React Frontend

**Prompt:**

> Build a React frontend for an AI technical interviewer with candidate cards, candidate selection, interview questions, answer input, progress tracking, follow-up indicators, and final scorecard display.

**Purpose:**

Used to implement the frontend interface and connect it with the FastAPI backend.

---

## 9. Frontend–Backend Integration

**Prompt:**

> Connect the React frontend with the FastAPI backend using API requests for candidates, starting interviews, submitting answers, and finishing interviews. Handle loading and error states.

**Purpose:**

Used to integrate the deployed application components.

---

## 10. UI/UX Improvements

**Prompt:**

> Improve the interview application's interface to make it more modern, unique, and attractive while keeping a black base and introducing green and red accent colors.

**Purpose:**

Used to improve the visual identity of the application without changing backend functionality.

---

## 11. Deployment and CORS

**Prompt:**

> Help deploy the React frontend and FastAPI backend and configure CORS so the deployed frontend can communicate with the deployed backend.

**Purpose:**

Used during deployment and troubleshooting of the production frontend-backend connection.

---

## 12. Debugging

**Prompt:**

> Debug the interview flow when the application reports "No valid curriculum day found" and identify the cause in the backend interview route and curriculum selection logic.

**Purpose:**

Used to troubleshoot the interview-start flow.

---

## 13. Candidate Data Debugging

**Prompt:**

> Debug why the frontend is displaying generic candidate names such as Candidate 1 and Candidate 2 instead of the actual candidate information from the JSON data.

**Purpose:**

Used to correct candidate-data normalization and frontend display.

---

## 14. Final Testing

**Prompt:**

> Review the complete frontend and backend interview flow and identify issues that could prevent a deployed interview from working correctly.

**Purpose:**

Used for final testing and deployment verification.

---

# AI-Assisted Application Behavior

The application uses AI during the actual interview process.

### Question Generation

Gemini receives candidate and curriculum context and generates technical interview questions.

### Answer Evaluation

Gemini evaluates submitted answers and classifies their quality.

### Adaptive Interview

The backend uses the evaluation to determine whether to:

- ask a follow-up question,
- increase question difficulty,
- decrease question difficulty,
- move to another eligible curriculum day.

The deterministic interview engine remains responsible for session state, eligibility, question counts, day coverage, and interview completion.

---

# Human Review and Integration

AI-generated suggestions and code were not used blindly.

The team:

- reviewed generated code,
- integrated the required components,
- tested the frontend and backend,
- debugged API and deployment issues,
- verified the interview flow,
- modified the UI,
- and deployed the final application.

---

# Final Deployment

**Frontend:**

https://ai-interview-agent-seven-roan.vercel.app/

The application was tested after deployment to verify that the frontend and backend communicate successfully.

---

## Summary

AI was used as a development assistant and as part of the application's interview intelligence.

The final project combines:

**React frontend + FastAPI backend + candidate analysis + curriculum-aware scheduling + Gemini question generation + AI answer evaluation + adaptive follow-ups + scoring.**