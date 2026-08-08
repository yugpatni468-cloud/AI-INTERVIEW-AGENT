import json
from pathlib import Path


class CurriculumLoader:

    def __init__(self):
        data_path = Path(__file__).parent.parent / "data" / "curriculum.json"

        with open(data_path, "r", encoding="utf-8") as file:
            self.data = json.load(file)

    def get_day(self, day):
        for lesson in self.data["days"]:
            if lesson["day"] == day:
                return lesson
        return None