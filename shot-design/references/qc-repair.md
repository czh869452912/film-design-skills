# QC and Repair

Review the sequence, then review each shot, then review the prompt. Do not review all three at once — each level hides different mistakes.

## 1. Sequence checks

| Check | Pass condition | If it fails |
|---|---|---|
| Turn | one clear change between the first and last shot | add a beat, or cut the sequence down to the beat that turns |
| Q&A chain | each shot answers and raises | delete the shots that do neither |
| Knowledge | the audience learns something specific at a specific moment | reorder — usually move the answer earlier for suspense, later for surprise |
| Ramp | intensity rises on one axis | flatten the middle before raising the end |
| Contrast | at least one quiet shot before the peak | insert a held beat |
| Duration shape | one real hold and one real snap; no even division unless declared ritual | run `render --format rhythm`; give length to a charge or a landing, shorten the impact |
| Cut priority | every cut has emotion + story declared; lower items only sacrificed deliberately | run `render --format cuts`; fix the highest undeclared item first |
| Beat traceability | every fact stated in a beat is visible in a shot that owns it | move the fact, or add the shot; never leave it only in the beat sheet |
| Previs gate | 3+ shots, a handoff, a contact or a side/height swap has rendered panels and an animatic before video | draw the panels, annotate, build the animatic; if skipped, set `previs_waived` with a reason |
| Landing | the final shot is the longest or shortest, and comes after the peak | trim or extend the last shot |
| Duration | fits the model's single-pass limit | split into clips, or cut beats |

## 2. Shot checks

| Check | Pass condition |
|---|---|
| One idea | the purpose can be said in one clause |
| Information load | every key fact has a shot long enough to carry it (≈2.5 s+), or the fact is split across shots |
| Contact ownership | the frame where weapons or hands meet contains a person (hand or face), or a reaction shot follows within one cut |
| Ban substitute | every ban names the positive action that replaces it (not "don't look" but "eyes stay on the shelf label") |
| Turn frame | the picture at the moment information changes is written and visible | 
| Mechanism fit | the chosen mechanism's failure mode is addressed in the card |
| Read | the values form 2–3 masses; squint test passes |
| Focus | one focal point; the highest contrast is on it |
| Movement | the move has a visible motive, and its middle frames compose |
| Action | one primary action, 2–4 observable performance cues |
| Cut | the outgoing frame hands something to the incoming frame |
| Continuity | screen side, eyeline, light direction, prop hand are stated |
| Sound | designed per beat, including what is absent |

## 3. Prompt checks

| Check | Pass condition |
|---|---|
| Executability | one action and one move per 3 s |
| Specificity | concrete nouns and visible changes, no "cinematic/beautiful/epic" |
| Bans | names this material's real collapse modes |
| Anchors | identity, wardrobe, prop, light direction repeated where they must persist |
| Timing | any timestamps are consecutive, ≥3 s, and match the duration |
| Language | dialogue and on-screen text preserved verbatim in their original language |

## 4. Storyboard and animatic checks

| Check | Pass condition | If it fails |
|---|---|---|
| Panel read | silhouette, camera height and screen direction legible in 2 s | redraw as a rougher panel; remove detail, add arrows |
| Panel honesty | the panel shows what the shot will actually contain | fix the shot card first, then redraw |
| Panel order | reading order matches shot order | renumber; never rely on the image model's ordering |
| Arrow provenance | every arrow comes from `storyboard.overlays` and is drawn by `annotate.py` | add overlays to the card; never ask the image model to draw marks |
| Corpus integrity | `eval.py` reports no doc or table issues | fix the table or the failing file before continuing |
| Annotation | every panel has `S## · size · angle · move · duration` | add it in the caption, not inside the drawing |
| Animatic timing | the cuts land on the beat boundaries | adjust `duration_s`, not the animatic |
| Animatic review | you can judge rhythm without reading the images | the panels are too detailed; simplify |

## 5. Failure modes and repairs

| Symptom in the generated clip | Likely cause | Repair |
|---|---|---|
| Flat, "stock footage" feel | no deliberate dial values; average framing | set 2 dials hard and add one contradiction |
| Confusing geography | line of action crossed, eyeline mismatch | reverse one shot's angle, or insert a neutral cutaway |
| Emotion reads as acting | abstract emotion words, too many cues | cut to 2 observable cues + one subtext line |
| Cuts feel abrupt | cut on the wrong beat; no shared element | cut on action/sound/shape; design the outgoing frame |
| One shot is beautiful, the sequence is dead | shots are illustrations, no Q&A chain | rewrite the chain; remove the prettiest shot if it answers nothing |
| Model adds cuts or subtitles | Seedance erring by commission | pass the specific bans and the one-take requirement to the prompt writer; that skill decides where they go |
| Model drops a shot | H3 erring by omission | reduce shot count, restate each shot's anchor, shorten dialogue |
| Faces slide / identity drifts | too many subjects or angles per shot | per-subject reference binding, fewer people, simpler action |
| Movement looks like drift | unmotivated camera | attach the move to a gaze, gesture, or approach |
| Everything at once | compound action and compound camera in one window | split the shot; one action + one move |
| Emotion peaks too early | the strongest frame is in the middle | reorder; save the largest size or lowest angle for the turn |
| A long single shot performs the action late and abruptly | no internal beat markers; H3/H3-style models pick their own moment | write beat windows in plain phrases ("for the first three seconds... from about four seconds...") and repeat what stays still |
| Prompt fights the reference image | card composition contradicts the generated keyframe | the keyframe wins: rewrite screen positions from the image, then update the card |
| Clip renders as asked but reads wrong | failure modes only cover "drawn wrong", not "understood wrong" | add a misread guard: framing, eyeline, sound or a reaction shot that tells the audience what this is; list the likely misreading in `bans` |

## 6. Risk statement

End every delivery with one line:

```text
Riskiest shot: S03 — the orbit around two characters while she speaks.
Why: compound move + dialogue + two subjects.
Fallback: lock the camera and let her turn into frame instead of orbiting.
```

A named risk with a fallback is worth more than a clean checklist.

## 7. Regeneration discipline

When one shot drifts:

1. Name the exact failure (wardrobe, direction, expression, prop state).
2. Keep the design intent and the continuity block unchanged.
3. Simplify the *action*, never the *design*.
4. Regenerate only that shot.
5. Compare against the frames before and after before accepting.

Do not rewrite the whole sequence because one shot failed — that creates new failures everywhere else.
