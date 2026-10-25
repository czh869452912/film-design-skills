# Changelog

## 0.6.0 — 2026-10-25

- Prefer whole four-/six-panel pages for NovelAI sequence drawing when readable, following the user's grid preference. Keep panel and shot identities separate.
- Separate stable character identities from per-panel appearances, current actions and global centers. Add a focused NovelAI page reference and a local-only prompt compiler.
- Add measured crop manifests tied to the exact source hash; preserve originals and distinguish layout review from content approval.
- Regression coverage includes per-occurrence coordinates, identity/state reuse, slot capacity, actual crop pixels, source preservation and failed preflight. Live tests improve cup-page consistency but still fail shared support; the duel page fails geometry/count. These are not production-quality passes.

## 0.5.0 — 2026-10-25

Rebuilt the foundational storyboard workflow around action/blocking, viewing choices, rough sequence, revision and timing. Earlier entries below describe historical rules, some superseded here.

- Separate beat, shot and panel; permit many-to-many beat/shot links, multiple panels per continuous shot and untimed drafts.
- Add shared structural representation; preserve legacy one-image-per-shot inputs. Derive shot timing from panels; export exact frame allocations and shot groups.
- Remove automatic cut-quality scores and artistic timing/framing penalties. Corpus reports are inventory only.
- Make mechanisms, emotion dimensions and model adapters optional; remove universal climax, camera-motion and shot-duration prescriptions.
- Preflight missing drawings; selected reference packs retain original shot/panel identity.
- Replace worked examples with a cup handoff and a spatially explicit duel; add an equal-duration display montage.
- Regression tests cover legacy/new examples, draft timing, malformed input, media paths, reference selection and decoded video frame order/count. Creative improvement still needs independent visual evaluation.


## 0.4.5 — 2026-10-24

Storyboard panels as the video model's reference kit (tested on H3, 10 s duel):

- New `scripts/build_refpack.py`: copies clean panels into an ordered pack
  (`01-S01.png` …), writes `manifest.json` + `refs.md` mapping `<Picture N>` → `[Shot N]`
  with a staging-only role. Wired into `selftest.py`.
- `handoff.md`: "storyboard pack" reference strategy, with the measured trade-offs —
  panels only keep staging but collapse the render to sketch style; keyframe + panels
  keeps the look with some sketch leakage; includes the four ordered fixes.
- `storyboard.md`: clean vs annotated panels — annotated copies are for review, clean
  copies are the reference input.
- `SKILL.md`: Step 7b builds the reference kit; panels are the default reference
  strategy for multi-shot pieces.

## 0.4.4 — 2026-10-24

Previs gate — the duel test skipped storyboards and paid for it:

- `SKILL.md` Step 6: a storyboard pass is now **required** before video handoff when
  the sequence has 3+ shots, a hand-off, a contact beat, a side/height swap, or runs
  over ~8 s. Writing the `storyboard` block is explicitly *not* the pass: render
  panels, annotate, build the animatic.
- `previs_waived` field for deliberate skips, with a stated reason.
- Validator warns on 3+ shots without storyboard specs.
- `qc-repair.md`: previs gate check added.
- Examples: Last Train and The Interview gained storyboard blocks.

## 0.4.3 — 2026-10-24

Finding from the H3 duel test (kimono vs sailor suit, 10 s): a textbook
object-insert at the impact beat lost to a reaction close-up, because at 1.2 s the
model cannot hold who is holding what.

- New rule: **a contact without a person is texture, not story** — the contact
  frame must contain a hand or a face, or the reaction follows in the next shot.
- `M07 Impact close` failure mode updated: an object-only frame severs
  who-hit-whom; pair with `M18`.
- `beats.md`: the `impact` beat owns a reaction, not only a contact.
- `qc-repair.md`: contact-ownership check added to the shot table.

## 0.4.2 — 2026-10-24

Rhythm, not division:

