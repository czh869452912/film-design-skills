# Sequence Rhythm

A shot is not a picture; it is an answer to the question the previous shot asked.

## 1. The question-and-answer chain

Every cut should either **answer** something the viewer is now wondering, or **raise** a new question. A shot that does neither is filler.

The simplest chain is two shots: a look, then the object of the look. The strongest chains overlap — the answer to shot 2 is also the question of shot 3.

| Move | Pattern | Effect |
|---|---|---|
| Answer → question | look, then object | ordinary continuity |
| Question → answer delayed | look, two irrelevant shots, then object | tension, impatience |
| Answer before question | object, then the person who will find it | suspense, dramatic irony |
| Question unanswered | look, then something else entirely | mystery, or a cheat — use once |
| Wrong answer | object looks like the answer, then is not | reversal |

Write the chain in one line per shot before designing frames:

```text
S1 Q: where is she? -> S2 Q: what is she holding? -> S3 A: the letter. New Q: will she send it?
```

If the chain can be written without images, the sequence is a plot, not a film — go back and find what the frame adds.

## 2. What the viewer knows

This is the strongest emotional instrument and it is set by **order**, not by framing.

| Viewer vs. character | Viewer state | Use for |
|---|---|---|
| knows more | suspense, dread, helplessness | thriller, tragedy, farce |
| knows less | mystery, curiosity | reveal, investigation |
| knows the same | immersion, identification | action, intimacy |
| knows something false | reversal, shock | twist, betrayal |

To create suspense, place the answer before the question and let the character walk toward it. To create surprise, place the answer at the same moment the character receives it. The same three shots produce both; only the order changes.

## 3. The ramp

Emotion must be **built**, not declared. Over a sequence, increase intensity along one axis at a time:

- proximity (wide → close),
- pressure (air → occlusion),
- height difference (level → extreme),
- contrast (flat → chiaroscuro),
- pace (long holds → shorter shots),
- information (unknown → known).

**Contrast is the engine.** An action beat is more violent when it is sandwiched between two quiet shots. The climax works because everything before it was lower. If everything is at eight, nothing is.

Two structures that reliably work:

- **Calm before storm**: open pleasant and symmetric, then break the symmetry at the turn, then compress.
- **Locked observer**: hold one camera position for the whole scene while the action escalates inside the frame. The frame's refusal to move becomes the pressure.

## 4. Cutting craft

- **Cut on action.** Place the edit inside a movement so the eye follows motion instead of noticing the cut. Stage the action so it overlaps the edit point.
- **Cut on the look.** A glance is the strongest edit cue; the audience wants to see what the character sees.
- **Cut on sound.** A door, a bell, a breath can carry the cut and cover a geography change.
- **Cut on shape or motion.** Match the silhouette or the direction of movement across the cut.
- **Exits and entrances**: cutting while the subject is still partly in frame accelerates; clearing the frame and holding an empty shot for 1–2 s slows and implies time passing.
- **Do not cut for distance alone.** If the only change is size, move the camera; a cut promises new information.

## 5. Cut priority — the Rule of Six

When a cut feels wrong, do not fix it by feel. Check the six criteria in priority order; each one outweighs everything below it combined.

| # | Criterion | Weight | Question for this cut | Fix when it fails |
|---|---|---|---|---|
| 1 | Emotion | 51 % | does the cut serve what the audience should feel right now? | move the cut earlier or later; change which shot ends on the feeling |
| 2 | Story | 23 % | does the cut advance what the audience knows or wants? | cut to different information, not to a different angle |
| 3 | Rhythm | 10 % | is the length right for this beat's pace? | lengthen/shorten; never fix rhythm at the cost of 1 or 2 |
| 4 | Eye-trace | 7 % | does the eye land where the previous shot left it? | match the focal point, or add an insert to redirect |
| 5 | Screen plane | 5 % | does the 2D composition hold across the cut (left/right weight, horizon)? | reframe one side of the cut |
| 6 | 3D space | 4 % | is the geography still true (axis, eyeline, depth)? | insert a bridge, or re-establish |

Rules:

- **Serve 1 and 2 first.** A cut that is rhythmically perfect and emotionally wrong is a wrong cut.
- **Fix the highest failing item, not the most visible one.** A jump in screen plane is easier to see than a missed emotion, and easier to fix wrongly.
- **The order is also a debugging order.** If a cut is confusing, check space (6) last — audiences forgive geography long before they forgive a broken feeling.
- **This is a priority list, not a score.** The numbers say "what to sacrifice first", not "how good the cut is".

`shotlist.py render --format cuts` prints, for every cut, which of the six the design already specifies — a readiness check, not a quality score.

## 6. Screen direction and the line

- Draw the **line of action** (usually the sight line between two people, or the path of motion).
- Keep every camera on one side of that line for the scene, so left/right relationships stay stable.
- **Cross the line only with a reason**: a new sight line (a character turns to someone new), a character physically crossing, a moving camera crossing in one unbroken shot, or a neutral cutaway that resets geography.
- Once the geography is established, the audience can follow a return to an earlier setup without a re-establishing shot.
- **Eyelines must match**: if A looks frame right, B must look frame left in the reverse. A mismatch reads as two people in different rooms.
- Reversing screen direction inside a chase or travel sequence is a strong dramatic move — it reads as turning back, being stopped, or losing ground. Do not do it accidentally.

