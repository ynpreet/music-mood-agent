# Music Mood Agent

**Demo 4 of 4 · Agentic AI Workshop**

> **Educational demo.** `tracks.json` holds 35 real, recognizable tracks
> with approximate teaching values for energy, valence, and tempo — not
> measured audio features. Mood detection is keyword-based; this is
> entertainment, not therapy.

---

## Real-world problem, target users, market need, and differentiation

**The problem.** You had a long day, you're packing for a road trip, or
you're staring at a textbook you can't focus on. Your playlists have a
*vibe* but you can't explain why — and no playlist service shapes the
*emotional arc* of a listening session: meet you where you are, lift you
toward where you want to be, sustain the good mood once you're there.

**Target users.** Everyday listeners who use music functionally — to
unwind, to energize, to focus — and describe what they need in plain words
("I'm stressed after a long workday"), not in audio-feature sliders.

**Market need.** Recommendation engines optimize for the next click. Nobody
builds the *sequence*: an arc with a beginning, a turn, and a landing —
plus the honesty of saying *why* each song fits, and a memory of what
worked for you last time.

**Differentiation.** This demo was inspired by real listening-data analysis
— Preet's Spotify listening-data dashboard showed that *when* and *what*
people listen to follows mood patterns, which is exactly what this agent
automates. The differentiator is the arc guarantee: MATCH the mood you're
in (so the playlist starts honest, not forced) → LIFT you toward where
you want to be → SUSTAIN the good mood once you're there — with one
why-it-fits line per song, and session memory that weights tracks that
worked last time (watch for `[MEMORY-BOOSTED]` in Situation 3: "last time
study-focus worked with lo-fi, weighting that higher").

---

## Meaningful Agentic AI functionality

**Why an agent, not a chatbot?** If a student asks "why not just ask an
LLM?": an LLM would hallucinate song titles. This system does something
structurally different:

- **Plans** — each of the three agents prints its PLAN and numbered steps,
  so students SEE the agentic loop.
- **Uses a tool** — `search_catalog` filters the catalog per arc slot (you
  see every tool call in the output); every pick comes from a real (mock)
  catalog via that tool, never from generation.
- **Reasons over multiple steps** — interpret → target arc → retrieve →
  score → sequence → explain.
- **Remembers** — past sessions bias future picks: if lo-fi got you through
  studying last time, those tracks get +8 points the next time you say "I
  can't focus."

A single LLM call couldn't do this reliably — the structure (interpret →
build with tools → explain, with memory) is the point. As the speaker
notes put it: "an agent *does things*; a chatbot just talks."

---

## Project scope, inputs, outputs, constraints, success criteria, and definition of done

**Scope.** A deterministic, offline playlist agent: three situations play
back-to-back — stressed after work, road trip with friends, can't focus
and need to study — each producing a 5-song emotional-arc playlist.

**Inputs.**

- Situation text in plain words (the three scripted situations, or any
  text the keyword rules can match).
- `tracks.json`: 35 tracks with artist, title, genre, mood tags
  (happy/calm/energetic/melancholic/focus), energy 1–10, valence 1–10,
  tempo (BPM).
- `SESSION_MEMORY`: two pre-seeded past sessions (study-finals lo-fi win;
  wind-down acoustic win).

**Outputs.**

- Mood profile: current state, desired state, 5-slot emotional arc (slot =
  role, target energy, target valence, mood tags).
- 5-song sequence with arc roles, scores, and `[MEMORY-BOOSTED]` flags.
- One plain-language "why it fits" line per song.

**Constraints.** Stdlib only, fully offline, zero API keys, zero
randomness. Keyword-based mood interpretation (no real understanding).
Memory is pre-seeded, not learned live.

**Success criteria.** Three situations each produce 5 distinct tracks with
the correct arc shape; Situation 3 shows the memory boost on "A Walk";
output is byte-identical on every run; `TEST-LOG.md` records 10/10.

**Definition of done.** `python3 demo.py` runs the three situations and
exits 0; README carries all 10 checklist sections; `TEST-LOG.md` shows the
10/10 determinism gate passing.

