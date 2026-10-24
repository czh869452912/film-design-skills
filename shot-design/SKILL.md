---
name: shot-design
description: Design shots, encode emotion, and previz them for AI video generation (Seedance 2.5, MiniMax H3). Use when turning a scene into beats, a shot list, storyboard panels, an animatic, or the design brief behind per-shot prompts; when deciding framing, angle, lens, movement, staging, and composition; when a clip feels flat, confusing, or emotionally off. Covers beat sheets, a shot-template library, a six-dial emotion system, storyboard drawing rules, a validator, an animatic builder, and handoff to the model's prompt skill. This skill designs; it does not format final prompts.
compatibility: Portable to any agent that can read local files and run Python 3. No API calls required. Hands the design to the target model's prompt writer — for MiniMax H3, load h3-prompt-writing and write the Ref2VA six-section prompt there.
---

# Shot Design

A video model executes; it does not stage. This skill does the staging first — as decisions a camera operator and an editor would defend — and then hands those decisions to the model's prompt writer, which owns the prompt's structure.

Two source disciplines are fused here:

- **Coverage and continuity** (Katz, *Film Directing: Shot by Shot*): shot sizes, angles, lenses, the line of action, the question-and-answer chain, cutting on action, staging in depth.
- **Graphic composition** (Mateu-Mestre, *Framed Ink*): light/dark massing, silhouette, negative space, framing devices, line language, size relationships, "one quick read per frame".

Provenance and chapter/page anchors: `references/sources.md`.

## When to use / when not to

Use for:

- turning a script beat, a brief, or a mood into a shot sequence;
- choosing framing, angle, lens, movement, staging, and composition per shot;
- expressing an emotion or a power shift through camera decisions;
- preparing the design brief that a prompt writer turns into a Seedance 2.5 or MiniMax H3 prompt;
- diagnosing a generated clip that feels flat, confusing, unmotivated, or emotionally wrong.

Do not use for:

- full multi-scene production pipelines — use `3d-animation-short-generator` or the ad/MV skills;
- **final prompt formatting** — field names, section order, reference labels, retention markers, timing notation and word budgets belong to the model's prompt skill. For H3, load `h3-prompt-writing` and write the Ref2VA six sections there;
- generating the actual images or clips.

## Intake

Ask only for what is missing, at most three questions. Defaults in brackets.

1. **Beat**: what happens, and what changes? [one sentence]
2. **Emotion + knowledge**: what should the viewer *feel*, and what should they *know or suspect* at the end? [the brief implies both — state them explicitly]
3. **Budget**: total duration, aspect ratio, model, asset mode (text-only / one keyframe / reference kit). [10 s, 16:9, MiniMax H3 via the AutoDL workflow, reference kit → Ref2VA]

If the user gives only a mood ("make it sad"), do not invent a plot. Offer two contrasting beat readings and design the stronger one.

## Workflow

### Step 1 — One line, one turn

Write the logline and the emotional turn as a before/after:

```text
Logline: A courier waits under an awning for a handoff that will not come.
Turn: wary impatience → quiet ownership of the letter.
```

The turn is the contract for every later decision. A sequence without a turn is a mood board.

### Step 2 — Beats before shots

Read `references/beats.md`. Build the beat sheet first; a shot list without beats has no tension curve.

- every beat changes **one** thing: what the viewer knows, where the power sits, or what the character decides;
- pick a tempo template (arrival, duel, ultimate, standoff, chase, emotional turn, reveal, farewell) and adapt its lengths;
- write the tension numbers and check the curve: peak at 70–85 %, landing after it;
- state each beat as a question the shot will raise and answer (Q&A pattern in `sequence-rhythm.md`);
- budget by duration — see `handoff.md` §4; a 3-second window holds one action and one camera move;
- **never divide the runtime by the shot count.** Duration comes from the beat's function: hold the omen, snap the impact, let the landing sit (`sequence-rhythm.md` §8). A 10 s / 4-shot action piece is closer to 3.6 / 1.8 / 2.2 / 2.4 than to 2.5 × 4;
- a single shot over ~6 s still needs internal beat windows (`0–3 s stand`, `3–7 s lean`, `7–10 s hold`).

### Step 3 — Pick the emotion dials

Read `references/emotion-design.md`. Choose at most three dials per shot, and name the value for each:

