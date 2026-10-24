# Handoff and Model Budgets

This skill designs shots. It does not write final prompts.

A prompt is a **specification** — field names, section order, label rules, timing notation, retention markers, word budget — owned by the model's own prompt-writing skill. If this skill writes prompt syntax, it will produce a prompt that is almost right and therefore wrong.

## 1. Division of labour

| Layer | Owns | Does not own |
|---|---|---|
| `shot-design` (this skill) | intent, beats, framing, staging, composition, camera, action, sound design, reference roles, continuity, bans | field names, section order, `<Subject N>` numbering, retention markers, `<d>` tags, word counts, negative-prompt placement |
| Model prompt skill | final prompt structure and syntax | the design decisions behind it |

For MiniMax H3 on this project's AutoDL pipeline, the prompt skill is `h3-prompt-writing` in **Ref2VA** (full-reference, six sections). The workflow accepts up to 9 images and 3 audios, so assets are *references*, not merely a first frame. Load that skill and follow it exactly; hand it §2 below.

If a design decision seems impossible to express in the target's prompt syntax, the fix belongs in the prompt skill (or in the design), never in this file.

## 2. What this skill hands over

Emit a **design brief**, not a prompt. The prompt writer needs exactly these fields:

| Design field | What the prompt writer does with it |
|---|---|
| `intent.logline`, `intent.turn`, `intent.audience_knows` | `summary`: task type, subject, event, reference relationships |
| `references[]` (label, role, attributes, exclusions) | `subject_definitions` + `retention_analysis` entries |
| `continuity[]` per shot | the preservation clauses in `retention_analysis` and the "what stays unchanged" statements inside each shot |
| `framing`, `composition`, `light`, `staging`, `camera`, `action`, `sound` | `detailed_description`: composition, appearance and position, environment and light, action and state change, camera, sound |
| beat windows / `duration_s` | shot order and cut times; the total must equal the requested duration |
| `bans` | the model's exclusion slot (negatives list, global bans, or per-shot prose, whichever that guide specifies) |
| `references[].label` | the model's own label convention — `<Picture 1>` for H3, `@Image 1` for Seedance |

Do not rename, reorder, or pre-translate these into the target's fields. Give the raw design and let the prompt skill shape it.

## 3. Reference roles are the handoff contract

Every reference asset must arrive with a role and an exclusion. A role is what the asset is *allowed* to define:

`identity` · `wardrobe` · `scene/architecture` · `prop` · `motion` · `camera path` · `lighting/palette` · `voice timbre` · `music` · `first frame` · `last frame` · `storyboard/staging`

| Example | Role | Attributes to preserve | Exclusion |
|---|---|---|---|
| `<Picture 1>` | identity + first frame | dark bob, loose grey t-shirt, posture, machine on the left, drum light | do not take the room's clutter |
| `<Picture 2>` | storyboard/staging for [Shot 2] | subject placement, screen direction, horizon, light direction | do not take the pencil style, labels or arrows |
| `<Video 1>` | motion | only her leaning motion and its timing | do not take its clothing or scene |
| `<Audio 1>` | voice timbre | breathy delivery | do not copy its dialogue |

### The storyboard pack

The strongest default for a multi-shot piece: **one panel per shot becomes one `<Picture N>`**, each bound to its own shot. The panel fixes composition, staging, screen direction and light direction; the prompt fixes style, identity and performance. This is why the previs gate exists — the panels are not only a check, they are the input kit.

| Rule | Why |
|---|---|
| Feed **unannotated** panels | labels, arrows and impact marks leak into the render; annotate a copy for review |
| One picture per shot, in shot order | keeps `<Picture N>` ↔ `[Shot N]` mapping trivial |
| Declare every picture's role as **staging only** | otherwise the model averages the sketch style into the video |
| Add **one** style keyframe if the look matters | combined kit: panels for staging, one colour frame for palette/identity |
| Exclude sketch style, text and arrows explicitly | the panel's pencil texture is the most common leak |

Budget: H3 takes up to 9 images, so a 5-shot piece fits panels for every shot with room for a style keyframe. Beyond 9 shots, use panels for the shots that carry staging risk (contact, hand-off, side swap) and text for the rest.

**What to expect** (from a 10 s H3 test with five sketch panels):

| Kit | Staging fidelity | Style |
|---|---|---|
| one colour keyframe only | low — later shots drift, heads get cropped | good |
| panels only | high — composition follows each panel | **collapses to sketch**: the pencil style leaks into the video even when the prompt forbids it |
| keyframe + panels | high | mostly good, with sketch texture creeping into mid-sequence shots |

So: use the keyframe + panels kit as the default, and treat style leakage as a known failure. Fixes, in order: (1) put the style picture first and name it as the style reference; (2) convert the panels to toned greyscale or colour keys before feeding; (3) feed only the panels for the risky shots rather than all of them; (4) add the style-exclusion sentence to every shot, not only the first.

Rules:

- **One asset may define several subjects** (a person and a room in one still). Say so explicitly; the prompt writer must split them into separate definitions.
- **Never let an asset define more than one *aspect* of the same subject** without saying which wins.
- **State exclusions** for anything that could bleed in: background, other people, style, text.
- **Do not restate what a reference already defines** in the action description — that creates a conflict the model resolves by averaging.

## 4. Budgets that change the design

These are execution limits, not prompt syntax. They determine how many shots and beats survive.

| | MiniMax H3 (this pipeline) | Seedance 2.5 |
|---|---|---|
| Single pass | 4–15 s | 4–30 s |
| Reference assets | ≤9 images, ≤3 audio | up to 50, bound per scene |
| Practical shot ceiling | 2–3 (10 s), 3–5 (15 s) | stages ≥3 s each |
| Per-window content | one primary action + one camera move per ~3 s | same |
| Failure mode | errs by omission: drops shots, executes late | errs by commission: adds cuts, subtitles, BGM |

Density table:

| Piece length | Shots (H3) | Typical shape |
|---|---|---|
| 4–5 s | 1 | one action, one camera move |
| 6–8 s | 1–2 | setup → change |
| 10–12 s | 2–3 (or one take) | setup → turn → hold |
| 15 s | 3–4 | setup → turn → pressure → resolve |

A single shot over ~6 s still needs internal beat windows in the design (`0–3 s stand`, `3–7 s lean`, `7–10 s hold`), because otherwise the model picks its own moment. How those windows are written into the prompt is the prompt skill's business.

## 5. Handoff checklist

Before handing off:

- [ ] every shot has framing, camera (including "static"), one primary action, sound
- [ ] every reference has a model-native label, a role, attributes to preserve, and exclusions
- [ ] continuity is stated per shot, as things that must not drift
- [ ] bans name this material's plausible collapses, not generic quality words
- [ ] beat windows sum to the requested duration
- [ ] no field name, section header, label number, or marker invented here

If the prompt skill rejects a design element as unrepresentable, revise the design — do not smuggle the element in as prose.
