# Shot List Spec

One JSON file per sequence, covering the whole preproduction chain: beats → shots → storyboard panels. It is the contract between design, drawing and prompts: if a shot changes, the card changes first; the panel and the prompt are rebuilt from it.

## 1. Schema

```json
{
  "title": "Descent",
  "intent": {
    "logline": "A figure steps out of a tear in the sky and lands in front of a crowd.",
    "turn": "the crowd is waiting for a savior -> it is not a savior",
    "audience_knows": "something is wrong with the arrival before the crowd does"
  },
  "target": {
    "model": "h3",
    "duration_s": 10,
    "aspect": "16:9",
    "mode": "ref2va"
  },
  "style": {
    "look": "monochrome storyboard for previz",
    "palette": "paper white, mid grey, black",
    "aspect": "16:9"
  },
  "beats": [
    {"id": "B1", "name": "omen", "goal": "the street reacts before anything appears",
     "duration_s": 2.0, "tension": 4, "knowledge_change": "something is coming"},
    {"id": "B2", "name": "reveal", "goal": "the figure becomes legible",
     "duration_s": 2.5, "tension": 6, "knowledge_change": "the arrival is a threat"}
  ],
  "shots": [
    {
      "id": "S01",
      "beat_id": "B1",
      "mechanism": "M01",
      "duration_s": 2.0,
      "purpose": "Make the street react before the figure exists in frame.",
      "emotion": {
        "target": "dread",
        "dials": {"proximity": 3, "power": 5, "pressure": 5, "stability": 2, "value": 8, "time": 6},
        "contradiction": "bright, ordinary daylight for a thing that should not exist"
      },
      "framing": {
        "size": "WS",
        "angle": "eye-level",
        "lens_mm": 28,
        "options": [
          {"name": "A", "start": "empty street, crowd small at both edges, sky blank",
           "turn": "every head tilts up, sky still blank", "end": "the same wide frame, all eyes on nothing",
           "tradeoff": "knowledge with the crowd; judging distance"},
          {"name": "B", "start": "medium on the crowd, heads up, sky out of frame",
           "turn": "a bright rim enters the top edge", "end": "crowd silhouettes, light above them",
           "tradeoff": "surprise; inhabiting distance"}
        ],
        "chosen": "A",
        "notes": "street furniture on both sides, sky occupying the top third"
      },
      "composition": {
        "value_masses": "white sky band, mid-grey street, black silhouettes of stalls",
        "focus": "the empty centre of the street",
        "negative_space": "the sky that will be torn open"
      },
      "staging": {
        "subjects": [{"name": "Crowd", "screen": "along both edges", "facing": "away from camera", "pose": "standing, still"}],
        "screen_direction": "none"
      },
      "camera": {
        "move": "static", "amplitude": "none", "speed": "none",
        "motivation": "the street has stopped; the camera should too",
        "start_frame": "ordinary street, people mid-step",
        "turn_frame": "heads begin to lift, a balloon stops rising",
        "end_frame": "same frame, everyone turned toward the sky"
      },
      "light": {"key": "flat overcast daylight", "ratio": "2:1", "palette": "grey, no colour"},
      "action": {
        "primary": "Every person in the street stops and turns toward the sky.",
        "cues": ["one shopper freezes mid-step", "a child's balloon stops rising"],
        "subtext": "They have been waiting for this, and they are wrong to."
      },
      "sound": {"diegetic": "street ambience cutting to silence, then a low hum", "dialogue": "none", "music": "none"},
      "storyboard": {
        "panel": "wide street, tiny crowd along both edges, all heads turned up, empty sky above",
        "arrows": ["thin dotted eye-lines up to the sky"],
        "overlays": [
          {"type": "sight", "from": [0.18, 0.72], "to": [0.42, 0.18]},
          {"type": "sight", "from": [0.82, 0.72], "to": [0.58, 0.18]}
        ],
        "annotation": "S01 · WS · eye · static · 2.0 s",
        "level": "rough"
      },
      "transition_out": {"type": "cut-on-sound", "matches": "the hum carries into the tear"},
      "continuity": ["overcast flat light", "street stalls on both sides", "no one faces camera"],
      "bans": ["no colour", "no hero pose", "no on-screen text"],
      "references": [],
      "render": {"status": "pending", "image": null}
    }
  ]
}
```

## 2. Required fields (validator-enforced)

