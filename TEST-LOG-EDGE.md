# Music Mood Agent — Edge-Case Test Log (Hardening Wave)

Date: 2026-10-10. Catalog expanded: 36 → 60 tracks across 7 moods
(happy, sad, calm, energetic, focused, romantic, workout).
Mood interpreter hardened: typo tolerance (hapy/happpy, sadd, energtic,
romatic, worokut, focussed, clam), mixed-mood splitting ("sad but need
energy" → sad + energetic), empty/gibberish → honest "couldn't place that
mood — here's a balanced mix" (never a fake confident label).

## 20 mood inputs — all pass

| # | Input | Result |
|---|-------|--------|
| 1 | "I feel so hapy today" | happy ✓ (typo tolerated) |
| 2 | "feeling happpy" | happy ✓ |
| 3 | "sadd after the breakup" | sad ✓ |
| 4 | "energtic morning" | energetic ✓ |
| 5 | "feeling romatic tonight" | romantic ✓ |
| 6 | "worokut time!" | workout ✓ |
| 7 | "need to focussed" | focused ✓ |
| 8 | "clam evening" | calm ✓ |
| 9 | "sad but need energy" | sad + energetic ✓ (mixed) |
| 10 | "happy and calm vibes" | happy + calm ✓ (mixed) |
| 11 | "asdfqwerty" | honest fallback ✓ |
| 12 | "" (empty) | honest fallback ✓ |
| 13 | "!!!!!" | honest fallback ✓ |
| 14 | "como estas" (non-English) | honest fallback ✓ |
| 15 | "supercalifragilistic" | honest fallback ✓ |
| 16 | "lorem ipsum" × 200 words | honest fallback, no hang ✓ |
| 17 | "😊😊😊" emoji-only | happy ✓ |
| 18 | "😢" emoji-only | sad ✓ |
| 19 | "💪🔥" emoji-only | energetic ✓ |
| 20 | "i feel fine" | honest fallback ✓ |

## Catalog integrity
- Verified: every track referenced by the playlist builder exists in the
  catalog — no phantom songs (0 misses).
- Determinism: two runs byte-identical; seeded RNG only, no clock.

## HTTP robustness (all endpoints, 6 hostile inputs each)
- Empty body, malformed JSON `{not json`, JSON array, wrong types,
  10KB junk strings, null bytes, no Content-Length, rapid double-submit:
  HTTP 200 always, zero 500s, zero tracebacks in server logs.
- Note: malformed JSON initially dropped the connection (pre-fix); fixed by
  try/except in `_read_json` (also fixed in the build_apps.py template).

## Failures found and fixed
1. Mixed moods previously surfaced only the first mood — now all detected
   moods contribute. 2. Track-count copy said "36 tracks" — updated to 60.
3. Malformed JSON caused RemoteDisconnected — fixed, now returns honest
   empty-params response.