| Dial | Low end | High end |
|---|---|---|
| Proximity | extreme wide → we judge | extreme close-up → we inhabit |
| Power (height) | high angle → diminished | low angle → dominant |
| Pressure | open space, air around subject | occlusion, edges, cramped frame |
| Stability | locked, level, symmetrical | handheld, tilted, unstable |
| Value | flat, even, legible | chiaroscuro, silhouette, hidden |
| Time | held, slow, long take | cut, brisk, compressed |

An emotion is a *setting of dials*, not an adjective in the prompt. "Lonely" is not a word to paste — it is a wide frame, a subject at the edge, a large dead area, and a held duration.

### Step 4 — Choose the viewing plan, then the mechanism

Camera mechanics are downstream of what the audience sees when. Do this in three parts.

**4a — Compare viewing plans** (`references/framing-decision.md`). For each beat whose viewing choice is still open, write 2–3 plans. Each plan is three still frames:

- **start**: who is in frame, how large, what else is visible, what is withheld;
- **turn**: what becomes visible or hidden at the moment information changes;
- **end**: the last image of the beat and what the eye rests on.

Judge on information timing first (does the viewer learn the fact before, with, or after the character?), then distance, simultaneity and continuity cost. Record the plans in `framing.options` and the winner in `framing.chosen`.

**4b — Pick mechanisms** (`references/templates.md`, IDs `M01`–`M32`). One spine mechanism that can deliver the chosen plan, optionally one modifier. Read the failure column of both before committing. Never stack two mechanisms whose camera moves in opposite directions.

**4c — Fill the shot card** (`references/shot-list-spec.md`):

1. What the frame must say (one clause).
2. Size and angle — what the audience should be able to read.
3. Lens and depth — compression vs. expansion, separation vs. context.
4. Composition — value masses first, then silhouette, then detail (`references/composition.md`).
5. Staging and screen direction — where bodies are, which way they travel, which side of the line.
6. Movement and its motivation — something in the frame must cause the move.
7. Entry, turn and exit frames — the three pictures the beat owns.
8. Sound — the beat's rhythm, not decoration.

The card is the design; the panel and the prompt are projections of it.

### Step 5 — Verify the sequence

- **Q&A chain**: each shot answers the previous question and raises the next. A shot that does neither is dead weight.
- **Eye-path handoff**: the last focal point of one shot sits near the first focal point of the next (`composition.md` §9).
- **Screen direction**: travel keeps its direction until a motivated reversal; the line of action holds across cuts.
- **Cut justification**: a cut must add subject, space, state, viewpoint, or time. If only distance changes, move the camera instead.
- **Cut priority** (`sequence-rhythm.md` §5): when a cut feels wrong, fix the highest failing item in Murch's order — emotion 51, story 23, rhythm 10, eye-trace 7, screen plane 5, space 4 — not the most visible one.
- **Density**: shots per duration, one primary action per beat, one camera move per shot (`handoff.md` §4).
- **Duration shape**: at least one real hold and one real snap; the longest shot should be a charge or a landing, never a burst or an impact. `render --format rhythm` shows the shape and flags even division.
- **Run** `python scripts/shotlist.py validate <file.json>` and fix every error; `render --format cuts` shows what each cut still leaves undeclared.

### Step 6 — Storyboard before any video handoff

Read `references/storyboard.md`. For each shot, add a `storyboard` block to the card: what the panel shows, arrows, annotation, simplification level.

**The previs gate.** A storyboard pass is **required** before handing a sequence to a video model when any of these is true:

- the sequence has **3 or more shots**;
- anything is **transferred between hands** (weapon, letter, cup, key);
- there is a **contact beat** (weapon on weapon, body on ground);
- two characters swap **screen sides, height or depth**;
- the piece is longer than ~8 s.

**Writing the `storyboard` block is not the pass.** The gate means: render at least one panel per beat (and every contact or handoff shot), annotate it with `annotate.py`, and build an animatic with `animatic.py` — then look at it. A block of prose in the JSON is a plan to do that, not the check itself.

Panels are **optional** only for a single shot, or for a sequence whose every frame is already fixed by approved reference images. If the gate applies and you skip it, record why in the shot list (`"previs_waived": "reason"`) — "ran out of time" is not a reason; the failures this avoids cost more than the panels.

Why: H3/Seedance execute a prompt from one anchor image. Without panels, there is no shared spatial reference for shots 2–5, and the failures are exactly the ones that look like model bugs — a second sheath appearing, a blade changing hands, a character jumping sides between cuts. Those are design holes that a rough panel catches for free.