---

## Documented single-agent or multi-agent workflow

**Multi-agent workflow** — three agents, each with a printed PLAN:

```
                    ┌─────────────────────────┐
  "I'm stressed     │  Agent 1 · Mood-        │   mood profile:
   after a long     │  Interpreter            │   current='stressed…'
   workday"  ──────▶│  (keyword rules)        │──▶desired='calm…'
                    └────────────┬────────────┘   arc: 5 slots
                                 │
                    ┌────────────▼────────────┐
  SESSION_MEMORY ──▶│  Agent 2 · Playlist-    │   5-song sequence
  (past sessions'   │  Builder                │──▶with arc roles
   winning tracks)  │  TOOL: search_catalog() │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │  Agent 3 · Explainer    │   one "why it fits"
                    │  (role + attributes     │──▶line per song
                    │   -> plain language)    │
                    └─────────────────────────┘
```

**Agent 1 · Mood-Interpreter** — situation text → mood profile. Keyword
rules map to three profiles (focus/study, road-trip/party, wind-down);
first rule with any keyword hit wins; no hits → gentle calm fallback arc.

**Agent 2 · Playlist-Builder** — mood profile → 5-song sequence. For each
arc slot it calls `search_catalog(mood, energy range, valence floor)`,
scores hits (`60 − 5·|Δenergy| − 4·|Δvalence| + 12·tag hits + 8 memory
boost`), picks the best unused track (deterministic tie-break on score →
title → artist).

**Agent 3 · Explainer** — 5-song sequence → one why-it-fits line per song,
combining arc role + energy/valence/tempo/genre into plain language, with
a memory note when a pick was boosted.

**The catalog** (`tracks.json`): 35 real, recognizable tracks. Each has
artist, title, genre, mood tags (`happy`/`calm`/`energetic`/`melancholic`/
`focus`), energy 1–10, valence (positivity) 1–10, and tempo (BPM). Energy,
valence, and BPM values are approximate teaching values, not measured audio
features.

---

## Working prototype evidence, source code, and setup instructions

### Open in Chrome (fastest way to demo)

```bash
cd ~/workspace/agentic-ai-workshop/music-mood-agent
python3 app.py
```

Then open **http://localhost:8005** in Google Chrome and click
**"▶ Run live demo"**. The story, the agent trace (each agent's PLAN,
numbered steps, `search_catalog` tool calls, and `[MEMORY-BOOSTED]` flags —
all highlighted), and the three resulting playlists appear right in the
browser. Stdlib only, fully offline, no API keys, no installs.

### How to run (MacBook, step by step)

You need nothing but Python 3, which ships with macOS, and Google Chrome.

**1. Open Terminal.** (Spotlight → type "Terminal" → Enter.)

**2. Check Python:**

```bash
python3 --version
```

Any Python 3.8+ works.

**3. Go to the demo folder:**

```bash
cd ~/workspace/agentic-ai-workshop/music-mood-agent
```

**4. Start the web server:**

```bash
python3 app.py
```

You'll see `Open in Chrome: http://localhost:8005`.

**5. Open that URL in Google Chrome** and click **"▶ Run live demo."**
The three situations play back-to-back in the browser: the agent trace on
the left (each agent's PLAN, numbered steps, `search_catalog` tool calls,
`[MEMORY-BOOSTED]` flags — all highlighted) and the three 5-song playlists
on the right, each with one "why it fits" line per song.

**No-browser fallback:** run `python3 demo.py` instead — the same three
situations print straight to the terminal and the program exits 0.

Either way: no arguments, no installs, no network, no API keys. The output
is **byte-identical on every run** (see `TEST-LOG.md`), so it never
surprises you on stage.

### The three demo situations

