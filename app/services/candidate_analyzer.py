import json
from pathlib import Path


STRONG_PRIOR_MAX_ATTEMPTS = 1
MODERATE_PRIOR_MAX_ATTEMPTS = 3
LEGACY_DIFFICULT_ATTEMPTS_THRESHOLD = 3


def _classify_prior(attempts: int) -> str:

    if attempts <= STRONG_PRIOR_MAX_ATTEMPTS:
        return "STRONG"

    if attempts <= MODERATE_PRIOR_MAX_ATTEMPTS:
        return "MODERATE"

    return "FRAGILE"


class CandidateAnalyzer:

    def __init__(self):

        data_path = (
            Path(__file__).resolve().parent.parent
            / "data"
            / "candidates.json"
        )

        with open(
            data_path,
            "r",
            encoding="utf-8"
        ) as file:
            self.data = json.load(file)

    def get_candidate(
        self,
        candidate_id: str
    ):

        for candidate in self.data["candidates"]:

            member = candidate.get("member", {})

            if member.get("id") == candidate_id:
                return candidate

        return None

    def analyze(
        self,
        candidate_id: str
    ):

        candidate = self.get_candidate(candidate_id)

        if candidate is None:
            return None

        passed = []
        failed = []
        skipped = []
        difficult = []

        for mission in candidate.get("missions", []):

            if mission.get("skipped") is True:

                skipped.append(mission)
                continue

            if mission.get("passed") is True:

                attempts = mission.get("attempts", 1)

                enriched = dict(mission)

                enriched["prior"] = _classify_prior(
                    attempts
                )

                passed.append(enriched)

                if attempts >= LEGACY_DIFFICULT_ATTEMPTS_THRESHOLD:
                    difficult.append(mission)

            elif mission.get("passed") is False:

                failed.append(mission)

        return {
            "candidate": candidate["member"],
            "passed_missions": passed,
            "failed_missions": failed,
            "skipped_missions": skipped,
            "difficult_topics": difficult,
            "eligible_days": [
                mission["day"]
                for mission in passed
            ],
            "failed_days": [
                mission["day"]
                for mission in failed
            ],
            "skipped_days": [
                mission["day"]
                for mission in skipped
            ],
            "signals": candidate.get(
                "signals",
                {}
            ),
        }