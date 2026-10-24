# Changelog

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