| # | Situation | Arc | First pick (sample) |
|---|-----------|-----|---------------------|
| 1 | "I'm stressed after a long workday" | MATCH → BRIDGE → LIFT → SUSTAIN → SUSTAIN | "Slow Dancing in a Burning Room" — John Mayer (meets the tension, then unwinds) |
| 2 | "Road trip with friends this weekend!" | MATCH → LIFT → PEAK → SUSTAIN → SUSTAIN | "Maria Tambien" — Khruangbin (cool groove to roll out on) → peaks with "Uptown Funk" |
| 3 | "I can't focus — I need to study for my exam" | MATCH → SETTLE → FOCUS → FOCUS → SUSTAIN | "A Walk" — Tycho (**memory-boosted**: it worked for you last time) |

### Files

| File | What |
|---|---|
| `demo.py` | The terminal demo — 3 agents, 3 situations. `python3 demo.py` |
| `app.py` | The Chrome web UI — serves the demo in the browser on port 8005. `python3 app.py` |
| `tracks.json` | The 35-track real-Spotify catalog. |
| `requirements.txt` | Intentionally empty — stdlib only, nothing to install |
| `TEST-LOG.md` | 10 consecutive runs: exit codes + output hashes (10/10 byte-identical) |
| `RUBRIC.md` | Self-score against the hackathon judging rubric, with evidence per score |

### Speaker notes

- **Open with the question:** "Raise your hand if your playlists have a
  *vibe* but you can't explain why." This demo makes the vibe explicit.
- **Point at the loop:** when Agent 2 prints `TOOL CALL: search_catalog(...)`,
  pause — that's the moment to say "an agent *does things*; a chatbot just
  talks."
- **The memory moment** in Situation 3 is the money shot: "last time
  study-focus worked with lo-fi, weighting that higher." Ask the room: "Who
  here has a 'study playlist' they'd defend with their life?" That's memory,
  and this agent has it too.
- **If a student asks "why not just ask an LLM?"**: an LLM would hallucinate
  song titles. Here, every pick comes from a real (mock) catalog via a tool,
  and the arc guarantees the emotional shape instead of hoping for it.

---

## Functional and end-to-end testing, realistic scenarios, failure cases, reliability, and human oversight

**Realistic scenarios (end to end).** Three situations back-to-back in one
run: wind-down after a stressful workday (MATCH → BRIDGE → LIFT → SUSTAIN
→ SUSTAIN), road-trip celebration (MATCH → LIFT → PEAK → SUSTAIN →
SUSTAIN), and study focus (MATCH → SETTLE → FOCUS → FOCUS → SUSTAIN) — the
last demonstrating the memory boost from a prior session.

**Failure cases the demo handles** (all from `demo.py` behavior):

