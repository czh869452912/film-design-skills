from pathlib import Path

OUT = Path("duel-test/panels/prompts")
OUT.mkdir(parents=True, exist_ok=True)

STYLE = ("storyboard panel, monochrome pencil sketch, rough greyscale, 16:9, cinematic composition, "
         "no text, dusk at an abandoned shrine courtyard, stone steps, mist, cedar trees; "
         "woman A: young woman in a deep red furisode kimono, long black hair tied low, wooden geta, "
         "black lacquered sheathed katana; woman B: young woman in a navy sailor uniform with white scarf, "
         "pleated skirt, black boots, short hair, drawn katana; ")

BASELINE = {
    "b1": "over the shoulder from behind B in the lower left foreground, her back to camera, the blade hanging at her right leg; A stands on the seventh stone step in the upper right, facing frame left, holding the hem of her kimono, the sheath horizontal at her waist; low angle, torii and backlight behind A",
    "b2": "close-up at A's waist, her thumb pressing the tsuba, the blade showing half a finger's width at the sheath mouth, kimono fabric and black lacquer filling the frame, shallow depth",
    "b3": "side medium shot; B climbs three stone steps and cuts diagonally downward with the blade high; A steps one step to her left, yielding, her geta sliding; both in profile, mist behind them",
    "b4": "medium close over A's shoulder; B's blade sweeps through the foreground and strikes A's black sheath, the lacquer chipping at the contact; A turns toward B's inside",
    "b5": "two-shot on the same axis; the tip of A's sheath rests under the edge of B's white scarf; B's blade points out into the fog; both stand still, mist around their feet",
}

SKILL = {
    "s1": "wide low side shot; A on the left third on the seventh step, the sheath horizontal in front of her waist angled fifteen degrees toward B, her right hand at the sheath mouth; B on the right third, left foot forward, the drawn blade lowered behind her leg; four empty steps between them; a dark stone lantern in the left foreground; a small torii in bright mist at the lower right; warm backlight from the upper right",
    "s2": "low medium close shot of B; her rear heel presses into the wet stone, the blade tip drawing a shallow arc behind her leg; the stone lantern is a black wedge on the left; mist behind",
    "s3": "side medium shot; B climbs three steps, her body covering the stone lantern; A revealed behind her with the sheath coming up; B's blade passes over her shoulder; A's geta leaves the stone by an inch; mist",
    "s4": "low close shot; the blade tip an inch from the black sheath; the blade bites the lacquer and a white line bursts open; bright mist behind; no faces in frame",
    "s5": "low medium shot pulling into a wide; only the sheath and a white line on the black lacquer are visible at first, then mist, steps and the small torii are revealed; A is now lower on the steps and B is above her, turning back; the positions have changed",
}

for prefix, table in (("baseline", BASELINE), ("skill", SKILL)):
    for shot, description in table.items():
        path = OUT / f"{prefix}-{shot}.txt"
        path.write_text(STYLE + description + "\n", encoding="utf-8")

print(f"wrote {len(list(OUT.glob('*.txt')))} prompt files")
