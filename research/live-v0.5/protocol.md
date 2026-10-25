# Live v0.5 test protocol

Two practical execution cases: a continuous cup transfer (1 shot / 4 panels / 6 s) and a missed sword attack on shrine steps (3 shots / 8 panels / 10 s). These are existing worked examples, so this is execution validation, not independent generalization or an old/new A/B.

Initial panels: NovelAI V5 full, 1024x576, 23 steps, fixed saved per-panel seeds, sequential requests. Reviewer first inspects images without action captions, then compares to plan. Keep initial failures. At most one deliberate redesign round per failing relation; do not resubmit network failures. H3 follows review, using only chosen references and explicitly recorded unresolved issues. No independent reader is available in this run; do not claim blind evaluation.

Observe: actor identification, ownership/support, approach path, event ordering, cut continuity, result readability. Review actual drawings and densely sampled video frames, rather than quality words or schema scores. Stop on auth/rate/credit errors.
