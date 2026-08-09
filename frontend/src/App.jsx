
import { useEffect, useState } from "react";
import "./App.css";

const API = "http://127.0.0.1:8000";

function App() {
  const [candidates, setCandidates] = useState([]);
  const [selectedCandidate, setSelectedCandidate] = useState(null);

  const [session, setSession] = useState(null);
  const [answer, setAnswer] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [finished, setFinished] = useState(false);
  const [scorecard, setScorecard] = useState(null);

  useEffect(() => {
    loadCandidates();
  }, []);

  async function loadCandidates() {
    try {
      setError("");

      const response = await fetch(
        `${API}/candidates`
      );

      if (!response.ok) {
        throw new Error(
          "Could not load candidates"
        );
      }

      const data = await response.json();

      setCandidates(data);
    } catch (err) {
      setError(err.message);
    }
  }

  async function startInterview(candidate) {
    try {
      setLoading(true);
      setError("");
      setFinished(false);
      setScorecard(null);
      setAnswer("");

      const candidateId =
        candidate.member?.id ||
        candidate.id;

      const response = await fetch(
        `${API}/interview/start`,
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            candidate_id: candidateId,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
            "Could not start interview"
        );
      }

      setSelectedCandidate(candidate);

      setSession({
        ...data,
        transcript: [
          {
            question: data.question,
            answer: "",
            day: data.day,
            topic: data.topic,
            is_followup: false,
          },
        ],
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function submitAnswer() {
    if (!answer.trim() || !session) {
      return;
    }

    try {
      setLoading(true);
      setError("");

      const currentQuestion =
        session.question;

      const response = await fetch(
        `${API}/interview/answer`,
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            session_id:
              session.session_id,
            answer_text: answer,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
            "Could not submit answer"
        );
      }

      const previousTranscript =
        session.transcript || [];

      const updatedTranscript = [
        ...previousTranscript.map(
          (item, index) => {
            if (
              index ===
              previousTranscript.length - 1
            ) {
              return {
                ...item,
                answer: answer,
              };
            }

            return item;
          }
        ),
      ];

      if (!data.ready_to_finish) {
        updatedTranscript.push({
          question: data.question,
          answer: "",
          day: data.day,
          topic: data.topic,
          is_followup:
            data.is_followup,
        });
      }

      setSession({
        ...session,
        question:
          data.question,
        day: data.day,
        topic: data.topic,
        is_followup:
          data.is_followup,
        question_number:
          data.question_number,
        distinct_days_asked:
          data.distinct_days_asked,
        ready_to_finish:
          data.ready_to_finish,
        transcript:
          updatedTranscript,
      });

      setAnswer("");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function finishInterview() {
    if (!session) return;

    try {
      setLoading(true);
      setError("");

      const response = await fetch(
        `${API}/interview/finish`,
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            session_id:
              session.session_id,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
            "Could not finish interview"
        );
      }

      setScorecard(data);
      setFinished(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function getCandidateName(candidate) {
    return (
      candidate.member?.name ||
      candidate.name ||
      "Candidate"
    );
  }

  function getCandidateId(candidate) {
    return (
      candidate.member?.id ||
      candidate.id ||
      "UNKNOWN"
    );
  }

  function getCandidateRole(candidate) {
    return (
      candidate.member?.role ||
      candidate.role ||
      candidate.member?.title ||
      "Technical Candidate"
    );
  }

  function getMissions(candidate) {
    return candidate.missions || [];
  }

  function getCompleted(candidate) {
    return getMissions(candidate).filter(
      (mission) =>
        mission.passed === true
    ).length;
  }

  function getSkipped(candidate) {
    return getMissions(candidate).filter(
      (mission) =>
        mission.skipped === true
    ).length;
  }

  if (session && selectedCandidate) {
    const progress =
      session.question_number || 1;

    return (
      <div className="app">
        <div className="interview-layout">
          <aside className="sidebar">
            <div className="profile-circle">
              {getCandidateName(
                selectedCandidate
              )
                .charAt(0)
                .toUpperCase()}
            </div>

            <h2>
              {getCandidateName(
                selectedCandidate
              )}
            </h2>

            <p>
              {getCandidateRole(
                selectedCandidate
              )}
            </p>

            <hr />

            <h4>
              INTERVIEW PROGRESS
            </h4>

            <div className="progress">
              <div
                className="progress-bar"
                style={{
                  width: `${Math.min(
                    progress * 12.5,
                    100
                  )}%`,
                }}
              />
            </div>

            <p>
              Question {progress} / 8+
            </p>

            <p>
              Days covered:{" "}
              {session.distinct_days_asked ||
                1}
            </p>

            <hr />

            <h4>
              CURRENT TOPIC
            </h4>

            <div className="topic">
              {session.topic}
            </div>

            <button
              className="secondary-btn"
              onClick={() => {
                setSession(null);
                setSelectedCandidate(null);
                setError("");
              }}
            >
              ← Back to Candidates
            </button>
          </aside>

          <main className="interview-panel">
            <div className="top-row">
              <div>
                <span className="brand">
                  AI INTERVIEWER
                </span>

                <h1>
                  Technical Interview
                </h1>
              </div>

              <div>
                Question{" "}
                {progress} / 8+
              </div>
            </div>

            {error && (
              <div className="error">
                {error}
              </div>
            )}

            <div className="question-card">
              <div className="question-meta">
                Day {session.day}
                {" · "}
                {session.topic}

                {session.is_followup && (
                  <span className="followup">
                    Follow-up
                  </span>
                )}
              </div>

              <h2>
                {session.question}
              </h2>
            </div>

            {!finished && (
              <div className="answer-area">
                <textarea
                  value={answer}
                  onChange={(e) =>
                    setAnswer(
                      e.target.value
                    )
                  }
                  placeholder="Type your answer..."
                  disabled={loading}
                  onKeyDown={(e) => {
                    if (
                      e.key === "Enter" &&
                      e.ctrlKey
                    ) {
                      submitAnswer();
                    }
                  }}
                />

                <button
                  className="primary-btn"
                  onClick={
                    submitAnswer
                  }
                  disabled={
                    loading ||
                    !answer.trim()
                  }
                >
                  {loading
                    ? "Processing..."
                    : "Send Answer →"}
                </button>
              </div>
            )}

            {session.ready_to_finish && (
              <button
                className="finish-btn"
                onClick={
                  finishInterview
                }
                disabled={loading}
              >
                {loading
                  ? "Finishing..."
                  : "Finish Interview"}
              </button>
            )}

            {scorecard && (
              <div className="scorecard">
                <h2>
                  Interview Results
                </h2>

                {scorecard.scores?.map(
                  (score, index) => (
                    <div
                      className="score-item"
                      key={index}
                    >
                      <strong>
                        {score.topic}
                      </strong>

                      <span>
                        {score.score}
                      </span>
                    </div>
                  )
                )}

                {scorecard.narrative_feedback && (
                  <p>
                    {
                      scorecard.narrative_feedback
                    }
                  </p>
                )}

                {scorecard.recommendation && (
                  <p>
                    <strong>
                      Recommendation:
                    </strong>{" "}
                    {
                      scorecard.recommendation
                    }
                  </p>
                )}
              </div>
            )}
          </main>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="header">
        <div>
          <span className="brand">
            AI INTERVIEWER
          </span>

          <h1>
            Technical Interview
          </h1>

          <p>
            Conduct a personalized
            technical interview based on
            the candidate's learning
            journey.
          </p>
        </div>
      </header>

      {error && (
        <div className="error global-error">
          {error}
        </div>
      )}

      {loading && (
        <div className="loading">
          Loading...
        </div>
      )}

      <div className="candidate-grid">
        {candidates.map(
          (candidate, index) => (
            <div
              className="candidate-card"
              key={
                getCandidateId(
                  candidate
                ) || index
              }
            >
              <div className="candidate-top">
                <div className="profile-circle">
                  {getCandidateName(
                    candidate
                  )
                    .charAt(0)
                    .toUpperCase()}
                </div>

                <span className="role">
                  {getCandidateRole(
                    candidate
                  )}
                </span>
              </div>

              <h2>
                {getCandidateName(
                  candidate
                )}
              </h2>

              <p className="candidate-id">
                {getCandidateId(
                  candidate
                )}
              </p>

              <div className="stats">
                <div>
                  <span>
                    Completed
                  </span>

                  <strong>
                    {getCompleted(
                      candidate
                    )}
                  </strong>
                </div>

                <div>
                  <span>
                    Skipped
                  </span>

                  <strong>
                    {getSkipped(
                      candidate
                    )}
                  </strong>
                </div>
              </div>

              <button
                className="primary-btn"
                onClick={() =>
                  startInterview(
                    candidate
                  )
                }
              >
                Start Interview →
              </button>
            </div>
          )
        )}
      </div>
    </div>
  );
}

export default App;