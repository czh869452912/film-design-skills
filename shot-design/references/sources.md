# Sources and Provenance

Two books were converted to Markdown and mined for this skill. Everything labelled *(synthesis)* below is original structure built on top of them — the books supply the principles, not the tables.

## 1. Primary sources

| ID | Work | Used for |
|---|---|---|
| K | Steven D. Katz, *Film Directing: Shot by Shot — Visualizing from Concept to Screen*, Michael Wiese Productions, 1991 | coverage, continuity, staging, lenses, angles, movement, POV |
| F | Marcos Mateu-Mestre, *Framed Ink: Drawing and Composition for Visual Storytellers*, Design Studio Press, 2010 | graphic composition, value massing, emotion through framing, continuity of the page |

Page anchors marked `F p.xxx` are the book's own page numbers. Katz is cited by chapter because the edition paginates inconsistently across printings.

## 2. Where each reference file comes from

### `shot-grammar.md`

| Content | Source |
|---|---|
| Shot-size ladder and what each size lets the audience read | F p.024 (long/medium/close/extreme close); K ch.6 (medium, full shot, close-up as reaction) |
| Close-up needs other close-ups; full shot carries body language | K ch.6 |
| Angle and height, including the *Citizen Kane* caution that angles have no meaning by themselves | F p.040–041; K ch.14 |
| Wide vs. long lens, compression, distortion, depth | F p.028–030; K ch.13 ("Compressed Depth", "Staging Patterns and Telephoto Lenses") |
| Dramatic circle of action, in/out of the action | K ch.13 |
| Staging in depth: separation (Welles) vs. intersection (Renoir) | K ch.13 |
| Movement vocabulary and motivation | F p.060–070 (camera move within the set, camera motivation, locking the camera); K ch.17–20 (pan, crane, tracking) |
| Framing devices: doorway, architecture, mirror | K ch.15 ("Framing Devices") |
| Open vs. closed framing and aesthetic distance | K ch.15 |
| Transitions, cut on action, clearing the frame, exits and entrances | K ch.7 (`Cutting On Movement`, `Exits and Entrances`, `Clearing the Frame`) |
| AI execution notes | *(synthesis)* from Seedance 2.5 / H3 behaviour, kept as budgets only |

### `emotion-design.md`

| Content | Source |
|---|---|
| Proximity / height / pressure / stability / value / time dials | *(synthesis)* built on F p.040–041, 042, 051, 075 and K ch.15–16 |
| Knowledge as the strongest lever; suspense vs. surprise by ordering | K ch.7 (`The Narrative Impulse`, `Using the Patterns`, Examples 1–3) |
| "Closing the circle", negative space as isolation / threat / scale | F p.042 |
| Conceal and reveal, obscuring a face to share a point of view | F p.051–053 |
| Power staging: size, eye height, lighting contrast, who looks | F p.057 (knowledge vs. unawareness); F p.024 |
| Contradiction move | *(synthesis)* — the books demonstrate it (e.g. locked camera against a chaotic scene, F p.068–070) but do not name it |
| Observable performance cues and subtext | *(synthesis)*; the principle "make them feel, do not tell them" is F p.015 |
| Sound as emotion | *(synthesis)*; H3's soundscape discipline in `h3-prompt-writing` |

### `composition.md`

| Content | Source |
|---|---|
| Compose value masses first, objects last; thumbnail and squint tests | F p.020–024, 034, 042–043 |
| One idea per frame; remove what does not contribute | F p.014; "Last Thoughts" |
| Contrast directs the eye; pools of light; silhouette | F p.019, 034, 075 |
| Silhouette and body language | F p.096–104 |
| Negative space | F p.042 |
| Cropping, extreme placement, symmetry as a statement | F p.049, 051 |
| Line language (horizontal/vertical/diagonal/curve) and lines pointing | F p.024, 044–047, 049 |
| Size relationships, big/medium/small, scale progression | F p.046, 049, 056 |
| Depth cues and atmospheric falloff | F p.018–019, 028; K ch.13 |
| Eye path, focus handoff between frames, screen direction | F p.055 (keeping the focal point), 114; K ch.6 |
| Tangencies and accidental mergers | F p.024 ("avoid tangencies and weird coincidences") |
| Day/night by reflection rather than sky value | F p.054 |

