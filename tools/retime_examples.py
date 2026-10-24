import json
from pathlib import Path

EX = Path(__file__).resolve().parents[1] / "shot-design" / "examples"

# descent: hold the empty street, snap the reveal, hold the pause, land and settle
descent_durs = {"S01": 3.6, "S02": 1.8, "S03": 2.2, "S04": 2.4}
descent_beats = [
    {"id": "B1", "name": "establish", "goal": "the street is ordinary, and already wrong",
     "duration_s": 3.6, "tension": 3, "knowledge_change": "this is a normal afternoon"},
    {"id": "B2", "name": "reveal", "goal": "the figure becomes legible against the tear",
     "duration_s": 1.8, "tension": 5, "knowledge_change": "the arrival is a body, not a light"},
    {"id": "B3", "name": "charge", "goal": "it gathers itself before it moves",
     "duration_s": 2.2, "tension": 7, "knowledge_change": "it is about to do something"},
    {"id": "B4", "name": "impact", "goal": "the landing answers the crowd's hope",
     "duration_s": 2.4, "tension": 10, "knowledge_change": "this is not a rescue"},
]

# last train: hold the wide, tighten on the hands, hold the decision
last_durs = {"S01": 5.0, "S02": 3.0, "S03": 4.0}
last_beats = [
    {"id": "B1", "name": "establish", "goal": "put her alone with the letter",
     "duration_s": 5.0, "tension": 3, "knowledge_change": "the carriage is empty and she is not going anywhere"},
    {"id": "B2", "name": "reveal", "goal": "make the letter an object she can hold",
     "duration_s": 3.0, "tension": 5, "knowledge_change": "the apology has been written and folded already"},
    {"id": "B3", "name": "turn", "goal": "she decides not to send it",
     "duration_s": 4.0, "tension": 7, "knowledge_change": "the letter will stay with her"},
]

# interview: hold the table, quicken to the reversal, let the officer sit in it
interview_durs = {"S01": 4.5, "S02": 3.0, "S03": 2.5, "S04": 5.0}
interview_beats = [
    {"id": "B1", "name": "establish", "goal": "hand the initiative to the officer",
     "duration_s": 4.5, "tension": 3, "knowledge_change": "the officer believes he is winning"},
    {"id": "B2", "name": "omen", "goal": "show that the suspect recognises the photograph",
     "duration_s": 3.0, "tension": 5, "knowledge_change": "the photograph means something to him"},
    {"id": "B3", "name": "turn", "goal": "the power changes hands",
     "duration_s": 2.5, "tension": 9, "knowledge_change": "he is not the one being interviewed"},
    {"id": "B4", "name": "aftermath", "goal": "the officer recalculates",
     "duration_s": 5.0, "tension": 5, "knowledge_change": "the interview is over and he has lost it"},
]

specs = [
    ("descent", descent_durs, descent_beats, {"shape": "hold-snap-hold",
     "note": "hold the empty street, snap the reveal, hold the pause, let the dust settle"}),
    ("last-train", last_durs, last_beats, {"shape": "hold-snap-hold",
     "note": "hold the wide carriage, tighten on the hands, hold the decision"}),
    ("the-interview", interview_durs, interview_beats, {"shape": "wave",
     "note": "hold the table, quicken into the reversal, let the officer sit in it"}),
]

for name, durations, beats, rhythm in specs:
    path = EX / f"{name}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    for shot in data["shots"]:
        shot["duration_s"] = durations[shot["id"]]
    data["beats"] = beats
    data["rhythm"] = rhythm
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("updated", name, list(durations.values()))

# keep the test copy of descent in sync
src = EX / "descent.json"
dst = Path(__file__).resolve().parents[1] / "test-run2" / "descent.json"
dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
print("synced test-run2/descent.json")
