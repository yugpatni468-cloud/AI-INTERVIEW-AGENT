
import { useEffect, useState } from "react";

const API_URL = "http://127.0.0.1:8000";

function App() {
  // ==========================================
  // STATES
  // ==========================================

  const [screen, setScreen] = useState("candidates");

  const [candidates, setCandidates] = useState([]);
  const [selectedCandidate, setSelectedCandidate] = useState(null);

  const [messages, setMessages] = useState([]);
  const [message, setMessage] = useState("");

  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);

  const [questionNumber, setQuestionNumber] = useState(1);
  const [currentDay, setCurrentDay] = useState(1);

  const [results, setResults] = useState(null);
  const [error, setError] = useState("");

  // ==========================================
  // LOAD CANDIDATES FROM BACKEND
  // ==========================================

  useEffect(() => {
    const loadCandidates = async () => {
      try {
        setLoading(true);
        setError("");

        const response = await fetch(`${API_URL}/candidates`);

        const data = await response.json();

        console.log("CANDIDATES RESPONSE:", data);

        if (!response.ok) {
          throw new Error(
            data.detail || `Backend error: ${response.status}`
          );
        }

        setCandidates(data);
      } catch (err) {
        console.error("CANDIDATES ERROR:", err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadCandidates();
  }, []);

  // ==========================================
  // START INTERVIEW
  // ==========================================

  const startInterview = async (candidate) => {
    setSelectedCandidate(candidate);

    setMessages([]);
    setError("");
    setSessionId(null);

    setQuestionNumber(1);
    setCurrentDay(1);

    setResults(null);

    setLoading(true);
    setScreen("interview");

    try {
      const response = await fetch(`${API_URL}/interview/start`, {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          candidate_id: String(candidate.id),
          day: 1,
        }),
      });

      const data = await response.json();

      console.log("START RESPONSE:", data);

      if (!response.ok) {
        throw new Error(
          data.detail || `Backend error: ${response.status}`
        );
      }

      // Session ID
      const newSessionId =
        data.session_id ||
        data.sessionId ||
        data.interview_id ||
        data.id;

      if (!newSessionId) {
        throw new Error("Backend did not return a session_id.");
      }

      setSessionId(newSessionId);

      // Question number
      setQuestionNumber(data.question_number || 1);

      // Curriculum day
      setCurrentDay(data.day || 1);

      // First question
      const question =
        data.question ||
        data.next_question ||
        data.next_question_text ||
        data.ai_question ||
        data.message ||
        data.reply;

      if (!question) {
        throw new Error(
          "Backend did not return an interview question."
        );
      }

      setMessages([
        {
          sender: "ai",
          text: question,
        },
      ]);
    } catch (err) {
      console.error("START INTERVIEW ERROR:", err);

      setError(err.message);

      setMessages([
        {
          sender: "ai",
          text: `Unable to start interview: ${err.message}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  // ==========================================
  // SEND ANSWER
  // ==========================================

  const sendMessage = async () => {
    if (!message.trim() || loading || !sessionId) {
      return;
    }

    const userMessage = message.trim();

    // Show user answer immediately
    setMessages((prev) => [
      ...prev,
      {
        sender: "user",
        text: userMessage,
      },
    ]);

    setMessage("");
    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_URL}/interview/answer`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify({
          session_id: sessionId,
          answer_text: userMessage,
        }),
      });

      const data = await response.json();

      console.log("ANSWER RESPONSE:", data);

      if (!response.ok) {
        throw new Error(
          data.detail || `Backend error: ${response.status}`
        );
      }

      // Update question number
      if (data.question_number !== undefined) {
        setQuestionNumber(data.question_number);
      }

      // Update curriculum day
      if (data.day !== undefined) {
        setCurrentDay(data.day);
      }

      // Find next question
      const nextQuestion =
        data.question ||
        data.next_question ||
        data.next_question_text ||
        data.ai_question ||
        data.message ||
        data.reply;

      if (nextQuestion) {
        setMessages((prev) => [
          ...prev,
          {
            sender: "ai",
            text: nextQuestion,
          },
        ]);
      }

      // If backend says interview completed
      if (
        data.done === true ||
        data.completed === true ||
        data.interview_completed === true
      ) {
        await finishInterview();
      }
    } catch (err) {
      console.error("ANSWER ERROR:", err);

      setError(err.message);

      setMessages((prev) => [
        ...prev,
        {
          sender: "ai",
          text: `Could not process your answer: ${err.message}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  // ==========================================
  // FINISH INTERVIEW
  // ==========================================

  const finishInterview = async () => {
    if (!sessionId || loading) {
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_URL}/interview/finish`, {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          session_id: sessionId,
        }),
      });

      const data = await response.json();

      console.log("FINISH RESPONSE:", data);

      if (!response.ok) {
        throw new Error(
          data.detail || `Backend error: ${response.status}`
        );
      }

      setResults(data);

      setScreen("results");
    } catch (err) {
      console.error("FINISH ERROR:", err);

      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // ==========================================
  // RESET INTERVIEW
  // ==========================================

  const resetInterview = () => {
    setScreen("candidates");

    setSelectedCandidate(null);
    setMessages([]);
    setMessage("");

    setSessionId(null);

    setQuestionNumber(1);
    setCurrentDay(1);

    setResults(null);
    setError("");
  };

  // ==========================================
  // CANDIDATES SCREEN
  // ==========================================

  if (screen === "candidates") {
    return (
      <div className="min-h-screen bg-slate-950 text-white">

        {/* NAVBAR */}

        <nav className="border-b border-slate-800 px-8 py-5">

          <div className="mx-auto flex max-w-7xl items-center justify-between">

            <div>
              <h1 className="text-xl font-bold">
                AI Interview Agent
              </h1>

              <p className="text-sm text-slate-400">
                ABTalks Technical Interview
              </p>
            </div>

            <div className="rounded-full border border-slate-700 px-4 py-2 text-sm text-slate-300">
              31-Day AI Cohort
            </div>

          </div>

        </nav>

        {/* MAIN */}

        <main className="mx-auto max-w-7xl px-8 py-16">

          <p className="mb-3 text-sm font-medium text-blue-400">
            TECHNICAL INTERVIEW PLATFORM
          </p>

          <h2 className="text-4xl font-bold">
            Select a Candidate
          </h2>

          <p className="mt-3 max-w-2xl text-slate-400">
            Conduct a personalized technical interview based on
            the candidate's learning journey.
          </p>

          {/* ERROR */}

          {error && (
            <div className="mt-6 rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-400">
              {error}
            </div>
          )}

          {/* LOADING */}

          {loading && candidates.length === 0 && (
            <div className="mt-10 text-center text-slate-400">
              Loading candidates...
            </div>
          )}

          {/* CANDIDATES */}

          <div className="mt-12 grid gap-6 md:grid-cols-2 lg:grid-cols-3">

            {candidates.map((candidate) => (

              <div
                key={candidate.id}
                className="rounded-2xl border border-slate-800 bg-slate-900 p-6 transition hover:border-blue-500"
              >

                <div className="flex items-center justify-between">

                  <div className="flex h-12 w-12 items-center justify-center rounded-full bg-blue-500/20 text-xl font-bold text-blue-400">
                    {candidate.name?.charAt(0)}
                  </div>

                  <span className="rounded-full bg-slate-800 px-3 py-1 text-xs">
                    {candidate.level || "Unknown"}
                  </span>

                </div>

                <h3 className="mt-5 text-xl font-semibold">
                  {candidate.name}
                </h3>

                <div className="mt-5 grid grid-cols-2 gap-3">

                  <div className="rounded-xl bg-slate-800 p-3">

                    <p className="text-xs text-slate-400">
                      Completed
                    </p>

                    <p className="mt-1 text-lg font-bold">
                      {candidate.completed ?? 0}
                    </p>

                  </div>

                  <div className="rounded-xl bg-slate-800 p-3">

                    <p className="text-xs text-slate-400">
                      Skipped
                    </p>

                    <p className="mt-1 text-lg font-bold">
                      {candidate.skipped ?? 0}
                    </p>

                  </div>

                </div>

                {/* TOPICS */}

                {candidate.topics &&
                  candidate.topics.length > 0 && (

                    <div className="mt-5 flex flex-wrap gap-2">

                      {candidate.topics.map((topic) => (

                        <span
                          key={topic}
                          className="rounded-lg bg-slate-800 px-3 py-1 text-xs text-slate-300"
                        >
                          {topic}
                        </span>

                      ))}

                    </div>

                  )}

                <button
                  onClick={() => startInterview(candidate)}
                  disabled={loading}
                  className="mt-6 w-full rounded-xl bg-blue-600 px-4 py-3 font-medium hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {loading
                    ? "Starting..."
                    : "Start Interview →"}
                </button>

              </div>

            ))}

          </div>

          {/* NO CANDIDATES */}

          {!loading && candidates.length === 0 && !error && (

            <div className="mt-10 rounded-xl border border-slate-800 bg-slate-900 p-8 text-center text-slate-400">
              No candidates found.
            </div>

          )}

        </main>

      </div>
    );
  }

  // ==========================================
  // RESULTS SCREEN
  // ==========================================

  if (screen === "results") {
    return (
      <div className="min-h-screen bg-slate-950 text-white">

        {/* HEADER */}

        <header className="border-b border-slate-800 px-8 py-5">

          <div className="mx-auto flex max-w-6xl items-center justify-between">

            <div>

              <h1 className="text-xl font-bold">
                AI Interview Agent
              </h1>

              <p className="text-sm text-slate-400">
                Interview Results
              </p>

            </div>

            <span className="rounded-full bg-green-500/10 px-4 py-2 text-sm text-green-400">
              ✓ Interview Completed
            </span>

          </div>

        </header>

        <main className="mx-auto max-w-6xl px-8 py-12">

          <p className="text-sm text-blue-400">
            TECHNICAL INTERVIEW REPORT
          </p>

          <h2 className="mt-2 text-4xl font-bold">
            {selectedCandidate?.name}
          </h2>

          <p className="mt-2 text-slate-400">
            AI-generated technical interview assessment
          </p>

          {/* ERROR */}

          {error && (
            <div className="mt-6 rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-400">
              {error}
            </div>
          )}

          {/* SCORE CARDS */}

          <div className="mt-10 grid gap-5 md:grid-cols-2 lg:grid-cols-4">

            {results?.scores &&
              Object.entries(results.scores).map(
                ([skill, score]) => (

                  <div
                    key={skill}
                    className="rounded-2xl border border-slate-800 bg-slate-900 p-6"
                  >

                    <p className="text-sm capitalize text-slate-400">
                      {skill.replaceAll("_", " ")}
                    </p>

                    <p className="mt-3 text-4xl font-bold text-blue-400">
                      {score}
                    </p>

                    <p className="mt-1 text-xs text-slate-500">
                      Score
                    </p>

                  </div>

                )
              )}

          </div>

          {/* WEAK CONCEPTS */}

          <div className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-6">

            <h3 className="text-xl font-semibold">
              Weak Concepts
            </h3>

            {results?.weak_concepts?.length > 0 ? (

              <div className="mt-4 flex flex-wrap gap-3">

                {results.weak_concepts.map(
                  (concept, index) => (

                    <span
                      key={index}
                      className="rounded-lg bg-red-500/10 px-4 py-2 text-sm text-red-400"
                    >
                      {concept}
                    </span>

                  )
                )}

              </div>

            ) : (

              <p className="mt-3 text-slate-400">
                No major weak concepts identified.
              </p>

            )}

          </div>

          {/* COVERAGE GAPS */}

          <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-900 p-6">

            <h3 className="text-xl font-semibold">
              Coverage Gaps
            </h3>

            {results?.coverage_gaps?.length > 0 ? (

              <ul className="mt-4 space-y-3">

                {results.coverage_gaps.map(
                  (gap, index) => (

                    <li
                      key={index}
                      className="rounded-lg bg-slate-800 p-3 text-sm text-slate-300"
                    >
                      {gap}
                    </li>

                  )
                )}

              </ul>

            ) : (

              <p className="mt-3 text-slate-400">
                No major coverage gaps identified.
              </p>

            )}

          </div>

          {/* AI FEEDBACK */}

          <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-900 p-6">

            <h3 className="text-xl font-semibold">
              AI Feedback
            </h3>

            <p className="mt-4 leading-relaxed text-slate-300">
              {results?.narrative_feedback ||
                "No narrative feedback available."}
            </p>

          </div>

          {/* RECOMMENDATION */}

          <div className="mt-6 rounded-2xl border border-blue-500/20 bg-blue-500/5 p-6">

            <h3 className="text-xl font-semibold">
              Recommendation
            </h3>

            <p className="mt-4 leading-relaxed text-slate-300">
              {results?.recommendation ||
                "No recommendation available."}
            </p>

          </div>

          {/* BUTTONS */}

          <div className="mt-8 flex gap-4">

            <button
              onClick={resetInterview}
              className="rounded-xl border border-slate-700 px-6 py-3 text-sm font-medium hover:bg-slate-800"
            >
              ← Back to Candidates
            </button>

            <button
              onClick={() => setScreen("interview")}
              className="rounded-xl bg-blue-600 px-6 py-3 text-sm font-medium hover:bg-blue-500"
            >
              Review Interview
            </button>

          </div>

        </main>

      </div>
    );
  }

  // ==========================================
  // INTERVIEW SCREEN
  // ==========================================

  return (
    <div className="min-h-screen bg-slate-950 text-white">

      {/* HEADER */}

      <header className="border-b border-slate-800 bg-slate-950 px-6 py-4">

        <div className="mx-auto flex max-w-7xl items-center justify-between">

          <div>

            <h1 className="text-lg font-bold">
              AI Interview Agent
            </h1>

            <p className="text-xs text-slate-400">
              Technical Interview • ABTalks AI Cohort
            </p>

          </div>

          <div className="flex items-center gap-3">

            <div className="flex items-center gap-2 rounded-full bg-red-500/10 px-4 py-2 text-xs text-red-400">

              <span className="h-2 w-2 rounded-full bg-red-500" />

              LIVE INTERVIEW

            </div>

            <button
              onClick={finishInterview}
              disabled={loading || !sessionId}
              className="rounded-xl bg-blue-600 px-4 py-2 text-sm font-medium hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading
                ? "Finishing..."
                : "Finish Interview"}
            </button>

            <button
              onClick={resetInterview}
              disabled={loading}
              className="rounded-xl border border-slate-700 px-4 py-2 text-sm hover:bg-slate-800 disabled:opacity-50"
            >
              Exit
            </button>

          </div>

        </div>

      </header>

      {/* DASHBOARD */}

      <main className="mx-auto grid max-w-7xl grid-cols-12 gap-6 p-6">

        {/* LEFT SIDEBAR */}

        <aside className="col-span-3 rounded-2xl border border-slate-800 bg-slate-900 p-6">

          <div className="flex items-center gap-4">

            <div className="flex h-14 w-14 items-center justify-center rounded-full bg-blue-500/20 text-xl font-bold text-blue-400">

              {selectedCandidate?.name?.charAt(0)}

            </div>

            <div>

              <h2 className="font-semibold">
                {selectedCandidate?.name}
              </h2>

              <p className="text-sm text-slate-400">
                {selectedCandidate?.level}
              </p>

            </div>

          </div>

          {/* PROGRESS */}

          <div className="mt-8">

            <div className="flex items-center justify-between">

              <p className="text-xs text-slate-400">
                INTERVIEW PROGRESS
              </p>

              <p className="text-xs text-slate-500">
                Day {currentDay} / 4
              </p>

            </div>

            <div className="mt-4 h-2 overflow-hidden rounded-full bg-slate-800">

              <div
                className="h-full bg-blue-600 transition-all duration-500"
                style={{
                  width: `${Math.min(
                    (questionNumber / 8) * 100,
                    100
                  )}%`,
                }}
              />

            </div>

            <div className="mt-2 flex justify-between">

              <p className="text-sm text-slate-400">
                Question {questionNumber} / 8+
              </p>

              <p className="text-sm text-slate-500">
                Day {currentDay}
              </p>

            </div>

          </div>

          {/* TOPICS */}

          <div className="mt-8">

            <p className="text-xs text-slate-400">
              CURRICULUM TOPICS
            </p>

            <div className="mt-4 space-y-3">

              {selectedCandidate?.topics?.map(
                (topic, index) => (

                  <div
                    key={topic}
                    className="flex items-center gap-3 text-sm"
                  >

                    <span
                      className={
                        index < currentDay
                          ? "text-green-400"
                          : "text-slate-500"
                      }
                    >
                      {index < currentDay
                        ? "✓"
                        : "○"}
                    </span>

                    {topic}

                  </div>

                )
              )}

            </div>

          </div>

        
</aside>
        {/* CHAT */}

        <section className="col-span-9 flex h-[calc(100vh-120px)] flex-col overflow-hidden rounded-2xl border border-slate-800 bg-slate-900">

          {/* CHAT HEADER */}

          <div className="border-b border-slate-800 px-6 py-5">

            <div className="flex items-center justify-between">

              <div>

                <p className="text-xs text-blue-400">
                  AI INTERVIEWER
                </p>

                <h2 className="mt-1 text-lg font-semibold">
                  Technical Interview
                </h2>

              </div>

              <div className="text-sm text-slate-400">
                Question {questionNumber} / 8+
              </div>

            </div>

          </div>

          {/* ERROR */}

          {error && (

            <div className="mx-6 mt-4 rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-400">
              {error}
            </div>

          )}

          {/* MESSAGES */}

          <div className="flex-1 space-y-6 overflow-y-auto p-6">

            {messages.map((msg, index) => (

              <div
                key={index}
                className={`flex ${
                  msg.sender === "user"
                    ? "justify-end"
                    : "justify-start"
                }`}
              >

                <div
                  className={`max-w-[75%] rounded-2xl px-5 py-4 ${
                    msg.sender === "user"
                      ? "bg-blue-600 text-white"
                      : "border border-slate-800 bg-slate-800 text-slate-200"
                  }`}
                >

                  <p className="mb-1 text-xs opacity-60">
                    {msg.sender === "user"
                      ? "You"
                      : "AI Interviewer"}
                  </p>

                  <p className="leading-relaxed">
                    {msg.text}
                  </p>

                </div>

              </div>

            ))}

            {loading && (

              <div className="text-sm text-blue-400">
                AI is thinking...
              </div>

            )}

          </div>

          {/* INPUT */}

          <div className="border-t border-slate-800 p-5">

            <div className="flex gap-3">

              <input
                value={message}
                onChange={(e) =>
                  setMessage(e.target.value)
                }
                onKeyDown={(e) => {

                  if (e.key === "Enter") {
                    sendMessage();
                  }

                }}
                disabled={loading || !sessionId}
                placeholder={
                  sessionId
                    ? "Type your answer..."
                    : "Waiting for interview session..."
                }
                className="flex-1 rounded-xl border border-slate-700 bg-slate-950 px-5 py-3 text-white outline-none focus:border-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
              />

              <button
                onClick={sendMessage}
                disabled={
                  loading ||
                  !sessionId ||
                  !message.trim()
                }
                className="rounded-xl bg-blue-600 px-6 font-medium hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {loading ? "Sending..." : "Send"}
              </button>

            </div>

            <p className="mt-2 text-xs text-slate-500">
              Press Enter to send your answer
            </p>

          </div>

        </section>

      </main>

    </div>
  );
}

export default App;