# Worked Example — "Last Train" (12 s, 16:9)

A complete pass through the workflow: intent, chain, cards, both prompts, QC. Copy the *shape*, not the content.

## 1. Intent

```text
Logline: On the last train, a night-shift cleaner folds an unsent letter into a paper boat.
Turn:    rehearsed apology -> the decision to keep it to herself.
Knows:   the viewer sees that the carriage is empty and that she is not going to send it.
```

Emotion curve: **isolation (S1) → tenderness with precision (S2) → resignation that becomes ownership (S3)**.

## 2. Q&A chain

```text
S1 Q: who is alone on this train?        A: she is. New Q: what is she holding?
S2 Q: what is she doing with it?         A: folding it into a boat. New Q: will she send it?
S3 Q: does she let it go?                A: no — she pockets it. The answer is the turn.
```

## 3. Shot cards (abridged)

**S01 — 5.0 s, static wide**

- Purpose: establish emptiness and the object in her hand.
- Dials: proximity 2, power 5, pressure 6, stability 2, value 8, time 6. Contradiction: wide shot for a private emotion.
- Framing: WS, eye level, 35 mm. She sits centre-left, two thirds of the carriage empty to the right.
- Composition: a dark window band across the top, one cold fluorescent tube above her, wet black glass behind. The repeat of seat rows gives a horizontal rhythm she breaks by sitting.
- Staging: she faces camera-left, letter in her right hand, bag on the seat beside her — the only occupied pair of seats.
- Camera: static; the emptiness is the subject.
- Action: she smooths the letter flat on her knee, then stops.
- Sound: wheel rhythm, ventilation hum, a fluorescent buzz on the third second.
- Cut out: sound bridge — the light buzz carries into S02.

**S02 — 3.0 s, close detail, slight low angle**

- Purpose: make the folding an act of care, not a plot device.
- Dials: proximity 9, power 4, pressure 7, stability 3, value 7, time 4.
- Framing: CU on hands and letter at seat height, low angle so the window and her jaw sit above.
- Composition: hands fill the lower two thirds; her out-of-focus jaw occupies the top edge — presence without expression.
- Camera: slow push in, small amplitude; motive: the crease she is making.
- Action: two folds, then she presses the crease with a thumbnail.
- Sound: paper crease, wheel rhythm continuing.
- Cut out: cut on the last press.

**S03 — 4.0 s, medium close, slow push**

- Purpose: the decision, without a line.
- Dials: proximity 8, power 5, pressure 5, stability 4, value 8, time 3. Contradiction: close-up, but she never looks at the lens.
- Framing: MCU, eye level, 50 mm; the window reflects passing lights across her cheek.
- Composition: her face left third, the finished boat held at the bottom edge, the dark window filling the right.
- Camera: slow push in, small amplitude; motive: she lifts the boat toward the window light.
- Action: she looks at the boat, then puts it in her coat pocket. No smile, no tear.
- Cues: eyes stay on the boat, one slow blink, thumb presses the pocket flap down.
- Subtext: she is not giving up on the apology — she is deciding it is hers.
- Sound: the fluorescent buzz stops; only wheels remain.
- End frame: her hand flat over the pocket, profile against black glass.

## 4. Handoff brief

Mechanisms: S01 `M31 Lone figure` · S02 `M19 Detail insert` · S03 `M32 Push to face`.

This is where the skill stops. Everything below is design; the prompt fields are produced by the target's prompt skill.

```text
DESIGN BRIEF — Last Train, 12 s, 16:9, MiniMax H3 (reference kit)

References
  <Picture 1> — role: identity + scene + first frame
    defines: the cleaner (navy uniform, hair tied back), the carriage (empty rows,
             cold fluorescent tube, wet black glass), the unsent letter
    preserve: fully
    exclude: any text on the window decals

Shot 1 / 0.0–5.0 s
  Purpose: establish emptiness and the letter.
  Framing: WS, eye level, 35 mm; she sits centre-left, two thirds empty to frame right.
  Values: dark window band above, one cold tube, wet black glass behind.
  Camera: static — the emptiness is the subject; the camera refuses to help her.
  Start: wide carriage, figure small. End: her hand resting on the unfolded letter.
  Action: she smooths the letter flat on her knee, then stops.
  Cues: thumb presses the fold; jaw sets; shoulders drop.
  Subtext: she is rehearsing the apology for the last time.
  Sound: wheel rhythm, ventilation hum, a fluorescent buzz.
  Continuity: navy uniform, hair tied back, letter in her right hand, window behind her.
  Bans: no crowd, no on-screen text, no music, no fast cuts.
  Cut out: on the fluorescent buzz.

Shot 2 / 5.0–8.0 s
  Purpose: make the folding an act of care.
  Framing: CU at seat height, slight low angle, 50 mm; hands fill the lower two thirds,
           her out-of-focus jaw at the top edge.
  Camera: slow push in, small amplitude — motive: the crease she is making.
  Action: two folds, then a thumbnail presses the crease. End state: a paper boat in her palm.
  Subtext: this is the only part of the apology she still controls.
  Sound: paper crease over the wheel rhythm.
  Cut out: on the final press.

Shot 3 / 8.0–12.0 s
  Purpose: the decision, without a line.
  Framing: MCU, eye level, 50 mm; face left third, boat at the bottom edge, dark glass right.
  Camera: slow push in — motive: she lifts the boat toward the window light.
  Action: she looks at the boat, then pockets it and presses the flap flat.
  Cues: eyes stay on the boat; one slow blink; thumb presses the flap.
  Subtext: she is not giving up on the apology; she is deciding it is hers.
  Sound: the fluorescent buzz stops, wheels remain.
  End frame: profile against black glass, hand flat over the pocket.
  Bans: no smile, no tear, no music, no subtitle.
  Cut out: hold.
```

## 5. What the prompt writer does with it

For MiniMax H3 on this project's AutoDL pipeline: load `h3-prompt-writing`, choose **Ref2VA**, and use the brief as follows.

| Brief element | Becomes, in the prompt skill |
|---|---|
| `<Picture 1>` role + defines + preserve/exclude | the subject and picture definitions, and the retention lines |
| `continuity` per shot | the preservation wording inside each shot, and the retention statements |
| framing / values / camera / action / cues / sound | the shot-by-shot body, in play order |
| shot durations and cut points | the cut times, summing to the requested duration |
| `bans` | where that guide allows exclusions |

Two things the design layer must not do: number the labels, and write the body. If a shot's job cannot be expressed in that structure, redesign the shot rather than smuggling prose into the brief.

## 6. QC

| Check | Result |
|---|---|
| Turn | passed — the boat returns to the pocket |
| Q&A chain | passed — each shot answers and raises |
| Knowledge | passed — the viewer knows she will not send it before she does |
| Ramp | passed — proximity rises, pressure falls (a private decision) |
| Contrast | passed — S1 wide and cold, S2 tight and warm, S3 held |
| Landing | passed — S3 is the longest and lands after the decision |
| Density | passed — 3 shots / 12 s, one action and one move each |
| Handoff | passed — every reference has a role and an exclusion; every shot has continuity and bans |

**Riskiest shot**: S02. Paper folding is a fine manipulation the model often turns into mush, and the thumbnail press needs a stable hand.

**Fallback**: cut before the fold is finished — end S02 on the second crease and let S03 open with the finished boat already in her palm.
