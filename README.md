# AI Interview Agent

An AI-powered technical interview platform that conducts personalized interviews based on a candidate's learning journey, completed curriculum, and previous performance.

## 🚀 Live Demo

**Frontend:**  
https://ai-interview-agent-seven-roan.vercel.app/

---

## 🎯 Problem

Traditional technical interviews often use the same questions for every candidate, regardless of their previous learning experience or strengths and weaknesses.

The AI Interview Agent solves this by creating a personalized and adaptive interview experience based on the candidate's completed curriculum and previous performance.

---

## 💡 Solution

The system analyzes a candidate's learning history and identifies the curriculum topics they have successfully completed.

During the interview:

1. The system selects eligible curriculum topics.
2. Gemini generates a technical question based on the candidate's curriculum.
3. The candidate submits an answer.
4. Gemini evaluates the answer.
5. The system classifies the answer as **Strong, Partial, or Weak**.
6. The interview difficulty adapts based on the candidate's performance.
7. Weak or incomplete answers can trigger follow-up questions.
8. The system tracks topic coverage and interview readiness.
9. A final scorecard is generated after the interview.

---

## ✨ Key Features

### 👤 Candidate Analysis

- Candidate profiles loaded from structured JSON data.
- Tracks passed, failed, and skipped missions.
- Tracks the number of attempts for completed missions.
- Determines candidate confidence priors:
  - Strong
  - Moderate
  - Fragile

### 🧠 Curriculum-Aware Interview

Questions are generated from curriculum topics that the candidate has successfully completed.

This prevents the system from asking questions about topics the candidate has not yet learned.

### 🤖 AI Question Generation

Gemini generates technical interview questions using:

- Candidate information
- Curriculum topic
- Previous interview transcript
- Current difficulty level
- Previous answer quality

### 📈 Adaptive Difficulty

The interview supports three difficulty levels:

| Level | Description |
|---|---|
| L1_RECALL | Basic concept and recall |
| L2_APPLIED | Application and practical understanding |
| L3_SYSTEM | Deeper system-level reasoning |

Difficulty can change according to the candidate's answer quality.

### 🔄 Intelligent Follow-ups

When an answer is classified as Partial or Weak, the system can ask a follow-up question on the same topic.

Follow-ups are limited to prevent the interview from becoming repetitive.

### 📝 Answer Evaluation

Answers are classified into:

- **STRONG**
- **PARTIAL**
- **WEAK**

The system can also identify reasoning gaps such as:

- Surface-level understanding
- Lack of trade-off awareness
- Lack of implementation grounding
- Hedging or incomplete reasoning
- Confidently incorrect answers

### 📊 Interview Progress

The interface tracks:

- Question number
- Number of curriculum days covered
- Current topic
- Current difficulty
- Follow-up questions
- Interview readiness

### 🏆 Final Scorecard

After the interview, the system provides:

- Topic-wise scores
- Weak concepts
- Coverage gaps
- Narrative feedback
- Recommendation

---

## 🏗️ System Architecture

```text
                    ┌─────────────────────┐
                    │      Candidate      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   React Frontend    │
                    │      (Vercel)       │
                    └──────────┬──────────┘
                               │
                         REST API
                               │
                               ▼
                    ┌─────────────────────┐
                    │   FastAPI Backend   │
                    │      (Render)       │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
       Candidate Analyzer  Curriculum       Interview
                          Loader            Engine
              │                │                │
              └────────────────┼────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Gemini Service   │
                    │  Question + Answer  │
                    │     Evaluation      │
                    └─────────────────────┘
```

---

## 🛠️ Tech Stack

### Frontend

- React
- JavaScript
- CSS
- Fetch API

### Backend

- Python
- FastAPI
- Pydantic

### AI

- Google Gemini

### Deployment

- Vercel — Frontend
- Render — Backend

### Data

- JSON-based candidate data
- JSON-based curriculum data

---

## 📁 Project Structure

