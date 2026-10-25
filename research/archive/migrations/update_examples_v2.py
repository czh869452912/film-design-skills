import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EX = ROOT / "shot-design" / "examples"

# ---------- descent ----------
p = EX / "descent.json"
d = json.loads(p.read_text(encoding="utf-8"))
mech = {"S01": "M01", "S02": "M02", "S03": "M05", "S04": "M10"}
turns = {
    "S01": "heads begin to lift; a balloon stops rising; the sky is still empty",
    "S02": "the boot leaves the tear; the street appears below the figure",
    "S03": "the fingers close; dust lifts around the knuckles",
    "S04": "knee and fist strike; the dust ring reaches the bottom edge of frame",
}
for shot in d["shots"]:
    shot.pop("template", None)
    shot["mechanism"] = mech[shot["id"]]
    shot["camera"]["turn_frame"] = turns[shot["id"]]

d["shots"][0]["framing"]["options"] = [
    {"name": "A", "start": "empty street, crowd small at both edges, sky blank",
     "turn": "every head tilts up, sky still blank", "end": "the same wide frame, all eyes on nothing",
     "tradeoff": "knowledge with the crowd; judging distance"},
    {"name": "B", "start": "medium on the crowd, heads up, sky out of frame",
     "turn": "a bright rim enters the top edge", "end": "crowd silhouettes, light above them",
     "tradeoff": "surprise; inhabiting distance"},
]
d["shots"][0]["framing"]["chosen"] = "A"

d["shots"][1]["framing"]["options"] = [
    {"name": "A", "start": "figure small inside the tear, sky fills the frame",
     "turn": "tilt down: street enters below, the tear rises out of frame",
     "end": "figure low in frame, street beneath it",
     "tradeoff": "we descend with the body; loss of the tear's scale"},
    {"name": "B", "start": "low wide, figure a silhouette against the tear",
     "turn": "figure falls through frame while the camera holds",
     "end": "figure lands small, tear still overhead",
     "tradeoff": "we watch from the ground; keeps scale, loses intimacy"},
]
d["shots"][1]["framing"]["chosen"] = "A"

p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# ---------- last train ----------
p = EX / "last-train.json"
d = json.loads(p.read_text(encoding="utf-8"))
mech = {"S01": "M31", "S02": "M19", "S03": "M32"}
turns = {
    "S01": "her hand stops moving; the letter lies flat on her knee",
    "S02": "the thumbnail presses the crease; the boat holds its shape",
    "S03": "the boat leaves the window light and disappears into the pocket",
}
for shot in d["shots"]:
    shot.pop("template", None)
    shot["mechanism"] = mech[shot["id"]]
    shot["camera"]["turn_frame"] = turns[shot["id"]]
p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# ---------- interview ----------
p = EX / "the-interview.json"
d = json.loads(p.read_text(encoding="utf-8"))
mech = {"S01": "M24", "S02": "M18", "S03": "M20", "S04": "M18"}
turns = {
    "S01": "the photograph comes to rest under the officer's fingers",
    "S02": "his eyes lift from the photograph to the officer",
    "S03": "the photograph reverses direction on the table",
    "S04": "his hand stops above the print and withdraws",
}
for shot in d["shots"]:
    shot.pop("template", None)
    shot["mechanism"] = mech[shot["id"]]
    shot["camera"]["turn_frame"] = turns[shot["id"]]
p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("updated", len(list(EX.glob("*.json"))), "examples")
