# Mechanism Library

An indexed library of shot mechanisms. Each entry is a *mechanism*, not a mood: a specific arrangement of frame, camera and subject that produces a known effect and has a known failure.

Use it the way a camera department uses a shot list: scan the index, open only the rows you need, then adapt one mechanism with one detail that makes it this film. Two mechanisms per shot at most — a spine and a modifier.

IDs are stable. Put the ID in `shot.mechanism` and the validator will check it exists.

## Index

| ID | Mechanism | Job |
|---|---|---|
| M01 | Space omen | something is coming |
| M02 | Descent | a powerful subject arrives |
| M03 | Orbit reveal | measure and admire a subject |
| M04 | Dead stop | the pause that sells the next move |
| M05 | Wind-up | intent before the strike |
| M06 | Dash | close distance, show speed |
| M07 | Impact close | the contact point |
| M08 | Hit-and-fly | the consequence of a hit |
| M09 | Shockwave | the world absorbs the hit |
| M10 | Landing | a fall or jump ends |
| M11 | Aerial chase | pursuit in open space |
| M12 | Track-through | movement through a space |
| M13 | Standoff | two sides, no movement yet |
| M14 | Power compare | one side must dominate |
| M15 | Eye-line cut | recognition between enemies |
| M16 | Turn | the subject realises |
| M17 | Interrupt | a third force changes the scene |
| M18 | Reaction insert | the cost on a face |
| M19 | Detail insert | a small object carries the beat |
| M20 | Reveal flip | knowledge inverts |
| M21 | Pull-out landing | let the new state sit |
| M22 | Doorway frame | watch from outside |
| M23 | Shot / reverse | conversation, balanced |
| M24 | Master two-shot | relationship in one frame |
| M25 | OTS power shift | who owns the conversation |
| M26 | Walk and talk | information while moving |
| M27 | A-pattern block | three players, one plane |
| M28 | L-pattern block | depth inside a group |
| M29 | Insert bridge | escape geography, buy time |
| M30 | Silent two-shot | what is not said |
| M31 | Lone figure | isolation in a wide |
| M32 | Push to face | realisation arrives |
| M33 | Crowd swell | the world reacts as one body |
| M34 | Vehicle approach | something arrives fast |
| M35 | Parallel pair | two places, one action |
| M36 | Dream drift | floating, unmotivated time |
| M37 | Comedy hold | hold past the joke |
| M38 | Reaction chain | escalation across faces |
| M39 | Silhouette reveal | a figure behind light |
| M40 | Overhead map | geometry, fate, systems |
| M41 | Performance front | full body, stage rhythm |
| M42 | Product turn | object as hero |

## 1. Arrival and action

| ID | Mechanism | Use when | Size · angle | Move | Pairs with | Failure |
|---|---|---|---|---|---|---|
| M01 | Space omen | something is about to enter | WS/EWS, eye or low | static, or slow tilt up | M02 | too much happening; the omen drowns in detail |
| M02 | Descent | a powerful subject arrives | MS→WS, low | tilt down following the body | M01, M10 | cut before the body settles |
| M03 | Orbit reveal | the subject must be measured | MS, low, long lens ok | slow orbit 30–60° | M04 | turntable: no change inside the circle |
| M04 | Dead stop | the pause before the move | CU/MS, eye | static | M05, M03 | held so long it reads as an error |
| M05 | Wind-up | before the strike | MCU, low, foreground occlusion | static or small push | M06 | pose unreadable because the silhouette is hidden |
| M06 | Dash | closing distance | MS, side-on, wide lens | track with subject, or static letting them cross | M07 | camera and subject move together: nothing moves |
| M07 | Impact close | the contact point | CU/ECU at contact, low | shallow push or static | M08 | impact happens off-frame |
| M08 | Hit-and-fly | the consequence of a hit | MS→WS, eye | follow or pan with the body | M09 | body leaves frame before it moves |
| M09 | Shockwave | the world absorbs the hit | WS/EWS, low | static, one-frame shake | M10 | debris as confetti; no spatial logic |
| M10 | Landing | a fall or jump ends | WS, ground level | static, camera settles | M09, M02 | no ground interaction: no dust, no compression |
| M11 | Aerial chase | pursuit in open space | WS, high or level | track, crane | M12 | both subjects same size: no depth cue |
| M12 | Track-through | movement through a space | MS, eye or chest | track/follow | M11, M26 | space unreadable: generic background |

## 2. Confrontation and power

| ID | Mechanism | Use when | Size · angle | Move | Pairs with | Failure |
|---|---|---|---|---|---|---|
| M13 | Standoff | two sides, no movement yet | two MS or a two-shot, eye | static | M15 | both faces equally lit and equally important |
| M14 | Power compare | one side must dominate | WS with both, low | static | M22 | the bigger figure is bigger only by being nearer |
| M15 | Eye-line cut | recognition between enemies | CU ×2, eye, matched | static | M13, M16 | eyelines do not match; two different rooms |
| M16 | Turn | the subject realises | MCU, eye | static or small push | M15, M17 | too fast to read, or too slow to surprise |
| M17 | Interrupt | a third force enters | WS, eye | whip pan or hard cut | M16, M29 | the new element is never given its own frame |

## 3. Emotion and reveal

| ID | Mechanism | Use when | Size · angle | Move | Pairs with | Failure |
|---|---|---|---|---|---|---|
| M18 | Reaction insert | the audience needs the cost | CU, eye | static | M19 | held until it becomes acting |
| M19 | Detail insert | a small object carries the beat | ECU, any | static | M18, M29 | object too small to read at video resolution |
| M20 | Reveal flip | knowledge inverts | MS→WS, any | static, or pull to reveal context | M29 | reveal shown before the character registers it |
| M21 | Pull-out landing | let the state sit | MS→WS, eye or high | slow pull out | M10 | pulled too far: subject becomes decoration |
| M22 | Doorway frame | watch from outside | MS, eye | static | M14 | frame too clean to feel observed |

