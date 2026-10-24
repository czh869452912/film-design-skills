# Beats

A shot list without beats is a pile of angles. Beats are where the audience's attention, pressure and release live; shots are how those beats are photographed.

A beat is **not** a shot. One beat can hold one shot (a 30-second take) or four (a burst). What defines a beat is that one thing changes and the audience's tension moves.

## 1. Beat taxonomy

| Beat | Job | Typical length | Tension |
|---|---|---|---|
| **establish** (建立) | place the world, the space, the rule | 1.5–4 s | 2–3 |
| **omen** (预兆) | something is about to happen; the world reacts | 1–2.5 s | 4 |
| **reveal** (显现) | the subject becomes legible | 1–3 s | 5–6 |
| **charge** (蓄力) | posture, energy, decision; the pause before | 1–3 s | 6–7 |
| **burst** (爆发) | motion starts; speed changes | 0.8–2.5 s | 8–9 |
| **impact** (命中) | contact, consequence, the loudest frame | 0.4–1.5 s | 10 |
| **aftermath** (余波) | the world absorbs the event | 1.5–4 s | 5–6 |
| **reaction** (反应) | a face or body registers what happened | 1–2.5 s | 4–6 |
| **turn** (转折) | what the audience knows flips | 1.5–3 s | 7–9 |
| **landing** (收束) | the new state is allowed to sit | 2–5 s | 2–4 |

Rules:

- **One job per beat.** A beat that is both reveal and impact is usually two beats.
- **Never two bursts adjacent.** The second has no contrast to borrow.
- **The charge beat is what makes the burst read.** Cutting the pause is the most common reason an action sequence feels weightless.
- **An impact beat owns a reaction, not just a contact.** The contact frame is one shot; who it lands on is the next. Steel meeting steel with nobody's hand or face in frame is texture, not story.
- **Land after the peak.** The last beat is the consequence, not the hit.
- **A beat can cross a cut, and a cut can happen inside a beat.** Cut where the beat's information changes, not on a stopwatch.

## 2. Tension curve

Write the tension number for each beat and check the shape before designing a single shot:

```text
establish 2 → omen 4 → reveal 6 → charge 7 → burst 9 → impact 10 → aftermath 5 → landing 3
```

- The peak sits at **70–85 %** of the runtime; everything after it is decay.
- A curve that rises monotonically from 8 to 10 has no contrast and will feel flat.
- Two peaks are allowed only if the second is higher and the dip between them is real.
- For a quiet piece, the same curve applies at low amplitude: the "impact" can be a hand closing.

## 3. Tempo templates

Durations are starting points for a **10–15 s** piece. Scale them proportionally; do not scale the number of beats.

### A. Arrival / descent (10 s) — the strong one enters

| Beat | Length | Shot logic |
|---|---|---|
| omen | 2 | wide, environment reacts (dust, light, birds) |
| reveal | 2 | the figure becomes legible, low angle |
| charge | 2 | the pause; posture, cloak, energy gathering |
| burst + impact | 2.5 | one move, one contact, one consequence |
| aftermath | 1.5 | debris, dust ring, the enemy's reaction |

### B. Duel exchange (12 s)

`establish 2 · probe 2 · first clash 1.5 · pause 1.5 · burst 2 · impact 1 · reset 2`

### C. Ultimate move (12 s)

`charge 3 · space change 2 · visual focus 2 · burst 2 · result 2 · landing 1`

### D. Standoff (8 s)

`establish 2 · eye contact 2 · pressure 2 · turn 1 · landing 1`

### E. Chase (10 s)

`establish 1.5 · pursuit 3 · obstacle 2 · near miss 1.5 · escape / catch 2`

### F. Emotional turn (10 s)

`normal 3 · disturbance 2 · recognition 2 · decision 2 · landing 1`

### G. Reveal / reversal (8 s)

`expectation 2 · detail that contradicts 2 · recognition 2 · aftermath 2`

### H. Farewell (12 s)