| Field | Why |
|---|---|
| `id` | continuity and panels reference it |
| `beat_id` | every shot must serve a beat |
| `duration_s` | budgets, animatic timing |
| `purpose` | a shot without a job is filler |
| `framing.size` | the audience's distance is the first decision |
| `camera.move` | every shot owns a movement decision, including "static" |
| `action.primary` | one readable action |
| `transition_out.type` | the cut is part of the design |

Optional but expected: `mechanism` (an ID from `templates.md`), `framing.options` + `framing.chosen`, `camera.turn_frame`, `storyboard`, `render`.

## 3. Design rules

- **Mechanisms come from the library.** `mechanism` holds an ID (`M01`…) from `templates.md`; do not invent new names when a mechanism exists, and do not stack more than two.
- **Framing options are compared, not decorated.** When `framing.options` is present it holds 2–3 viewing plans, each with `start`, `turn`, `end` and a `tradeoff`; `framing.chosen` names the winner. This is the `framing-decision.md` ritual in data form.
- **`camera.turn_frame` is the picture at the moment information changes.** If you cannot write it, the shot has no event.
- **One primary action.** Secondary behaviour goes in `cues`, never as a second event.
- **One camera move** per shot.
- **Dials are 0–10**; use them to compare shots.
- **At most one contradiction per sequence.**
- **Screen direction** is `left-to-right`, `right-to-left`, `toward-camera`, `away-from-camera`, or `none`; a change needs `reversal_reason`.
- **Bans name this material's collapse modes.**
- **References carry a role, attributes and an exclusion**:
  `{"label": "<Picture 1>", "role": "identity + first frame", "defines": "…", "preserve": "fully", "exclude": "…"}`
  Label convention follows the target model (`<Picture 1>` for H3, `@Image 1` for Seedance).
- **A single shot over 6 s carries `beats`** inside the shot (`[{"window": "0-3s", "action": "…"}]`) so the model does not pick its own timing.
- **A storyboard block only adds what the card cannot show**: arrows, annotation, simplification level. If the panel needs a new design decision, fix the card first.
- **Overlays are drawn by script, not by the image model**: `storyboard.overlays` holds deterministic marks in normalised panel coordinates (0–1, origin top-left):
  `{"type": "arrow", "from": [0.2, 0.8], "to": [0.55, 0.3], "curve": 0.1, "label": "DESCEND"}`,
  `{"type": "sight", "from": [...], "to": [...]}` (dotted),
  `{"type": "impact", "at": [0.5, 0.6], "size": 0.06, "label": "IMPACT"}`,
  `{"type": "orbit", "at": [0.5, 0.5], "radius": 0.2, "start": -140, "end": -20, "label": "ORBIT CW"}`.
  Four overlays per panel maximum. `annotate.py` renders them.

## 4. Beat rules

- `beats[].duration_s` sums to the piece duration (±0.1 s).
- Every `shot.beat_id` exists.
- Tension values are 0–10; the peak should sit at 70–85 % of the runtime.
- A `burst` beat must follow a `charge` beat. (The validator cannot tell names apart reliably, so this is a manual check in `beats.md` §6.)

## 5. Validation rules the script runs

1. Unique ids; positive durations; total fits the model's single-pass limit.
2. Shot duration ≥ 1.2 s.
3. A single shot over 6 s without `beats` is flagged.
4. Required fields present and non-empty.
5. Every shot's `beat_id` exists; beat durations sum to the total.
6. Tension peak position flagged when outside 60–90 %.
7. `mechanism` must exist in `templates.md`; more than two mechanisms per shot is flagged.
8. Framing options: at least two, each with `start`/`turn`/`end`; `chosen` must name one of them.
9. Dials 0–10; screen-direction flips need `reversal_reason`.
10. Handoff readiness: references have `label`, `role`, `defines`; multi-shot sequences have `continuity`.
11. Storyboard readiness: a shot with a `storyboard` block has `panel` and `annotation`; a shot with camera movement other than `static` should have at least one arrow.
12. Overlays: known types only, coordinates are `[x, y]` pairs in 0–1, four per panel maximum.
13. Aspect: must be a known ratio; a vertical aspect with `WS`/`EWS`/`FS` framing is flagged (stack or crop instead).

## 6. Table view

| Shot | Dur | Beat | Mechanism | Framing | Camera | Action | Cut out |

One line per shot. Paragraphs belong in the card.
