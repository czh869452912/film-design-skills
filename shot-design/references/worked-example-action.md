# Worked Example — "Descent" (10 s, action)

The counterpart to the drama example: same workflow, five beats, four shots, and
the decisions that make an action beat readable rather than busy.

Files: `examples/descent.json` (shot cards), panels and animatic in the development
workspace.

## 1. Intent

```text
Logline: A figure steps out of a tear in the sky and lands in the middle of a market street.
Turn:    the crowd waits for a savior -> the arrival is a threat.
Knows:   the crowd is relieved; the viewer sees that the tear is wrong.
```

## 2. Beats (tension 3 → 5 → 7 → 10)

| Beat | Length | Job | What the viewer learns |
|---|---|---|---|
| establish | 3.6 s | the street is ordinary, and already wrong | this is a normal afternoon |
| reveal | 1.8 s | the figure becomes legible | it is a body, not a light |
| charge | 2.2 s | it gathers itself | it is about to do something |
| impact | 2.4 s | the landing answers the crowd | this is not a rescue |

Peak at 87 %: late enough that the last beat can land, early enough that the
audience is not waiting for it.

## 3. Viewing plan before camera (shot S01)

| Plan | start | turn | end | Trade-off |
|---|---|---|---|---|
| A | empty street, crowd small at both edges, blank sky | every head tilts up, sky still blank | same wide frame, all eyes on nothing | suspense, judging distance |
| B | medium on the crowd, sky out of frame | a bright rim enters the top edge | crowd silhouettes, light above | surprise, inhabiting distance |

Chosen: **A**. The story is "they are waiting, and they are wrong to" — the viewer
needs to see the empty sky they are looking at. B hides the sky and gives the
model a light cue instead of a dramatic one.

The rule: choose on information timing, not on which plan looks better as a still.

## 4. Mechanisms

| Shot | Mechanism | Why | Failure it must avoid |
|---|---|---|---|
| S01 | `M01 Space omen` | the street is the subject, not the figure | detail drowning the omen |
| S02 | `M02 Descent` | the body must come down through frame | cutting before it settles |
| S03 | `M05 Wind-up` | buys the pause that makes the landing read | pose unreadable behind the silhouette |
| S04 | `M10 Landing` | the ground has to take the hit | no dust, no compression |

S02 uses a tilt as a **modifier** on M02, not a second mechanism: the camera does
not also push, orbit or crane.

## 5. Shot table

| Shot | Dur | Beat | Mechanism | Framing | Camera | Cut out |
|---|---|---|---|---|---|---|
| S01 | 3.6 s | establish | M01 | WS, eye | static | cut on sound |
| S02 | 1.8 s | reveal | M02 | MS, low | tilt down | cut on action |
| S03 | 2.2 s | charge | M05 | MCU, low | push in | cut on action |
| S04 | 2.4 s | impact | M10 | WS, ground | static | hold |

**The durations are not a division of 10 seconds.** 3.6 / 1.8 / 2.2 / 2.4: hold the ordinary street long enough to be read, snap the reveal so the body arrives fast, hold the pause before it moves, then let the landing and the dust take their time. Uniform 2.5 s × 4 was the first version of this example and it was wrong — it gave the same weight to an empty street and to a fist closing. `render --format rhythm` now flags that version.

## 6. Cut readiness

All three cuts score 100/100 on the Rule of Six checklist — not because they are
good, but because each cut declares emotion, story, rhythm, eye-trace, screen
plane and space. The check exists to catch the cuts that *don't*.

## 7. What the run changed

Two mechanisms were missing from the first library and were added because this
sequence needed them:

- `M31 Lone figure` — isolation in a wide. Needed by the drama example, absent here.
- `M32 Push to face` — realisation arriving. Needed by the quiet example.

A mechanism library grows from shots you actually designed, not from shots you
imagined designing.

## 8. Handoff

This example stops at the design. The MiniMax H3 prompt is written by
`h3-prompt-writing` in **Ref2VA** mode, from the brief produced by
`shotlist.py render --format brief`.
