import json
from typing import Iterable, Optional


class PromptBuilder:
    """Build consistent prompts for the interview lifecycle."""

    def build_prompt(self, candidate_analysis, lesson):
        """
        Existing /interview/start prompt.
        Kept for backward compatibility with the working start endpoint.
        """
        candidate = candidate_analysis["candidate"]
        passed = candidate_analysis["passed_missions"]
        skipped = candidate_analysis["skipped_missions"]
        difficult = candidate_analysis["difficult_topics"]

        return f"""
You are a Senior Technical Interviewer.

Candidate Details:
Name: {candidate['name']}
Job Role: {candidate['jobRole']}
Experience: {candidate['yearsExperience']} years
Education: {candidate['education']}

Today's Interview Topic:
Day {lesson['day']} - {lesson['title']}

Learning Objectives:
{self._bullet_list(lesson['objectives'])}

Candidate Statistics:
Completed Missions: {len(passed)}
Skipped Missions: {len(skipped)}
Difficult Topics: {len(difficult)}

Interview Rules:
- Ask exactly one technical interview question.
- Do not answer the question yourself.
- Make the question specific to the learning objectives.
- Adjust the technical depth to the candidate's experience.
- Do not add scoring, explanations, or multiple questions.

Return only the question text.
""".strip()

    def build_next_question_prompt(
        self,
        candidate: dict,
        lesson: dict,
        difficulty: str,
        transcript: Iterable[dict],
        is_followup: bool = False,
        gap_type: Optional[str] = None,
    ) -> str:
        transcript_text = self._format_transcript(transcript)

        followup_instruction = (
            "Ask one focused follow-up that probes the identified gap."
            if is_followup
            else "Ask the next main interview question on this topic."
        )

        return f"""
You are conducting a technical AI interview.

Candidate:
- Name: {candidate['name']}
- Role: {candidate['jobRole']}
- Experience: {candidate['yearsExperience']} years

Topic:
- Day {lesson['day']}: {lesson['title']}
- Learning objectives:
{self._bullet_list(lesson['objectives'])}

Required difficulty: {difficulty}
Interview history:
{transcript_text}

Instructions:
- {followup_instruction}
- Ask exactly one question.
- Keep it grounded in practical engineering decisions.
- Do not reveal answers, grades, or internal reasoning.
- Return only the candidate-facing question.

Known gap type: {gap_type or "None"}
""".strip()

    def build_answer_classification_prompt(
        self,
        question: str,
        answer: str,
        lesson: dict,
        difficulty: str,
    ) -> str:
        return f"""
You are evaluating one technical interview answer.

Topic: Day {lesson['day']} - {lesson['title']}
Learning objectives:
{self._bullet_list(lesson['objectives'])}

Question:
{question}

Candidate answer:
{answer}

Expected difficulty: {difficulty}

Classify the answer fairly. Return exactly one JSON object with this schema:
{{
  "quality": "STRONG" | "PARTIAL" | "WEAK",
  "gap_type": "SURFACE_NO_DEPTH" | "NO_TRADEOFF_AWARENESS" |
              "NO_IMPLEMENTATION_GROUNDING" | "HEDGING_PARTIAL" |
              "CONFIDENTLY_WRONG" | null,
  "rationale": "one short sentence"
}}

Use gap_type only for PARTIAL or WEAK answers.
Do not include Markdown or any text outside JSON.
""".strip()

    def build_feedback_prompt(self, candidate: dict, scorecard: dict) -> str:
        return f"""
Write concise, constructive technical interview feedback.

Candidate: {candidate['name']} ({candidate['jobRole']})

Scorecard:
{json.dumps(scorecard, indent=2)}

Include:
- two specific strengths;
- the most important concepts to improve;
- a practical next learning step.

Use a supportive professional tone. Do not invent facts.
""".strip()

    @staticmethod
    def _bullet_list(items: Iterable[str]) -> str:
        return "\n".join(f"- {item}" for item in items)

    @staticmethod
    def _format_transcript(transcript: Iterable[dict]) -> str:
        entries = list(transcript)

        if not entries:
            return "No prior questions in this interview."

        sections = []

        for entry in entries:
            sections.append(
                f"Question: {entry.get('question', '')}\n"
                f"Answer: {entry.get('answer') or '[Not answered yet]'}"
            )

        return "\n\n".join(sections)