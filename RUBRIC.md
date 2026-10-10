# Rubric Self-Score — Music Mood Agent (Demo 4 of 4)

Scored 1–5 per criterion against the PEAAII hackathon judging rubric
(`~/workspace/peaii-hackathon/judging-rubric.md`). Points = (score ÷ 5) × weight.

| # | Criterion | Weight | Score | Points | Evidence |
|---|-----------|--------|-------|--------|----------|
| 1 | Problem Definition & Real-World Impact | 25 | 4/5 | 20 | Concrete user story (share how you feel → get a mood-shaped playlist + reasons); 3 relatable situations demoed back-to-back; connects to real listening-data analysis. Loses a point: 40-track mock catalog can't serve a real user — impact is demonstrated, not delivered. |
| 2 | Meaningful Agentic AI Behavior | 20 | 4/5 | 16 | PLAN + numbered steps printed per agent; genuine tool use (`search_catalog` calls visible with filters and hit counts); multi-step pipeline (interpret → arc targets → retrieve → score → sequence); session memory visibly changes picks (`[MEMORY-BOOSTED]`). Loses a point: the Mood-Interpreter is keyword rules, not real NLU — honest gap, stated in README. |
| 3 | Working Prototype | 15 | 5/5 | 15 | `python3 demo.py` runs offline in seconds, stdlib only; 10/10 consecutive runs, exit 0, byte-identical output (TEST-LOG.md). Three full playlists with arcs and explanations actually produced. |
| 4 | Innovation & Creativity | 15 | 3/5 | 9 | The emotional-arc sequencer (MATCH → LIFT → SUSTAIN) plus memory-weighted rescoring is a real twist on "playlist recommenders," but mood-based music suggestion itself is a well-trodden idea (Spotify's own features do adjacent things). |
| 5 | Presentation & Communication | 15 | 4/5 | 12 | Printed agent loop makes the pipeline followable live; README carries speaker notes, architecture diagram, and a plain-language "why an agent" answer a non-technical audience can track. Loses a point: terminal text only — no visual UI for the playlists. |
| 6 | Responsible AI & Feasibility | 10 | 4/5 | 8 | Limitations stated in the README (keyword mood-reading can misfire; mock data; "entertainment, not therapy"); fully local so no personal listening data ever leaves the machine; clear real-Spotify-API swap path keeps it feasible. Loses a point: no handling at all for sensitive inputs (e.g. someone expressing distress) — a shipped version would need a human-support handoff. |
| | **TOTAL** | **100** | | **80** | |

## Honest gap note

The weakest link is the Mood-Interpreter: keyword matching is a teaching
stand-in for understanding, and it will misread sarcasm, mixed feelings, and
anything outside its three situation families (it falls back to the
wind-down arc silently). For a workshop demo this is the right trade — it
keeps the whole thing offline, instant, and deterministic — but nobody should
confuse it with real sentiment understanding.

## How a student could close it (in a hackathon weekend)

1. **Swap the interpreter:** replace keyword rules with a small local
   classifier or an LLM call that emits the same mood-profile schema
   (current/desired/arc slots) — the downstream agents don't change.
2. **Grow the catalog:** pull real audio features via the Spotify Web API
   (field mapping is already documented in the README).
3. **Make memory real:** persist sessions to a file/DB and update track
   weights from skips vs. completions instead of the pre-seeded list.
4. **Handle the sensitive case:** add a rule that routes distress-signaling
   input to supportive resources instead of a playlist.
5. **Visualize the arc:** plot energy/valence across the 5 slots so the
   audience *sees* MATCH → LIFT → SUSTAIN instead of reading it.