## 7. Rhythm and duration

Physical reality of reading time: a new composition needs roughly 1–1.5 s before the audience has absorbed it. Below that, cuts become texture.

| Shot function | Comfortable range | Notes |
|---|---|---|
| Establishing / geography | 2.5–6 s | needs time to be read |
| Dialogue line | 1.5–4 s | cut on the reaction, not the sentence end |
| Reaction / close-up | 1–3 s | shorter = shock, longer = weight |
| Insert / detail | 0.5–2 s | punctuation |
| Held final image | 2–5 s | the audience must be allowed to land |
| Long take | 8 s+ | needs internal change to justify the length |

Pacing rules:

- **Vary shot lengths in a pattern**, not randomly: long-short-short, or steady-short-short-short-then-long.
- **The last shot of a sequence should be the longest or the shortest** — never the middle.
- **Do not end on the peak**; end on the consequence. One beat after the climax gives the audience a place to stand.

## 8. Duration is a rhythm, not a division

Never divide the runtime by the shot count. Equal durations mean the edit has no opinion: nothing is being held, nothing is being rushed, and the sequence reads as a slideshow with sound.

**Set each duration from the beat's function**, then check the shape.

| Beat function | Starting range | Why |
|---|---|---|
| establish | 2.5–6 s | the audience must read the space once |
| omen | 1.0–2.5 s | a held wide is enough; more becomes a pause |
| reveal | 1.0–3.0 s | must be readable, not savoured |
| **charge** (蓄力) | 2.0–4.0 s | the pause is what makes the burst land |
| **burst** | 0.6–1.5 s | speed is made by leaving early |
| **impact** | 0.4–1.2 s | the shortest shot in the sequence |
| aftermath | 1.5–4.0 s | the world absorbs the event |
| reaction | 1.0–2.5 s | enough to register, not enough to act |
| turn | 1.5–3.0 s | the audience needs one beat to re-read |
| landing / hold | 2.0–5.0 s | the new state is allowed to sit |

Shape rules for any sequence of **4+ shots**:

1. **One long, one short.** At least one shot should be ≥1.6× the mean duration and one ≤0.7× the mean — unless the uniformity is deliberate (see 4).
2. **The longest shot belongs to a charge or a landing**, not to a burst or an impact. If the impact is the longest shot, the sequence has no speed.
3. **No two identical durations adjacent.** Identical neighbours flatten the stepping; ±10 % is enough to change the feel.
4. **Deliberate uniformity is allowed** — ritual, military repetition, comedy of repetition, a montage of identical acts. Declare it (`rhythm.shape = "ritual"` plus a note) so it reads as a decision rather than arithmetic.
5. **The last shot is long or short, never mid.** A mid-length final shot has no landing.

Shapes, as patterns of relative length:

| Shape | Pattern | Use for |
|---|---|---|
| **Hold → snap → hold** | long · short · short · long | arrival, reveal, impact, most action |
| **Accelerate** | long · medium · short · shortest | escalating pressure, chase, panic |
| **Decelerate** | short · short · medium · long | aftermath, realisation, grief |
| **Wave** | medium · long · medium · short · long | dialogue, negotiation, comedy build |
| **Ritual** | equal · equal · equal · equal | ceremony, repetition, deadpan |

A 10-second, 4-shot action piece is not 2.5/2.5/2.5/2.5. It is closer to **2.2 / 2.0 / 1.8 / 4.0**: hold the omen, tighten the reveal, snap the impact, then let the dust settle.

Check it mechanically: `shotlist.py render --format rhythm` prints the duration bar, the max/mean/min ratio, and flags uniformity that has not been declared.

## 9. Sequence shapes

**3-shot turn (10–12 s)**

```text
S1 establish the situation and the expected outcome
S2 break the expectation — new information, same space
S3 the character's response, held
```

**4-shot pressure (15 s)**

```text
S1 wide, calm, the world as it should be
S2 detail that contradicts it
S3 the character realizes — proximity increases
S4 the world continues, indifferent — pull back
```

**Single-take (15–30 s)**

```text
movement carries the camera through three states of the same space,
each state marked by a change in light, sound, or who is in frame
```

## 10. Transitions as punctuation

- A **cut** is a comma; a **dissolve** is a semicolon; a **fade** is a paragraph break.
- A **match cut** is a rhyme: use it to link two ideas, not two similar objects.
- An **occlusion wipe** (a body or object passing the lens) is the most believable transition in AI video because the passing object gives the model something physical to hide behind.
- **Never dissolve out of an emotional peak.** It dilutes the beat. Cut, or hold.

## 11. Sequence self-check

1. Write the Q&A chain. Every shot must sit in it.
2. Mark where the viewer's knowledge changes. That is the turn.
3. Check that intensity rises along one axis, not three at once.
4. Check screen direction and eyelines across every cut.
5. Check that the last shot is the longest or shortest, and that it lands *after* the peak.