### `sequence-rhythm.md`

| Content | Source |
|---|---|
| Q&A chain; overlapping question/answer; order creates suspense | K ch.7 |
| Three connection types: temporal, spatial, logical | K ch.7 |
| Contrast and climax ramp; calm before the storm | F p.075–079; K ch.7 |
| Cut on action, cut on look, exits and entrances, clearing the frame | K ch.7, ch.6 |
| Line of action, triangle system, crossing the line, cutaways | K ch.6 |
| Eyeline and screen direction | K ch.6, ch.9 ("Sight Lines and Eye Contact") |
| Rhythm and shot-duration guidance | *(synthesis)* from K ch.7 pacing discussion and F p.114 (rhythm in cutting) |
| Sequence shapes | *(synthesis)* |

### `shot-list-spec.md`, `handoff.md`, `qc-repair.md`, `worked-example.md`

*(synthesis)*. Model behaviour claims come from the official Seedance 2.5 prompt guide, MiniMax H3 prompt-writing references, and published production notes. They are kept at the level of **execution budget** (duration, shot density, reference count, one action per window) because prompt syntax belongs to the model's prompt skill, not to this one.

### `beats.md`, `templates.md`, `storyboard.md`

*(synthesis)*. Beat taxonomy, tempo templates, the mechanism library (M01–M42 and the modifiers) and panel rules are original structures distilled from:

- rhythm and contrast: Katz ch.7 (`Narrative Motion`, Q&A patterns) and `Framed Ink` p.075–079 (contrast, ramping to a climax);
- the 180°/screen-direction and staging vocabulary: Katz ch.6, ch.9;
- the composition and value principles behind every panel: `Framed Ink` p.020–024 (chiaroscuro, quick read, checklist), p.042 (negative space), p.049 (big/medium/small), p.089 (the line);
- the "storyboard as a means to work out a shot, not a pretty picture" premise: Katz ch.3;
- the Rule of Six in `sequence-rhythm.md` §5: Walter Murch, *In the Blink of an Eye* (the published weights; the checks are ours);
- vertical framing and the six structural variables in `composition.md` §10–11: Bruce Block, *The Visual Story*.

### Public material that informed structure (not copied)

- [62656456/ai-film-skills](https://github.com/62656456/ai-film-skills) (Apache-2.0): an indexed mechanism library and a viewing-plan comparison before camera choice.
- [smixs/visual-skills](https://github.com/smixs/visual-skills) (CC BY 4.0, © Serge Shima): dramaturgy-first ordering, and physical facts over adjectives.
- [OpenAI Cookbook — Sora 2 Prompting Guide](https://github.com/openai/openai-cookbook/tree/main/examples/sora): one move plus one action per shot; actions as beats and counts.
- [BytePlus Seedance 2.5 prompt guide](https://docs.byteplus.com/zh-CN/docs/ModelArk/seedance-2-5-prompt-guide): duration and stage budgets.

No prose or code was copied from these; the mechanism IDs, the dial system, the overlay format and the validators are ours. See `NOTICE` for the full attribution list.

## 3. What the books do **not** say

- They do not discuss AI video generation. Every timing budget, stage rule, reference-binding rule, and ban strategy is added here.
- They do not provide an emotion lookup table. `emotion-design.md` §3 compresses many worked examples into a starting position; it is a planning aid, not a rule.
- They do not agree on the primacy of the rules. Katz repeatedly notes that the 180-degree rule is a convention audiences can read past; Mateu-Mestre notes his rules are "sometimes meant to be broken". Treat both as defaults with reasons, not laws.

## 4. Conversion notes

Source PDFs were converted with the MinerU Precision Extract API (v4, `vlm` model). The 474-page Katz volume exceeded the 200-page per-file limit and was split into three page ranges before conversion. Extracted Markdown lives outside the skill, under `build/extracted/` in the development workspace; it is not required at runtime.

Figure captions and image files were dropped: this skill encodes the verbal principles, not the artworks. Anyone using the skill for study should keep the books at hand — the diagrams carry the argument in ways text cannot.
