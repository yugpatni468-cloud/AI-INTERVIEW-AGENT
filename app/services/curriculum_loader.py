import json
from pathlib import Path


class CurriculumLoader:

    def __init__(self):

        data_path = (
            Path(__file__).resolve().parent.parent
            / "data"
            / "curriculum.json"
        )

        with open(
            data_path,
            "r",
            encoding="utf-8"
        ) as file:
            self.data = json.load(file)

    def get_day(self, day):

        if day is None:
            return None

        for lesson in self.data.get("days", []):

            if int(lesson["day"]) == int(day):
                return lesson

        return None

    def get_all_days(self):

        return self.data.get("days", [])