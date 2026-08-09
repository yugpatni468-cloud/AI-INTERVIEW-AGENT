import json
from pathlib import Path

from fastapi import APIRouter


router = APIRouter(
    prefix="/candidates",
    tags=["Candidates"]
)


DATA_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "candidates.json"
)


@router.get("")
def get_candidates():

    with open(
        DATA_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    return data["candidates"]