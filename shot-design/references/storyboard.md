# Storyboard: Drawing Specification

A storyboard is a **checkable drawing**, not a poster. Its job is to let someone else verify the design before money is spent on video.

Priority order, and it is strict:

> **readability > narrative > continuity > beauty**

An ugly panel that shows the action clearly beats a beautiful one nobody can read.

## 1. What every panel must make readable

1. **Silhouette of the action** — what the body is doing, at a glance.
2. **Shot size and angle** — the panel's framing is the decision.
3. **Screen direction** — which way the subject faces and moves.
4. **Horizon / eye line position** — the height of the camera, drawn rather than labelled.
5. **One or two environmental anchors** — enough to place the space, no more.
6. **Light direction** — one value note, not a render.
7. **Arrows and annotation** — for what a still cannot show.

Everything else is optional: fabric detail, background crowd, texture, colour, rendering.

## 2. Arrow vocabulary

Draw arrows in a darker value than the panel; label them with 2–4 words.

| Meaning | Mark |
|---|---|
| camera push in / pull out | arrow perpendicular to the frame edge, toward / away from subject, label `PUSH` / `PULL` |
| camera pan / tilt | straight arrow along the motion, label the direction |
| camera orbit | curved arc around the subject, arrowhead showing direction, label `ORBIT CW/CCW` |
| tracking / follow | arrow parallel to the subject's path, label `TRACK` |
| whip / speed | double-headed arrow or three speed lines, label `WHIP` |
| subject movement | solid arrow from the body's current position to its next, label the verb |
| action path | dashed arrow for the trajectory of a weapon, fist, or fall |
| impact | short radial burst at the contact point, label `IMPACT` |
| line of sight | thin dotted line from eyes to target |
| focus shift | dotted line between two subjects with `RACK` |
| cut / fade | small `X` or diagonal slash in the panel corner, or a mark between panels |

Rules:

- **One camera arrow and one subject arrow maximum per panel.** More than that is a diagram, not a storyboard.
- The arrow's **start** is where the panel is; its end is the direction of change.
- Label in the language the production uses; keep labels 2–4 words.

## 3. Panel annotation

Fixed format, one line under or beside the panel:

```text
S03 · MS · low angle · orbit CW · 1.5 s
note: hold on recognition before the burst
```

- `S03` shot id, matching the shot list.
- size and angle, abbreviated consistently.
- movement, only if there is one.
- duration.
- one note line, only when the panel cannot show it (timing, sound, intent).

No paragraph annotations. If it needs a paragraph, the design is not resolved.

## 4. Simplification ladder

Draw at the level the decision needs:

| Level | Use for | Include | Omit |
|---|---|---|---|
| **thumbnail** (~2 cm) | beats, rhythm, composition blocks | 2–3 value masses, silhouette, one arrow | faces, props, text |
| **rough panel** | shot review, storyboard | silhouette, pose, screen direction, anchors, arrows | texture, secondary characters, detail light |
| **clean panel** | presentation, client review | the above plus simple value shading and consistent character shapes | rendering, colour, atmosphere |

Default to **rough panel**. Clean panels are for approval, not for thinking.

Three values only: paper white, one mid grey, black. If a panel needs a fourth value, it is a render.

## 5. Layout

| Layout | Use | Reading order |
|---|---|---|
| single card | iterating one shot; driving image-to-video | — |
| 4-grid (2×2) | ideation, comparing rhythm options | left→right, top→bottom |
| 6-grid (3×2) | sequence review of a 10–15 s piece | same |
| 9-grid (3×3) | beat sheet overview | same |

Grid tools are for **ideation**, not for a locked shot list. In practice an image model asked for a 4-panel grid will re-cast the content (a figure from panel 2 appears in panel 1), invent thick connector arrows between panels, and drift the framing per panel. If the panels must match the shot list exactly, render **one panel per request**; use the grid only while the sequence is still being decided.

- Keep the panel aspect ratio equal to the final video's. A 16:9 sequence on a 4:3 panel teaches the wrong composition. In 9:16, draw the stack (foreground hands / face / background light) rather than a squeezed wide shot.
- Leave a margin for the annotation strip; do not draw into it.
- Number panels in reading order, matching `shot_id`.
- In a grid, every panel gets the same value treatment, or the eye reads one panel as the important one by accident.

## 6. Consistency constraints

State these once per sequence and check every panel against them:

- character silhouette anchors (hair shape, coat length, posture),
- wardrobe blocks (one or two shapes that identify the character at thumbnail size),
- screen direction and which side each character occupies,
- prop hand and prop state,
- light direction,
- the horizon height.

If a panel breaks one, mark it deliberately (`REVERSE`), never silently.

## 7. What a panel must not try to be

- A finished illustration. Shading and texture hide design errors.
- A camera test. Perspective gymnastics are not the point; readable space is.
- A colour script. Value carries the read; colour is a later layer.
- A cast poster. More than three characters in a panel is usually a legibility failure.

## 8. Drawing for an image model

This file defines **what to draw**; the image skill defines how to phrase the request.

When the panel is produced by an image model:

- Ask for a **storyboard sketch / rough panel / greyscale layout**, not an illustration, not a poster.
- Keep one action per panel; models merge two actions into neither.
- Keep the camera simple: a panel that needs a complex move is better split into two panels.
- State the annotation as *text in the image* only if the model can render text reliably; otherwise leave the panel clean and put annotations in the caption beside it.
- Generate at the final aspect ratio; do not crop a square panel into 16:9 later.
- If identity matters, use one reference image and bind it to the character, not to the whole panel.

### Panels as the video model's reference kit

A panel is not only a check; for a multi-shot piece it is usually the best **staging reference** you can give the video model. Keep two copies:

| Copy | Purpose | Fed to a model? |
|---|---|---|
| clean panel | reference input: composition, staging, screen direction, light direction | yes, as `<Picture N>` per shot |
| annotated panel (`annotate.py`) | review: labels, arrows, impact marks | no — marks would render into the video |

Feed the pack with `build_refpack.py` (see `SKILL.md`): one picture per shot, declared as staging only, with the sketch style excluded. If the look matters, add **one** colour keyframe for palette and identity — the panels carry layout, the keyframe carries style.

## 9. Panel review

For each panel, answer in two seconds:

1. Can I tell what the body is doing?
2. Can I tell where the camera is?
3. Can I tell which way left and right are?
4. Does the panel answer its beat, or is it just a nice view?
5. Could a video model build this shot from this panel alone?

Any "no" sends the panel back to the shot list, not to the renderer.
