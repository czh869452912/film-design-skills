# Framing Decision

Camera mechanics are downstream of a viewing plan. Before choosing a lens or a move, decide **what the audience sees when** — then pick the mechanism that delivers it.

This is the "start / turn / end" ritual: compare two or three viewing plans for the same beat, using the same story, the same action, the same duration.

## 1. The three frames

For each plan, write three still frames. Not shot names: pictures.

| Frame | Question | What to write |
|---|---|---|
| **start** | what does the audience see before anything changes? | who is in frame, how large (fraction of height), what else is visible, what is withheld |
| **turn** | at the moment information changes, what is true of the frame? | what becomes visible or hidden, who moves in/out, what size change happens |
| **end** | what is the last image of the beat? | the final balance, the thing the eye rests on, what is now known |

If two plans have the same start, turn and end, they are the same plan — a different lens is not a different viewing plan.

## 2. Score the plans

| Criterion | Question |
|---|---|
| Information timing | when does the audience learn the key fact — before, with, or after the character? |
| Distance | are we judging, conversing, or inhabiting? |
| Simultaneity | does the plan let two relations be true at once (power + fear, intimacy + exit)? |
| Continuity cost | does it force a line crossing, a reverse, or a new geography? |
| Mechanism fit | which M-IDs from `templates.md` can actually deliver this plan in the runtime? |

Choose on information timing first: the same three frames can produce suspense, surprise or mystery depending only on order.

## 3. Comparison table

Write it before the shot cards, for beats where the viewing choice is still open:

```text
BEAT B2 — the figure becomes legible
Plan A  start: street WS, crowd small at the edges, sky empty
        turn:  tear opens high in frame, everyone still faces away
        end:   figure small inside the tear, crowd unchanged
        → knowledge: we see it before they do (suspense); distance: judging
Plan B  start: low MS on the crowd, heads up, sky out of frame
        turn:  heads tilt further, a bright rim enters top edge
        end:   figure only as a silhouette above them
        → knowledge: with the crowd (surprise); distance: inhabiting
Plan C  start: figure's boots in close-up against white sky
        turn:  tilt reveals the street far below
        end:   wide, figure tiny, crowd looking up
        → knowledge: after the crowd (mystery); distance: judging, late
```

Pick one, then put its frames in the shot card (`framing.options` + `framing.chosen`) and choose mechanisms (M-IDs) that can produce them.

## 4. Rules

- **Three plans maximum.** More means the beat is not defined yet.
- **One variable per plan.** If a plan changes size *and* order *and* POV, you have not isolated anything.
- **The turn frame is the plan.** If you cannot say what changes in the picture at the turn, the shot has no event.
- **Write the end frame as a picture, not a state of mind.** "The audience understands" is not a frame; "her hand flat on the pocket, profile against black glass" is.
- **Do not choose the plan that is easiest to prompt.** Choose the one whose information timing serves the beat, then find the mechanism that can execute it.
- **A plan may span two shots.** If the turn needs a cut (an eyeline, an insert), say which shot holds which frame.

## 5. Relation to mechanisms and beats

```text
beat (what changes) → viewing plan (start / turn / end) → mechanism IDs (how) → shot card (fields) → prompt skill
```

- `beats.md` defines *what* changes.
- This file defines *what the audience sees when*.
- `templates.md` defines *the camera arrangement that can deliver it*.
- The shot card records the choice; the prompt writer only executes it.

## 6. When to skip it

Skip the comparison when:

- the beat is a mechanical consequence of the previous one (a hit already decided);
- the runtime is too short for alternatives (under ~6 s total);
- the user has locked the shot.

Even then, write the turn frame. A shot whose turn frame you cannot state is not designed.