```text
AI-INTERVIEW-AGENT/
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── ...
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── data/
│   │   │   ├── candidates.json
│   │   │   └── curriculum.json
│   │   │
│   │   ├── models/
│   │   │   └── interview.py
│   │   │
│   │   ├── routes/
│   │   │   ├── candidates.py
│   │   │   └── interview.py
│   │   │
│   │   └── services/
│   │       ├── candidate_analyzer.py
│   │       ├── curriculum_loader.py
│   │       ├── interview_engine.py
│   │       ├── gemini_service.py
│   │       ├── prompt_builder.py
│   │       ├── scoring.py
│   │       └── session_store.py
│   │
│   └── ...
│
├── PROMPTS.md
├── README.md
└── ...
```

---

## 🔄 Interview Flow

```text
Candidate Selection
        ↓
Candidate Analysis
        ↓
Identify Passed Curriculum Days
        ↓
Start Interview Session
        ↓
Generate AI Question
        ↓
Candidate Answers
        ↓
AI Evaluates Answer
        ↓
Strong ────────────────→ Increase Difficulty
        │
        ├── Partial ────→ Follow-up Question
        │
        └── Weak ───────→ Follow-up / Lower Difficulty
        ↓
Continue Until Readiness Criteria
        ↓
Finish Interview
        ↓
Generate Scorecard
```

---

## 🧩 API Endpoints

### Get Candidates

```http
GET /candidates
```

Returns the available candidate profiles.

### Start Interview

```http
POST /interview/start
```

Example request:

```json
{
  "candidate_id": "candidate-id"
}
```

### Submit Answer

```http
POST /interview/answer
```

Example request:

```json
{
  "session_id": "session-id",
  "answer_text": "Candidate's answer"
}
```

### Finish Interview

```http
POST /interview/finish
```

Example request:

```json
{
  "session_id": "session-id"
}
```

### Health Check

```http
GET /health
```

---

## 🎨 User Interface

The frontend provides:

- Candidate selection dashboard
- Candidate profile cards
- Interview progress sidebar
- Current curriculum topic
- AI-generated question display
- Answer input area
- Follow-up indicators
- Interview completion controls
- Final scorecard

The UI uses a dark visual theme with contrasting accent colors to provide a focused technical-interview experience.

---

## ▶️ Running Locally

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd <YOUR_PROJECT_FOLDER>
```

### 2. Start the Backend

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start FastAPI:

```bash
uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

### 3. Start the Frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend:

```text
http://localhost:5173
```

---

## 🔑 Environment Variables

The Gemini API key should be stored as an environment variable and should not be committed to GitHub.

Example:

```env
GEMINI_API_KEY=your_api_key_here
```

---

## 🧪 Testing

The complete application flow was tested across:

- Candidate loading
- Candidate selection
- Interview initialization
- AI question generation
- Answer submission
- Answer evaluation
- Adaptive follow-up questions
- Interview progress tracking
- Interview completion
- Scorecard generation
- Frontend-backend communication
- Production deployment

---

## 🚀 Deployment

The application is deployed using:

**Frontend:** Vercel

**Backend:** Render

### Live Application

https://ai-interview-agent-seven-roan.vercel.app/

The deployed frontend communicates with the deployed FastAPI backend through REST APIs.

---

## 🤖 AI Usage

AI was used both during development and as part of the final application.

During development, AI assisted with:

- Architecture
- Backend implementation
- Frontend implementation
- Debugging
- UI improvements
- Deployment troubleshooting
- Documentation

During application execution, Gemini is responsible for:

- Generating interview questions
- Evaluating candidate answers
- Supporting adaptive interview behavior

Detailed AI usage is documented in:

```text
PROMPTS.md
```

---

## 🏆 Hackathon Deliverables

| Requirement | Status |
|---|---|
| Public GitHub Repository | ✅ |
| Live Deployed Application | ✅ |
| AI Usage Log | ✅ PROMPTS.md |
| Frontend Deployment | ✅ |
| Backend Deployment | ✅ |
| Working Interview Flow | ✅ |

---

## 👥 Team

**Team Name:** CodeXverse

**Hackathon:** VicoDathon 2026

---

## 📌 Future Improvements

Possible future improvements include:

- Authentication and role-based access
- Persistent database instead of JSON storage
- Interviewer dashboard
- Candidate history and analytics
- Voice-based interviews
- Resume-based question generation
- More detailed performance analytics
- Multi-language interview support

---

## 📄 License

This project was developed as part of VicoDathon 2026.