- Readability beats beauty: silhouette, screen direction, horizon, light direction — then arrows, then detail.
- Default to **rough greyscale panels**; clean panels are for approval, not thinking.
- Produce the drawing brief with `render --format storyboard`. When the user wants images, hand each panel to the image skill (`gpt-image` or `novelai-image`) — that skill owns prompt syntax.
- **Draw the arrows with the script, not with the image model.** `annotate.py` adds the label bar and every overlay from `storyboard.overlays`, so marks stay legible and can be re-run when the card changes.
- Draw one panel per shot that carries a decision. A 6-shot sequence needs 6 panels; a 30 s sequence does not need 40.

### Step 7 — Build an animatic

```bash
python scripts/animatic.py shotlist.json --images storyboard --out animatic/animatic.mp4
```

The panels are concatenated at each shot's `duration_s`, with an `.edl.json` recording in/out times. Missing panels become labelled placeholders, so timing can be reviewed before the drawings exist. Review the animatic for rhythm, not for image quality: does the cut land where the beat does?

### Step 7b — Pack the panels as the video reference kit

```bash
python scripts/build_refpack.py shotlist.json --images storyboard --out refs/run1 --first-frame
```

Copies the **clean** panels into an ordered pack (`01-S01.png` …), writes `manifest.json` + `refs.md` with one role per picture, and maps `<Picture N>` → `[Shot N]`. Hand that pack to the prompt skill: one picture per shot, role "composition and staging", **sketch style excluded**, plus at most one colour keyframe if the look matters.

This is the default reference strategy for multi-shot pieces. A single hero keyframe fixes one frame; a panel pack fixes the staging of every shot, which is exactly what breaks in generation when it is missing.

### Step 8 — Hand off, do not pack

The design is finished when the brief in `references/handoff.md` §2 is complete: intent, shots, references with roles and exclusions, continuity, bans, beat windows.

Then, and only then:

- **For MiniMax H3**: load `h3-prompt-writing` and write the prompt there. On this project's AutoDL pipeline the mode is **Ref2VA** (full-reference, six sections), because the workflow takes up to 9 images and 3 audios — assets are references, not just a first frame. Decide each asset's role first (`first frame`, `identity`, `scene`, `prop`, `motion`, `voice`); one still can be both a first frame and an identity reference.
- **For any other model**: hand the same brief to that model's prompt guide.
- **Never** invent a field name, section header, label number, retention marker, or timing notation here. If the prompt skill rejects a design element as unrepresentable, change the design.

### Step 9 — QC and risk

Apply `references/qc-repair.md`. Report pass/fail per shot, name the riskiest shot, and give the repair action for each failure. Never ship a shot list without stating which shot is most likely to fail and why. Repairs are design changes — if a fix belongs in the prompt, say so and hand it back.

## Output contract

Deliver in this order, compactly:

1. **Design intent** — logline, turn, emotion curve (one line per beat).
2. **Beat sheet** — beat, length, tension, goal, what the viewer learns.
3. **Shot table** — id, duration, beat, mechanism, framing, movement, cut.
4. **Production sheet** — the five-column table (`render --format sheet`): time · shot · camera · picture & action · dialogue & sound.
5. **Shot cards** — one fenced JSON block for the whole sequence (schema in `shot-list-spec.md`).
6. **Storyboard brief** — per-panel drawing brief, plus panel images or an animatic when the user wants them.
7. **Handoff brief** — references with roles, attributes and exclusions; continuity; bans; beat windows (`handoff.md` §2).
8. **QC** — the checklist result plus the top risk and its repair.

For a single clip, collapse this into: intent, 1–3 shots, storyboard brief (optional), handoff, one risk.

When the user also asks for the finished prompt, say plainly which prompt skill produces it, load that skill, and pass it the brief. For MiniMax H3 that is `h3-prompt-writing` in Ref2VA mode. Do not paste a prompt from this skill as if it were spec-compliant.

Answer the user in their language. Dialogue, lyrics and on-screen text keep their original language. The **design intent** is the only part that must never change between model variants or prompt rewrites.

## Non-negotiables

