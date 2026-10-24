# Emotion Design

Emotion is not an adjective added to a prompt. It is the result of six decisions about how the audience is placed, and one decision about what the audience knows.

## 1. The one principle

> The audience feels what the frame does to them, not what the description says.

So before choosing anything, answer two questions:

1. **Knowledge**: does the viewer know more than the character (suspense), less (mystery), the same (immersion), or something false (reversal)? This is the strongest emotional lever available, and it is decided by shot order, not by framing.
2. **Placement**: is the viewer a witness, a confidant, a target, or the character? That is decided by proximity, height, and whether the subject can see the lens.

Everything below tunes placement. Knowledge is decided in `sequence-rhythm.md`.

## 2. Six dials

Set a value for each. A shot with no deliberate setting falls back to the average of everything ever shot.

| Dial | 0 | 5 | 10 |
|---|---|---|---|
| **Proximity** | extreme wide — we judge | medium — we converse | extreme close — we inhabit |
| **Power** | high angle, subject small and low | eye level | low angle, subject fills and towers |
| **Pressure** | open space, air on all sides | normal margins | edges, occlusion, cramped frame, no exit |
| **Stability** | locked, symmetrical, level | steady handheld | tilted, shaking, off-balance |
| **Value** | flat, even, everything legible | key/fill contrast | chiaroscuro, silhouette, face withheld |
| **Time** | a held long take | ordinary cutting | fast cutting, compressed action |

Two rules:

- **Change at most two dials per cut.** A cut that moves proximity *and* power *and* stability reads as chaos, not as emphasis.
- **Hold one dial against the emotion.** This is the difference between a designed shot and a stock one (see §5).

## 3. Emotion recipes

Each row is a starting position, not a formula. The last column is the counter-move that keeps it from becoming a cliché.

| Emotion | Proximity | Power | Pressure | Stability | Value | Time | Counter-move |
|---|---|---|---|---|---|---|---|
| Isolation | EWS/WS, subject small | eye or slightly high | low pressure but large dead area | locked | flat, pale, low contrast | long hold | **ECU of hands** after the wide — isolation inside the body |
| Oppression | MS, subject boxed | high or low (both work) | 9 — occlusion, frame edges, ceiling | locked | heavy shadow mass above and beside | normal | **release the frame once**, early, so the audience remembers air |
| Threat | MS→CU on the threat, not the victim | low angle on threat | high | slow handheld | silhouette, backlight, one hot spot | slow | **hold on the victim's back**, never show the threat's face |
| Suspense | WS with both elements | eye | high | locked | pools of light, dark exits | long, uncut | **cut earlier than expected**, on the wrong beat |
| Intimacy | MCU/CU, two faces, equal size | eye | low, soft edges | gentle handheld or locked | soft, close values, warm | slow, unhurried | **one hard cut to a detail** — a hand, a cup — to prove the room is real |
| Grief (restrained) | MS or WS, not CU | eye or slightly high | moderate | locked | muted, flat, overcast | very long hold | **CU on the face at the moment it fails**, once |
| Shame / exposure | CU, face lit, surroundings dark | slightly high | 8 — nowhere to look | locked | hard key, no fill | still | **cut to the room's indifference** (a chair, a window) |
| Rage / loss of control | MS→CU with a tilt | low or dutch | high | handheld, unstable | high contrast, hot highlights | fast | **one dead-still frame** before the outburst |
| Power / dominance | low angle, subject occupies 2/3 | low | 8 — the other body is cropped | locked | rim light, dark mass | held | **give the dominated character one equal-size frame** to show the cost |
| Relief / release | WS, air restored | eye | 2 | slow drift | bright, open values | long | **keep one dark object in frame** so relief has a residue |
| Disorientation | any size, off-balance | dutch | 7 | handheld | broken values, glare | irregular | **freeze one clean symmetrical frame** at the end |
| Awe / sublime | EWS, human tiny | low or high (both) | 3 | slow crane or static | deep values, atmospheric layers | very long | **one human-scale detail** in the foreground to measure the scale |

## 4. Staging a power shift

Power in a frame is a comparison, not a property. To move it inside one scene:

- **Scale**: whoever occupies more of the frame has the floor. Change it by moving the camera, not the actor.
- **Eye height**: the higher pair of eyes in frame reads as dominant across a cut — the audience's gaze has to travel up or down.
- **Screen side**: the character with more screen space and the frame edge behind them reads as freer; the one boxed between objects reads as contained.
- **Who is lit**: the more contrasted face wins attention. A rim-lit back can dominate a fully lit face.
- **Who looks, who is looked at**: the observer holds power; the observed is exposed. A POV shot gives power to the looker, an OTS look-at gives it to the watched.
- **Knowledge**: the character who knows what the other does not is dominant regardless of framing. Intercutting is a power tool.

Design the shift as a sequence of two or three frames, each re-measuring one of these.

## 5. Contradiction (the advanced move)

Stock emotion is symmetric: sad = close + slow + dark. Designed emotion is often a single contradiction, held with confidence:

- **Wide shot for grief** — the world continuing around the loss is crueler than a close-up.
- **Static camera for panic** — the frame refuses to share the character's agitation.
- **Bright, even light for dread** — horror in daylight is worse than horror in shadow.
- **Close-up for loneliness** — a face filling the frame with nothing to look at.
- **Fast cutting for intimacy** — fragments of touch, more intimate than a held two-shot.
- **Long lens for a chase** — compression makes escape look impossible.

Use one contradiction per sequence. Two and the audience stops trusting the point of view.

## 6. Performance: observable cues only

Abstract emotion words give the model nothing to render. Write **2–4 observable cues** per emotional transition, drawn from:

eyes (focus, wetness, darting, closing), brows (tension, lift), mouth (press, part, swallow), breath (held, shallow, released), throat (swallow), hands (grip, fidget, still), shoulders (drop, square), weight (shift, lean), gaze target (where, and when it moves).

Then add **one subtext line** for the model's benefit:

```text
Emotion analysis: she is not asking for permission — she is waiting to be told
she was right, and already knows she will not be.
```

Subtext is not decoration. It tells the performer (human or model) *why* the cue happens, which is what keeps micro-acting from becoming a face-pulling contest.

## 7. Sound carries half the emotion

- **Silence** before a line is louder than score under it.
- **Room tone** establishes that the space is real; its absence reads as a studio.
- **One off-screen sound** can create a whole world (a train, a neighbour, a fly).
- **Music should enter after the emotion has already started**, not to announce it.
- In AI prompts: design the sound per beat, and ban the default score when you do not want it.

## 8. Self-check

Before shipping a shot, answer:

1. Which dials did I set, and to what value?
2. What does the viewer know at this moment that they did not know ten seconds ago?
3. What is the one contradiction that keeps this from being stock?
4. Which two observable cues will carry the turn?
5. If I removed the emotion word from the prompt, would the design still produce it?

If (5) is no, the design is not finished.
