import json
from pathlib import Path

EX = Path(__file__).resolve().parents[1] / "shot-design" / "examples"

last = {
    "beats": [
        {"id": "B1", "name": "establish", "goal": "put her alone with the letter",
         "duration_s": 4.5, "tension": 3, "knowledge_change": "the carriage is empty and she is not going anywhere"},
        {"id": "B2", "name": "reveal", "goal": "make the letter an object she can hold",
         "duration_s": 3.5, "tension": 5, "knowledge_change": "the apology has been written and folded already"},
        {"id": "B3", "name": "turn", "goal": "she decides not to send it",
         "duration_s": 4.0, "tension": 7, "knowledge_change": "the letter will stay with her"},
    ],
    "map": {"S01": "B1", "S02": "B2", "S03": "B3"},
}

interview = {
    "beats": [
        {"id": "B1", "name": "establish", "goal": "hand the initiative to the officer",
         "duration_s": 4.0, "tension": 3, "knowledge_change": "the officer believes he is winning"},
        {"id": "B2", "name": "omen", "goal": "show that the suspect recognises the photograph",
         "duration_s": 3.5, "tension": 5, "knowledge_change": "the photograph means something to him"},
        {"id": "B3", "name": "turn", "goal": "the power changes hands",
         "duration_s": 3.5, "tension": 9, "knowledge_change": "he is not the one being interviewed"},
        {"id": "B4", "name": "aftermath", "goal": "the officer recalculates",
         "duration_s": 4.0, "tension": 5, "knowledge_change": "the interview is over and he has lost it"},
    ],
    "map": {"S01": "B1", "S02": "B2", "S03": "B3", "S04": "B4"},
}

for name, spec in (("last-train", last), ("the-interview", interview)):
    path = EX / f"{name}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["beats"] = spec["beats"]
    for shot in data["shots"]:
        shot["beat_id"] = spec["map"][shot["id"]]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("updated", path.name)