- **One idea per shot.** If you cannot say what a shot is about in one clause, split it or drop it.
- **The turn frame decides the shot.** If you cannot name the picture at the moment information changes, the shot has no event — go back to the viewing plan.
- **Every shot changes information.** Emotion without new information is wallpaper.
- **A ban without a positive substitute is a hole.** Say what the body does instead of what it must not do; a prohibition alone gets executed as a missing limb.
- **A contact without a person is texture, not story.** If the frame holds only steel on steel, the audience cannot tell who hit whom; put a hand or a face in the contact, or cut to the reaction immediately.
- **Split the shot, do not add a clause.** If a shot carries two facts, or one fact that needs more than ~2.5 s, add a shot rather than piling constraints into one.
- **Movement needs a motive inside the frame** — a gaze, a gesture, a shape, an approach. "Push in for emotion" is not a motive; the motive is *what the push-in reveals or withholds*.
- **Design for the model's hands.** A 3-second beat gets one action and one move. Ambition that the model cannot execute reads as noise.
- **Design, don't specify.** Reference labels, section order, retention markers, `<d>` blocks and word budgets belong to the prompt skill. Producing them here creates prompts that are almost right, and therefore wrong.
- **Praise nothing you did not design.** No "cinematic", "beautiful", "epic" as a substitute for a decision.

## Reference map

| File | Read it for |
|---|---|
| `references/shot-grammar.md` | shot sizes, angles, lenses, movement, framing devices, transitions — and what each does to the viewer |
| `references/beats.md` | beat taxonomy, tension curves, tempo templates, beat → shot mapping |
| `references/framing-decision.md` | the start / turn / end comparison ritual before choosing a camera |
| `references/templates.md` | the mechanism library (M01–M32): arrangement, pairing, failure modes |
| `references/emotion-design.md` | the dial system, emotion recipes, irony/contradiction, performance cues |
| `references/composition.md` | value massing, silhouette, negative space, line language, scale, eye path, quick read |
| `references/sequence-rhythm.md` | Q&A chain, knowledge vs. unawareness, climax ramp, cut priority (Rule of Six), screen direction |
| `references/storyboard.md` | drawing spec: arrows, annotations, layouts, simplification, panel review |
| `references/shot-list-spec.md` | shot card schema, beat sheet, storyboard block, validation rules |
| `references/handoff.md` | division of labour, what to hand a prompt writer, reference roles, model budgets |
| `references/qc-repair.md` | pass/fail checks and repair actions |
| `references/worked-example.md` | one complete 12-second drama case, design through handoff |
| `references/worked-example-action.md` | the same workflow on a 10-second action beat: viewing plan, mechanisms, cuts |
| `references/sources.md` | book provenance, chapter and page anchors |

## Script

```bash
python scripts/shotlist.py init new.json --title "Last Train" --duration 12 --shots 3
python scripts/shotlist.py mechanisms                            # list M01–M42 with one-line jobs
python scripts/shotlist.py validate shotlist.json --strict        # warnings become failures
python scripts/shotlist.py render shotlist.json --format md       # review table
python scripts/shotlist.py render shotlist.json --format beats    # beat sheet
python scripts/shotlist.py render shotlist.json --format framing  # viewing plans, chosen one marked
python scripts/shotlist.py render shotlist.json --format cuts     # Rule-of-Six readiness per cut
python scripts/shotlist.py render shotlist.json --format sheet    # five-column production sheet
python scripts/shotlist.py render shotlist.json --format timeline # timing strip
python scripts/shotlist.py render shotlist.json --format rhythm   # duration shape + uniformity check
python scripts/shotlist.py render shotlist.json --format load     # cue density per shot
python scripts/shotlist.py render shotlist.json --format csv      # spreadsheet export
python scripts/shotlist.py render shotlist.json --format storyboard  # per-panel drawing brief
python scripts/shotlist.py render shotlist.json --format brief    # handoff brief for the prompt writer
python scripts/annotate.py shotlist.json --images storyboard --out annotated --sheet sheet.png
python scripts/build_refpack.py shotlist.json --images storyboard --out refs/run1 --first-frame
python scripts/animatic.py shotlist.json --images annotated --out animatic/animatic.mp4 --transition fade
python scripts/eval.py examples/                                  # corpus stats + doc integrity
python scripts/selftest.py                                        # regression gate: run after editing the tools
```

The scripts never design and never format model prompts. `shotlist.py` checks and prints the design (it reads the mechanism list straight out of `references/templates.md`); `annotate.py` draws labels and arrows; `build_refpack.py` turns clean panels into the ordered reference kit; `animatic.py` turns panels and durations into a reviewable clip; `eval.py` summarises a body of work and guards the docs against table corruption; `selftest.py` proves all of it still runs.
