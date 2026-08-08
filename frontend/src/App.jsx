import { useState } from "react";

function App() {
  const [screen, setScreen] = useState("candidates");
  const [selectedCandidate, setSelectedCandidate] = useState(null);
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);

  const candidates = [
    {
      id: 1,
      name: "Rahul Sharma",
      level: "Intermediate",
      completed: 24,
      skipped: 2,
      topics: ["RAG", "Vector DB", "Prompt Engineering"],
    },
    {
      id: 2,
      name: "Priya Singh",
      level: "Advanced",
      completed: 29,
      skipped: 1,
      topics: ["Agentic AI", "MCP", "RAG"],
    },
    {
      id: 3,
      name: "Arjun Verma",
      level: "Beginner",
      completed: 18,
      skipped: 5,
      topics: ["RAG", "Prompt Engineering"],
    },
  ];

  const startInterview = (candidate) => {
    setSelectedCandidate(candidate);

    setMessages([
      {
        sender: "ai",
        text: `Hello ${candidate.name}! Welcome to your ABTalks technical interview. Let's begin.`,
      },
      {
        sender: "ai",
        text: "First question: Can you explain what Retrieval-Augmented Generation (RAG) is and why we use it?",
      },
    ]);

    setScreen("interview");
  };

  const sendMessage = () => {
    if (!message.trim()) return;

    setMessages((previousMessages) => [
      ...previousMessages,
      {
        sender: "user",
        text: message,
      },
      {
        sender: "ai",
        text: "Good explanation. Now let's go one level deeper. What problems can occur if the retrieved documents are irrelevant?",
      },
    ]);

    setMessage("");
  };

  // ==========================================
  // CANDIDATE SCREEN
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
            Conduct a personalized technical interview based on the
            candidate's learning journey.
          </p>


          {/* CANDIDATES */}
          <div className="mt-12 grid gap-6 md:grid-cols-2 lg:grid-cols-3">

            {candidates.map((candidate) => (

              <div
                key={candidate.id}
                className="rounded-2xl border border-slate-800 bg-slate-900 p-6 transition hover:border-blue-500"
              >

                <div className="flex items-center justify-between">

                  <div className="flex h-12 w-12 items-center justify-center rounded-full bg-blue-500/20 text-xl font-bold text-blue-400">
                    {candidate.name.charAt(0)}
                  </div>

                  <span className="rounded-full bg-slate-800 px-3 py-1 text-xs">
                    {candidate.level}
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
                      {candidate.completed}
                    </p>
                  </div>


                  <div className="rounded-xl bg-slate-800 p-3">
                    <p className="text-xs text-slate-400">
                      Skipped
                    </p>

                    <p className="mt-1 text-lg font-bold">
                      {candidate.skipped}
                    </p>
                  </div>

                </div>


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


                <button
                  onClick={() => startInterview(candidate)}
                  className="mt-6 w-full rounded-xl bg-blue-600 px-4 py-3 font-medium hover:bg-blue-500"
                >
                  Start Interview →
                </button>

              </div>

            ))}

          </div>

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


        {/* RESULTS */}
        <main className="mx-auto max-w-6xl px-8 py-12">

          <p className="text-sm text-blue-400">
            TECHNICAL INTERVIEW REPORT
          </p>

          <h2 className="mt-2 text-4xl font-bold">
            {selectedCandidate?.name}
          </h2>

          <p className="mt-2 text-slate-400">
            Personalized interview based on ABTalks AI Cohort
          </p>


          {/* SCORE + ASSESSMENT */}
          <div className="mt-10 grid gap-6 md:grid-cols-3">

            {/* SCORE */}
            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-8">

              <p className="text-sm text-slate-400">
                Overall Score
              </p>

              <div className="mt-5 flex items-end gap-2">

                <span className="text-6xl font-bold">
                  78
                </span>

                <span className="mb-2 text-slate-400">
                  /100
                </span>

              </div>

              <div className="mt-5 h-3 overflow-hidden rounded-full bg-slate-800">

                <div
                  className="h-full rounded-full bg-blue-600"
                  style={{ width: "78%" }}
                />

              </div>

              <p className="mt-4 text-sm text-green-400">
                Strong Performance
              </p>

            </div>


            {/* TECHNICAL ASSESSMENT */}
            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-8 md:col-span-2">

              <h3 className="text-lg font-semibold">
                Technical Assessment
              </h3>

              <div className="mt-6 space-y-5">

                {[
                  ["RAG Understanding", 88],
                  ["Vector Databases", 82],
                  ["Agentic AI", 70],
                  ["Communication", 80],
                ].map(([skill, score]) => (

                  <div key={skill}>

                    <div className="mb-2 flex justify-between text-sm">

                      <span>{skill}</span>

                      <span>{score}%</span>

                    </div>

                    <div className="h-2 rounded-full bg-slate-800">

                      <div
                        className="h-full rounded-full bg-blue-500"
                        style={{ width: `${score}%` }}
                      />

                    </div>

                  </div>

                ))}

              </div>

            </div>

          </div>


          {/* FEEDBACK */}
          <div className="mt-6 grid gap-6 md:grid-cols-2">

            {/* STRENGTHS */}
            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-8">

              <div className="flex items-center gap-3">

                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-green-500/10 text-green-400">
                  ✓
                </div>

                <h3 className="text-lg font-semibold">
                  Strengths
                </h3>

              </div>

              <ul className="mt-6 space-y-4 text-sm text-slate-300">

                <li>✓ Strong understanding of RAG architecture</li>

                <li>✓ Good explanation of embeddings</li>

                <li>✓ Demonstrates practical problem solving</li>

                <li>✓ Communicates technical concepts clearly</li>

              </ul>

            </div>


            {/* IMPROVEMENTS */}
            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-8">

              <div className="flex items-center gap-3">

                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-yellow-500/10 text-yellow-400">
                  !
                </div>

                <h3 className="text-lg font-semibold">
                  Areas to Improve
                </h3>

              </div>

              <ul className="mt-6 space-y-4 text-sm text-slate-300">

                <li>• Explain retrieval failure cases in more depth</li>

                <li>• Improve understanding of MCP</li>

                <li>• Discuss engineering trade-offs more precisely</li>

                <li>• Provide more production-oriented examples</li>

              </ul>

            </div>

          </div>


          {/* ACTION BUTTONS */}
          <div className="mt-8 flex gap-4">

            <button
              onClick={() => setScreen("candidates")}
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


          {/* HEADER BUTTONS */}
          <div className="flex items-center gap-3">

            <div className="flex items-center gap-2 rounded-full bg-red-500/10 px-4 py-2 text-xs text-red-400">

              <span className="h-2 w-2 rounded-full bg-red-500" />

              LIVE INTERVIEW

            </div>


            <button
              onClick={() => setScreen("results")}
              className="rounded-xl bg-blue-600 px-4 py-2 text-sm font-medium hover:bg-blue-500"
            >
              Finish Interview
            </button>


            <button
              onClick={() => setScreen("candidates")}
              className="rounded-xl border border-slate-700 px-4 py-2 text-sm hover:bg-slate-800"
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
              {selectedCandidate?.name.charAt(0)}
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

            <p className="text-xs text-slate-400">
              INTERVIEW PROGRESS
            </p>

            <div className="mt-4 h-2 overflow-hidden rounded-full bg-slate-800">

              <div
                className="h-full bg-blue-600"
                style={{ width: "25%" }}
              />

            </div>

            <p className="mt-2 text-sm text-slate-400">
              Question 2 of 8+
            </p>

          </div>


          {/* TOPICS */}
          <div className="mt-8">

            <p className="text-xs text-slate-400">
              CURRICULUM TOPICS
            </p>

            <div className="mt-4 space-y-3">

              <div className="flex items-center gap-3 text-sm">
                <span className="text-green-400">✓</span>
                RAG
              </div>

              <div className="flex items-center gap-3 text-sm">
                <span className="text-yellow-400">●</span>
                Vector Databases
              </div>

              <div className="flex items-center gap-3 text-sm text-slate-500">
                <span>○</span>
                Prompt Engineering
              </div>

              <div className="flex items-center gap-3 text-sm text-slate-500">
                <span>○</span>
                Agentic AI
              </div>

              <div className="flex items-center gap-3 text-sm text-slate-500">
                <span>○</span>
                MCP
              </div>

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
                Question 2 / 8+
              </div>

            </div>

          </div>


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

          </div>


          {/* INPUT */}
          <div className="border-t border-slate-800 p-5">

            <div className="flex gap-3">

              <input
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    sendMessage();
                  }
                }}
                placeholder="Type your answer..."
                className="flex-1 rounded-xl border border-slate-700 bg-slate-950 px-5 py-3 text-white outline-none focus:border-blue-500"
              />

              <button
                onClick={sendMessage}
                className="rounded-xl bg-blue-600 px-6 font-medium hover:bg-blue-500"
              >
                Send
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