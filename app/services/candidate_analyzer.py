import json
from pathlib import Path

# Attempts-based prior thresholds used to seed adaptive difficulty for a
# PASSED mission. These intentionally mirror the tiers used elsewhere in
# the design (Strong / Moderate / Fragile) instead of the old single
# "difficult" cutoff, so the analyzer and the (future) difficulty engine
# agree on the same thresholds.
STRONG_PRIOR_MAX_ATTEMPTS = 1
MODERATE_PRIOR_MAX_ATTEMPTS = 3
# 4+ attempts on a PASSED mission => FRAGILE prior

# Legacy threshold, preserved as-is so existing consumers of
# "difficult_topics" (e.g. prompt_builder.py) keep working unchanged.
LEGACY_DIFFICULT_ATTEMPTS_THRESHOLD = 3


def _classify_prior(attempts: int) -> str:
    """Map an attempts count on a PASSED mission to a difficulty prior."""
    if attempts <= STRONG_PRIOR_MAX_ATTEMPTS:
        return "STRONG"
    if attempts <= MODERATE_PRIOR_MAX_ATTEMPTS:
        return "MODERATE"
    return "FRAGILE"


class CandidateAnalyzer:

    def __init__(self):
        data_path = Path(__file__).parent.parent / "data" / "candidates.json"

        with open(data_path, "r", encoding="utf-8") as file:
            self.data = json.load(file)

    def get_candidate(self, candidate_id):
        for candidate in self.data["candidates"]:
            if candidate["member"]["id"] == candidate_id:
                return candidate
        return None

    def analyze(self, candidate_id):
        """
        Classify every mission for a candidate into exactly one of three
        distinct states — PASSED, FAILED, or SKIPPED — and return an
        analysis object that both the existing prompt builder and the
        upcoming interview engine can consume.

        A mission with "passed": false is a FAILED mission: the candidate
        attempted it and did not clear the bar. This is intentionally kept
        separate from SKIPPED (never attempted) because the two mean very
        different things for personalization and weak-concept detection.
        Previously, FAILED missions matched neither the "passed" nor the
        "skipped" check and were silently dropped — that data loss is
        fixed here.

        Returns None if the candidate does not exist, so callers can use
        a simple `if candidate is None` check.
        """
        candidate = self.get_candidate(candidate_id)

        if not candidate:
            return None

        passed = []
        failed = []
        skipped = []
        difficult = []  # legacy field, preserved for existing consumers

        for mission in candidate["missions"]:
            if mission.get("skipped"):
                skipped.append(mission)
                continue

            if mission.get("passed") is True:
                attempts = mission.get("attempts", 1)

                enriched = dict(mission)
                enriched["prior"] = _classify_prior(attempts)
                passed.append(enriched)

                if attempts >= LEGACY_DIFFICULT_ATTEMPTS_THRESHOLD:
                    difficult.append(mission)

            elif mission.get("passed") is False:
                failed.append(mission)

            # A mission with neither "skipped" nor a "passed" key would be
            # malformed data and is intentionally left uncounted rather
            # than silently guessed at.

        eligible_days = [mission["day"] for mission in passed]
        failed_days = [mission["day"] for mission in failed]
        skipped_days = [mission["day"] for mission in skipped]

        return {
            "candidate": candidate["member"],
            "passed_missions": passed,
            "failed_missions": failed,
            "skipped_missions": skipped,
            "difficult_topics": difficult,
            "eligible_days": eligible_days,
            "failed_days": failed_days,
            "skipped_days": skipped_days,
            "signals": candidate["signals"],
        }