- `sequence-rhythm.md` §8: duration comes from the beat function (charge 2–4 s,
  burst 0.6–1.5 s, impact 0.4–1.2 s, landing 2–5 s), with five named shapes and a
  rule against dividing the runtime by the shot count.
- `shotlist.py --format rhythm`: duration bars, spread, detected shape, and a
  warning when a 4+ shot sequence is near-uniform without declaring `rhythm.shape: ritual`.
- Validator: near-uniform durations flagged; the longest shot flagged when its beat
  is `burst` or `impact`; `rhythm` block in the schema.
- `init` scaffold no longer divides evenly — it opens with a hold and contracts.
- Examples retimed: Descent 3.6/1.8/2.2/2.4; Last Train 5.0/3.0/4.0; Interview
  4.5/3.0/2.5/5.0 (peak moved to the officer's aftermath).
- Shot table and production sheet print the focal length.

## 0.4.1 — 2026-10-24

Findings from the blind A/B test (2 briefs × with/without skill, judged blind):

- New check: **orphan beats** — a beat with no shot is flagged.
- New render: `--format load` reports written cue/window density (a proxy, labelled as such).
- QC: information load per shot, ban-without-substitute, beat-to-shot traceability, and
  "renders as asked but reads wrong" failure mode.
- SKILL non-negotiables: a ban needs a positive substitute; split the shot instead of
  adding clauses.

## 0.4.0 — 2026-10-24

**Coverage**
- Mechanism library extended to M01–M42 (crowd, vehicle, montage, dream, comedy,
  horror, silhouette, overhead, performance, product) plus 8 camera modifiers.
- Beat library extended: comedy, horror, montage, hook, training/progress, and a
  genre note table.

**New tools**
- `scripts/annotate.py` — deterministic labels, arrows, sight lines, impact marks
  and orbit arcs from `storyboard.overlays`, plus a contact-sheet compositor.
  Image models no longer draw the annotations.
- `scripts/eval.py` — corpus statistics (mechanism coverage, beat distribution,
  framing distribution, cut readiness) and a table-integrity check for `templates.md`.
- `scripts/selftest.py` — regression gate for every tool, using the examples and
  synthetic panels; FFmpeg-dependent tests skip when ffmpeg is absent.
- `shotlist.py init` — valid scaffold from title/duration/aspect/shot count.
- `shotlist.py render --format timeline | csv`.
- `shotlist.py validate --strict` — warnings become failures.

**Animatic**
- Fades and audio track; label position; refactored to render per-shot video
  segments, which fixes faded-out stills (fading a single-frame image produced
  a black panel).

**Schema**
- `storyboard.overlays` (normalised [x, y] marks), `camera.turn_frame`,
  `framing.options` / `framing.chosen`, `mechanism` IDs.
- New checks: overlay types/coordinates, aspect ratio, vertical warnings,
  cut readiness, mechanism repetition.

**Composition**
- Vertical/9:16 framing and safe areas; colour and light structure.

**Docs**
- LICENSE (MIT), NOTICE, this changelog; README/SKILL/spec updated; all examples
  now carry beats, mechanisms and turn frames.

## 0.3.0 — 2026-10-24

- Split design from prompt specification: the skill no longer writes H3/Seedance
  prompt syntax; `model-adapters.md` replaced by `handoff.md`.
- MiniMax H3 treated as **Ref2VA** on this pipeline, not I2VA.
- Shot card schema v2 with `beats[]`, `beat_id`, references with role/preserve/exclude.
- Beat sheet, viewing-plan comparison, mechanism library, storyboard drawing
  brief, five-column sheet, cut readiness, animatic builder.
- `shotlist.py` rewritten: validate + renderers, mechanism list read from the docs.

## 0.1.0 — 2026-10-24

- Initial design: seven-step workflow, six-dial emotion system, composition and
  sequence references, shot card spec, worked example, validator.