`together 3 · the thing unsaid 3 · separation 3 · the space after 3`

### I. Comedy (8 s)

`setup 2 · escalation 2 · turn 1.5 · topper 2.5`

- The joke lives in the **hold** after the turn, not in the turn.
- Cut *before* the laugh, hold *after* the wrongness.
- A comedy beat can have no camera movement at all; the frame is the straight man.

### J. Horror (10 s)

`normalcy 2.5 · anomaly 2 · approach 2 · reveal 1.5 · aftermath 2`

- Withhold the object: the approach is longer than the reveal.
- The aftermath is where the audience realises what they saw.
- Never reveal twice; the second reveal must be a different thing.

### K. Montage (6–10 s)

`unit 1.5 · unit 1.5 · unit 1 · unit 1 · landing 2`

- A unit is one action, one framing, one sound. No unit needs a plot.
- Units should differ on one axis only (size, or direction, or time), or the montage reads as repetition.
- The landing is the only shot allowed to be longer than two units.

### L. Hook (first 2 s)

`image 1 · question 1`

- The first frame must contain a **wrongness or a want**. No establishing shot.
- The first cut should confirm what the image promised, or contradict it.
- In vertical formats the hook has to survive the crop: subject centred, scale large.

### M. Training / progress (10 s)

`attempt 2 · fail 2 · adjust 2 · succeed 2 · cost 2`

- Failure must be physical and readable at thumbnail size.
- The adjust beat is the one that carries the story; do not skip it for time.
- The cost at the end prevents the sequence from being a montage of victories.

### Genre notes

| Genre | The beat that matters | What it needs |
|---|---|---|
| Comedy | the hold | a still frame, a straight face, one extra second |
| Horror | the approach | withholding, off-screen space, sound before image |
| Romance | the near-miss | proximity changes, hands, eyelines, no dialogue |
| Action | the charge | a pause before the burst, a consequence after |
| Drama | the turn | someone admits something they cannot take back |
| Mystery | the wrong detail | an object the audience notices before the character |

## 4. Beat sheet format

```json
"beats": [
  {"id": "B1", "name": "omen", "goal": "the street reacts before she appears", "duration_s": 2.0,
   "tension": 4, "knowledge_change": "something is coming"},
  {"id": "B2", "name": "reveal", "goal": "we see who it is", "duration_s": 2.0,
   "tension": 6, "knowledge_change": "the subject is the threat"}
]
```

Rules for the sheet:

- `duration_s` across all beats equals the piece duration.
- **A beat's duration comes from its function, not from dividing the runtime.** See `sequence-rhythm.md` §8: charge and landing are long, burst and impact are short, and the shape must read as a decision.
- `knowledge_change` is written from the audience's side, not the plot's.
- `tension` is 0–10 and used to check the curve, not to be precise.

## 5. Beats → shots

For each beat, decide the shot count by **information**, not by duration:

| Beat has | Shots |
|---|---|
| one action, one readable state | 1 |
| an action plus a reaction worth seeing | 2 (action, reaction) |
| a spatial reveal plus a subject reveal | 2–3 (wide, subject, detail) |
| a physical impact with environment consequence | 2 (impact, aftermath) |

If a beat needs more than four shots, it is probably two beats.

## 6. Beat-level checks

1. Read the `goal` lines in order. They should tell the story without any camera words.
2. Read the `tension` numbers. Is there a peak, and is it late?
3. Is there a charge beat before every burst? If not, why not?
4. Does the last beat land on a state, not on an event?
5. Does any beat exist only to move a character from A to B? Cut it or merge it.
6. **Traceability**: every fact written in a beat must be visible in a shot that owns it. If the beat says "he stumbles three steps" and the shot only lands on a knee, the fact has been lost between layers — move it into the shot or cut it from the beat.
7. **Load**: a beat that carries two facts needs two shots, or one shot of at least 2.5 s per fact. Splitting the shot is cheaper than writing a longer clause.
