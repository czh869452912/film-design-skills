import json
from pathlib import Path

EX = Path(__file__).resolve().parents[1] / "shot-design" / "examples"

last = {
    "S01": ("empty carriage, she sits centre-left, the letter flat on her knee, two thirds of the frame empty",
            [], "S01 · WS · eye · static · 5.0 s"),
    "S02": ("hands folding the letter at seat height, her soft jaw at the top edge, dark glass behind",
            ["small push arrow at the frame edge"], "S02 · CU · low · push in · 3.0 s"),
    "S03": ("face in the left third, the paper boat at the bottom edge, black window filling the right",
            ["push arrow toward the window light"], "S03 · MCU · eye · push in · 4.0 s"),
}

interview = {
    "S01": ("two-shot across the table, officer nearer the camera, photo entering lower left",
            ["arrow of the photo sliding across the table"], "S01 · MS · eye · static · 4.5 s"),
    "S02": ("suspect's face right two thirds, eyes shadowed, photo edge bottom left",
            [], "S02 · MCU · low · static · 3.0 s"),
    "S03": ("his face and one hand, fingertip on the print at the bottom edge",
            ["arrow of the photo returning right to left"], "S03 · CU · low · static · 2.5 s"),
    "S04": ("officer left of centre, dark foreground shoulder, print bright at the bottom",
            [], "S04 · MCU · high · static · 5.0 s"),
}


def apply(name, table):
    path = EX / f"{name}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    for shot in data["shots"]:
        panel, arrows, annotation = table[shot["id"]]
        shot["storyboard"] = {
            "panel": panel,
            "arrows": arrows,
            "annotation": annotation,
            "level": "rough",
        }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("updated", name)


apply("last-train", last)
apply("the-interview", interview)