## 4. Dialogue and coverage

| ID | Mechanism | Use when | Size · angle | Move | Pairs with | Failure |
|---|---|---|---|---|---|---|
| M23 | Shot / reverse | conversation, balanced | MCU ×2, eye, matched | static | M24, M25 | identical framing both ways; no development |
| M24 | Master two-shot | the relationship in one frame | MS/WS two-shot, eye | static or slow push | M23 | both players equally weighted: no tension |
| M25 | OTS power shift | who owns the conversation | OTS, eye, 2–3 sizes | static, or push on the listener | M23, M18 | the shoulder eats the face |
| M26 | Walk and talk | information while moving | MS tracking, eye | track | M12 | talk drowns in background motion |
| M27 | A-pattern block | three players on one plane | MS/WS, eye | static | M28 | equal spacing: no hierarchy |
| M28 | L-pattern block | depth inside a group | MS, eye | static or small reframe | M27, M24 | foreground player blocks the others |
| M29 | Insert bridge | escape geography, buy time | ECU, any | static | M19, M20 | insert is pretty but answers nothing |
| M30 | Silent two-shot | what is not said | MS two-shot, eye | static, held | M24, M21 | held past the point where silence is active |
| M31 | Lone figure | isolation must be spatial | WS/EWS, eye or high | static | M21, M30 | figure too small to read, or centred so it loses the edge |
| M32 | Push to face | realisation arrives | MS→CU, eye | slow push, small amplitude | M18, M04 | pushes with nothing to reveal, or arrives before the turn |

## 5. Crowd, vehicle, montage, dream, comedy, horror, performance, product

| ID | Mechanism | Use when | Size · angle | Move | Pairs with | Failure |
|---|---|---|---|---|---|---|
| M33 | Crowd swell | the world reacts as one body | WS/EWS, eye or high | slow crane up, or static | M01, M40 | crowd reads as wallpaper, not as reaction |
| M34 | Vehicle approach | something arrives fast | WS/EWS, low, long lens ok | static, letting it grow; or pan with it | M14, M07 | arrives without scale change; no sense of speed |
| M35 | Parallel pair | two places, one action | MS ×2, matched angles | static | M29, M15 | the two shots are not comparable: different size, angle, rhythm |
| M36 | Dream drift | floating, unmotivated time | MS/WS, any | slow drift, no target | M21, M19 | drift without a subject; reads as a camera test |
| M37 | Comedy hold | hold past the joke | MS, eye, dead centre ok | static | M18, M04 | held so long the joke turns into a mistake |
| M38 | Reaction chain | escalation across faces | CU ×3, eye, matched | static | M15, M18 | all reactions identical: no escalation |
| M39 | Silhouette reveal | a figure behind light | MS/WS, low | static, or small push | M01, M20 | silhouette too dark to read posture |
| M40 | Overhead map | geometry, fate, systems | EWS, top-down | static, or slow rotate | M33, M35 | plan view with no figure for scale |
| M41 | Performance front | full body, stage rhythm | FS/WS, eye or low | static or slow lateral | M03, M12 | feet cropped; the performance loses its base |
| M42 | Product turn | object as hero | CU/MCU, eye, macro ok | slow orbit or light sweep | M19, M22 | object turns but reveals nothing new |

## 6. Modifiers

A modifier is not a mechanism. It changes how any mechanism plays; never use one as a spine.

| Modifier | Effect | When | Failure |
|---|---|---|---|
| Handheld | presence, instability, breath | threat, chase, argument | shake without a source reads as an error |
| Locked-off | control, patience, judgment | confrontations, comedy | held too long without internal change |
| Slow motion | weight, consequence, memory | impact, realisation | used for beauty; kills pace |
| Speed ramp | acceleration into a beat | action, transitions | ramps land after the beat |
| Rack focus | reveals a second subject | two subjects at different depths | focus drifts mid-line |
| Whip pan | violent connection | interrupts, jokes, transitions | motion blur eats the arrival frame |
| Shallow DOF | isolation, portraiture | intimacy, surveillance | subject drifts out of the plane |
| Deep focus | simultaneous arguments | ensembles, irony | everything equally important |

## 7. Choosing

1. State the beat's job in one clause.
2. Pick **one** mechanism that does that job (spine).
3. Optionally add **one** modifier mechanism — only if it changes information, not texture.
4. Adapt one concrete detail: light source, weather, wardrobe, prop, sound.
5. Read the failure column before rendering; those failures recur.

Do not stack three mechanisms in one shot: orbit + dash, or impact + shockwave in a single frame, cannot both be true.

## 8. Pairs that work

- M01 → M02 → M10: omen, arrival, consequence.
- M05 → M06 → M07: intent, speed, contact.
- M07 → M09: contact, then the world's answer (two shots, never one).
- M13 → M15: the room, then the eyes.
- M18 → M21: the face, then the space it is alone in.
- M23 → M25 → M18: exchange, power, cost.
- M27 → M28: the group, then the depth inside it.

## 9. Pairs that fight

- M03 + M06 in one shot: the camera cannot circle and chase at once.
- M07 + M09 in one shot: two scales cannot share a frame.
- M04 + M05 back to back: two pauses with no action between them.
- Any two mechanisms whose camera must move in opposite directions.