- **No keyword match.** If no situation rule fires, `interpret` falls back
  to the gentle wind-down arc (`STRESS_PROFILE`, labeled "wind-down
  (fallback)") instead of crashing — every input gets a safe arc.
- **No duplicate picks.** The builder excludes already-used titles per run
  (`if t["title"] not in used`), so a 5-song playlist never repeats a
  track even when slots overlap.
- **Tie-breaking is deterministic.** Candidates sort on (score, title,
  artist) — identical runs pick identical songs.
- **Memory applies only when relevant.** The +8 boost fires only for
  study-type situations (`"focus"` in the arc's middle slot); wind-down
  and party runs don't borrow study memory.
- **Narrow slot windows still return hits.** Each slot searches energy
  ±3 and valence ≥ tv−3 — wide enough that the 35-track catalog always
  yields candidates for every arc role.

**Reliability gate.** `TEST-LOG.md` records 10 consecutive runs of
`python3 demo.py` — exit codes + SHA-256 of full output — with the result
**10/10 PASSED, byte-identical output on every run**.

**Human oversight.** The demo says it out loud: mood detection is
keyword-based, not real understanding — sarcasm or mixed feelings ("happy
but exhausted") will be misread, and mood inference from text can misread
someone's mental state. **This is entertainment, not therapy** — the agent
builds playlists; it never diagnoses or counsels.

---

## Focus, feasibility, and avoidance of unnecessary complexity

Forty tracks, three keyword profiles, one scoring formula, stdlib only.
Deliberately *not* built:

- **No real Spotify API.** `tracks.json` stands in for the Spotify Web API;
  the swap path (section 10) changes the data source, not the agent
  structure.
- **No trained classifier.** Keyword rules are readable by students; a real
  classifier would hide the interpret step this demo is teaching.
- **No live learning.** Memory is pre-seeded with two sessions — the demo
  is honest that a real version would update weights from actual
  listen/skip behavior.
- **No audio analysis.** Energy/valence/tempo are approximate teaching
  values; the demo never claims to measure audio.

Feasibility: the entire agent loop is ~300 lines a student can read in one
sitting — and the arc guarantee (not the model) is the lesson.

---

## Interdisciplinary team roles and division of labor

| Role | Owns in this demo | Concrete component |
|---|---|---|
| **Domain researcher** | The emotional-arc design and mood taxonomy | The three mood profiles (STRESS/PARTY/FOCUS) with 5-slot arcs, mood-tag vocabulary (happy/calm/energetic/melancholic/focus), role-line templates (MATCH/BRIDGE/LIFT/SETTLE/FOCUS/SUSTAIN/PEAK) |
| **Agent engineer** | The 3-agent pipeline, tool, and memory | `interpret`, `build_playlist`, `explain`; `search_catalog` tool; `score_track` formula; the +8 `MEMORY_BOOST` application rule; the no-keyword fallback arc |
| **Data engineer** | The mock catalog and its schema | `tracks.json` (35 tracks: artist/title/genre/mood/energy/valence/tempo), `SESSION_MEMORY` structure, the mock→real Spotify field-mapping table in section 10 |
| **UX / storyteller** | The three situations and the stage narrative | Speaker notes (the vibe question, the memory money-shot), the three-situation table, the Chrome web UI (`app.py`) with highlighted agent trace |
| **QA** | Determinism gate and playlist invariants | `TEST-LOG.md` 10/10 byte-identical gate, no-duplicate-picks guarantee, correct arc shapes per situation, memory-boost verification on Situation 3 |

---

## Limitations, risks, and responsible AI (ethics, privacy, security, safety)

- **Mood detection is keyword-based, not real understanding** — sarcasm or
  mixed feelings ("happy but exhausted") will be misread. Say this out
  loud.
- **35 tracks can't cover anyone's taste** — a real system needs millions;
  the catalog is a teaching stand-in.
- **The memory is pre-seeded, not learned live** — a real version would
  update weights from what you actually finish listening to vs. skip.
- **Mood inference from text can misread someone's mental state — this is
  entertainment, not therapy**, and the demo says so. The agent must never
  be framed as a wellness or mental-health tool.
- **Privacy note for real use.** Session memory is listening history —
  personal data. A production version needs consent, on-device or
  access-controlled storage, and deletion controls; the demo keeps memory
  in-process and fictional.

---

## Practical value, adoption path, and measurable outcomes

**Practical value.** A playlist builder that starts honest (MATCH), moves
you somewhere better (LIFT), and holds the mood (SUSTAIN) — explaining
every pick in one line and remembering what worked last time. The value is
the *sequence with a shape*, not the next-track prediction.

**Adoption path — from mock to real Spotify data.** `tracks.json` stands in
for what the Spotify Web API gives you for real:

| Mock field | Real Spotify equivalent |
|---|---|
| `energy` | `energy` from Audio Features |
| `valence` | `valence` from Audio Features |
| `tempo` | `tempo` from Audio Features |
| `mood` tags | derived from audio features + playlist co-occurrence, or your own listening history |
| `SESSION_MEMORY` | the user's actual listening history (recently-played endpoint) |

Swap path: authenticate with Spotify's API → pull the user's top tracks'
audio features → replace `tracks.json` → replace the keyword
Mood-Interpreter with a real classifier. The agent *structure* (interpret →
build with tools → explain, with memory) stays exactly the same — that's
the lesson.

**Measurable outcomes.** Today: byte-identical determinism (10/10), correct
arc shapes across the three situations, verified memory boost on Situation
3. On real data: completion/skip rates per arc slot, session-length lift
vs a shuffle baseline, and repeat-use of memory-boosted tracks.

---

*Built for the Agentic AI Workshop · Demo 4 of 4*
