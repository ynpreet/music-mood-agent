#!/usr/bin/env python3
"""
Music Mood Agent -- Demo 4 of 4, Agentic AI Workshop.

The user describes how they feel or what they are doing
("I'm stressed after a long workday", "road trip with friends",
"can't focus, need to study") and a small crew of agents builds
them a 5-song playlist shaped as an emotional arc: MATCH the current
mood, then LIFT toward the desired mood, then SUSTAIN it.

Three agents, each with a printed PLAN and numbered steps, so
students can SEE the agentic loop:

  Agent 1 -- Mood-Interpreter  : situation text  -> mood profile
  Agent 2 -- Playlist-Builder  : mood profile    -> 5-song sequence
                                  (uses TOOL: search_catalog, reads
                                  SESSION_MEMORY, scores candidates)
  Agent 3 -- Explainer         : 5-song sequence -> one "why it fits"
                                  line per song

Run:   python3 demo.py
Stdlib only. Fully offline, zero API keys, zero randomness --
byte-identical output on every run (the 10-run test log proves it).
"""

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# Data: real Spotify track catalog (verified track IDs; metadata in local
# JSON, no API) + session memory.
# In a real deployment, SESSION_MEMORY would be a persistent store
# (database / vector store) that grows with every listening session.
# ---------------------------------------------------------------------------
CATALOG = json.loads((HERE / "tracks.json").read_text(encoding="utf-8"))

SESSION_MEMORY = {
    "past_sessions": [
        {
            "situation": "studying for finals late at night",
            "worked": ["Suite bergamasque, CD 82: III. Clair de lune",
                       "Experience", "Gymnopédie No. 1"],
            "takeaway": "solo piano/ambient focus tracks sustained concentration",
        },
        {
            "situation": "winding down after a hard day",
            "worked": ["River Flows in You", "Weightless"],
            "takeaway": "low-energy acoustic tracks beat silence for recovery",
        },
    ]
}

MEMORY_BOOST = 8  # extra score points for tracks a past session proved out


# ---------------------------------------------------------------------------
# TOOL: search_catalog -- the Playlist-Builder's only tool.
# ---------------------------------------------------------------------------
def search_catalog(mood=None, energy_min=None, energy_max=None, valence_min=None):
    """Filter the catalog. Returns tracks sorted by title (deterministic)."""
    hits = []
    for t in CATALOG:
        if mood and not any(m in t["mood"] for m in mood):
            continue
        if energy_min is not None and t["energy"] < energy_min:
            continue
        if energy_max is not None and t["energy"] > energy_max:
            continue
        if valence_min is not None and t["valence"] < valence_min:
            continue
        hits.append(t)
    hits.sort(key=lambda t: (t["title"].lower(), t["artist"].lower()))
    return hits


# ---------------------------------------------------------------------------
# Agent 1 -- Mood-Interpreter: situation text -> mood profile.
# ---------------------------------------------------------------------------
# Each rule maps keyword hits to a full mood profile:
#   current state, desired state, and the 5-slot emotional arc
#   (slot = role, target energy, target valence, desired mood tags).
STRESS_PROFILE = {
    "current": "stressed, tense after a long workday",
    "desired": "calm, gently recharged",
    "desired_word": "calm",
    "arc": [
        {"role": "MATCH",   "tags": ["melancholic", "calm"], "te": 5, "tv": 4},
        {"role": "BRIDGE",  "tags": ["calm"],                "te": 4, "tv": 6},
        {"role": "LIFT",    "tags": ["happy", "calm"],       "te": 4, "tv": 8},
        {"role": "SUSTAIN", "tags": ["calm", "happy"],       "te": 3, "tv": 8},
        {"role": "SUSTAIN", "tags": ["calm"],                "te": 2, "tv": 7},
    ],
}

PARTY_PROFILE = {
    "current": "buzzing, ready for the road with friends",
    "desired": "celebration, windows-down energy",
    "desired_word": "celebration",
    "arc": [
        {"role": "MATCH",   "tags": ["happy"],               "te": 6, "tv": 8},
        {"role": "LIFT",    "tags": ["energetic", "happy"],  "te": 8, "tv": 9},
        {"role": "PEAK",    "tags": ["energetic", "happy"],  "te": 9, "tv": 9},
        {"role": "SUSTAIN", "tags": ["energetic", "happy"],  "te": 9, "tv": 8},
        {"role": "SUSTAIN", "tags": ["happy", "energetic"],  "te": 8, "tv": 9},
    ],
}

FOCUS_PROFILE = {
    "current": "distracted, can't focus, mind scattered",
    "desired": "deep focus for studying",
    "desired_word": "focus",
    "arc": [
        {"role": "MATCH",   "tags": ["calm"],          "te": 5, "tv": 6},
        {"role": "SETTLE",  "tags": ["focus", "calm"], "te": 4, "tv": 7},
        {"role": "FOCUS",   "tags": ["focus"],         "te": 3, "tv": 7},
        {"role": "FOCUS",   "tags": ["focus", "calm"], "te": 3, "tv": 6},
        {"role": "SUSTAIN", "tags": ["focus", "calm"], "te": 2, "tv": 7},
    ],
}

# Rule order = priority order. First rule with ANY keyword hit wins.
# (Deterministic: fixed list.) Typo variants are included on purpose:
# students type "hapy", "stresed", "studdy" -- the agent should still hear them.
SAD_PROFILE = {
    "current": "low, heavy-hearted",
    "desired": "lighter, gently held",
    "desired_word": "lighter",
    "arc": [
        {"role": "MATCH",   "tags": ["melancholic", "sad"], "te": 4, "tv": 3},
        {"role": "BRIDGE",  "tags": ["melancholic", "calm"], "te": 4, "tv": 5},
        {"role": "LIFT",    "tags": ["calm", "happy"],       "te": 5, "tv": 7},
        {"role": "SUSTAIN", "tags": ["happy", "calm"],       "te": 4, "tv": 8},
        {"role": "SUSTAIN", "tags": ["calm"],                "te": 3, "tv": 7},
    ],
}

WORKOUT_PROFILE = {
    "current": "gearing up, needs fuel",
    "desired": "pumped, locked in",
    "desired_word": "pumped",
    "arc": [
        {"role": "MATCH",   "tags": ["energetic"],            "te": 7, "tv": 7},
        {"role": "LIFT",    "tags": ["energetic", "workout"], "te": 8, "tv": 8},
        {"role": "PEAK",    "tags": ["workout", "energetic"], "te": 9, "tv": 9},
        {"role": "SUSTAIN", "tags": ["energetic", "workout"], "te": 8, "tv": 8},
        {"role": "SUSTAIN", "tags": ["workout"],              "te": 7, "tv": 8},
    ],
}

ROMANTIC_PROFILE = {
    "current": "tender, wants the mood set",
    "desired": "romance in the air",
    "desired_word": "romance",
    "arc": [
        {"role": "MATCH",   "tags": ["calm", "romantic"],  "te": 4, "tv": 7},
        {"role": "BRIDGE",  "tags": ["romantic"],          "te": 4, "tv": 8},
        {"role": "LIFT",    "tags": ["romantic", "happy"], "te": 5, "tv": 8},
        {"role": "SUSTAIN", "tags": ["romantic", "calm"],  "te": 4, "tv": 8},
        {"role": "SUSTAIN", "tags": ["romantic"],          "te": 3, "tv": 7},
    ],
}

# Honest fallback: when nothing matches, say so. Never fake a confident label.
FALLBACK_PROFILE = {
    "current": "unrecognized -- couldn't place the mood",
    "desired": "a balanced mix, honestly labeled",
    "desired_word": "balance",
    "arc": [
        {"role": "MATCH",   "tags": ["calm"],               "te": 4, "tv": 6},
        {"role": "BRIDGE",  "tags": ["happy", "calm"],       "te": 5, "tv": 7},
        {"role": "LIFT",    "tags": ["energetic", "happy"],  "te": 7, "tv": 8},
        {"role": "SUSTAIN", "tags": ["calm", "happy"],       "te": 4, "tv": 7},
        {"role": "SUSTAIN", "tags": ["focus", "calm"],       "te": 3, "tv": 6},
    ],
}

SITUATION_RULES = [
    ({"workout", "gym", "running", "run", "jog", "jogging", "exercise",
      "training", "marathon", "cardio", "lift weights", "leg day"},
     WORKOUT_PROFILE, "workout"),
    ({"romantic", "date night", "anniversary", "valentine", "valentines",
      "candlelit", "dinner date", "in love", "crush", "slow dance"},
     ROMANTIC_PROFILE, "romantic"),
    ({"focus", "study", "studdy", "focuse", "exam", "concentrate",
      "concetrate", "deadline", "assignment", "homework", "distracted"},
     FOCUS_PROFILE, "focus/study"),
    ({"road trip", "roadtrip", "drive", "friends", "party", "weekend",
      "trip", "car ride", "hapy", "hapyy", "celebrate", "celebration"},
     PARTY_PROFILE, "road-trip/party"),
    ({"sad", "sadd", "heartbreak", "heartbroken", "lonely", "crying",
      "blue", "depressed", "down bad", "miss him", "miss her", "miss them",
      "breakup", "broke up"},
     SAD_PROFILE, "low/sad"),
    ({"stress", "stressed", "stresed", "stressful", "exhausted", "exhosted",
      "tired", "burnt", "burnout", "burntout", "long day", "drained",
      "overwhelm", "overwhelmed", "anxious", "anxiety", "winding down",
      "wind down", "relax", "calm down"},
     STRESS_PROFILE, "wind-down"),
]


def _kw_hit(lowered, kw):
    """Keyword hit with word boundaries for very short keywords.

    Prevents 'sad' (3 letters) from firing inside 'cansado', while keeping
    substring matching for longer phrases like 'road trip' or 'date night'.
    """
    if len(kw) <= 3:
        return re.search(r"\b" + re.escape(kw) + r"\b", lowered) is not None
    return kw in lowered


def interpret(situation_text):
    """Agent 1. Prints PLAN + steps, returns the mood profile."""
    print("[Agent 1 - Mood-Interpreter]  PLAN:")
    print("  1. Normalize the user's situation text.")
    print("  2. Match keywords -> current state, desired state, energy needed.")
    print("  3. Load session memory to bias tag weights.")
    print("  4. Emit a mood profile (with a 5-slot emotional arc).")
    print()

    lowered = situation_text.lower()
    print("  STEP 1: normalized -> \"%s\"" % lowered)

    profile, label = None, None
    hits = []
    for keywords, prof, lab in SITUATION_RULES:
        hits = sorted(k for k in keywords if _kw_hit(lowered, k))
        if hits:
            profile, label = prof, lab
            break
    if profile is None:  # honest fallback: never fake a confident label
        profile, label, hits = FALLBACK_PROFILE, "unrecognized -- balanced mix", []
    print("  STEP 2: keyword hits %s -> situation type '%s'" % (hits, label))
    if not hits:
        print("  HONESTY NOTE: I couldn't place that mood, so I'm building a")
        print("  balanced mix across moods instead of guessing wrong.")

    mem = SESSION_MEMORY["past_sessions"]
    print("  STEP 3: session memory loaded: %d past sessions" % len(mem))
    for s in mem:
        print("          - '%s' -> worked: %s" % (s["situation"], ", ".join(s["worked"])))

    print("  STEP 4: mood profile -> current='%s' | desired='%s'"
          % (profile["current"], profile["desired"]))
    print("          arc: " + " -> ".join(s["role"] for s in profile["arc"]))
    print()
    return profile


# ---------------------------------------------------------------------------
# Agent 2 -- Playlist-Builder: mood profile -> 5-song sequence.
# ---------------------------------------------------------------------------
def score_track(track, slot, memory_boost_titles):
    """Score a candidate against one arc slot. Higher is better."""
    score = 60
    score -= 5 * abs(track["energy"] - slot["te"])
    score -= 4 * abs(track["valence"] - slot["tv"])
    score += 12 * sum(1 for m in slot["tags"] if m in track["mood"])
    boosted = track["title"] in memory_boost_titles
    if boosted:
        score += MEMORY_BOOST
    return score, boosted


def build_playlist(profile, *, use_memory=True, energy_cap=None):
    """Agent 2. Prints PLAN + steps, uses the search_catalog tool, returns picks.

    use_memory=False: skip the +8 memory boost (the user asked to ignore past
    sessions). energy_cap=int: clamp every slot's target energy to that ceiling
    (e.g. the user asked for nothing high-energy). Both default to the
    historical behavior, so the canned demo output is byte-identical.
    """
    print("[Agent 2 - Playlist-Builder]  PLAN:")
    print("  1. Translate the emotional arc into 5 slot targets (energy, valence).")
    print("  2. For each slot: TOOL search_catalog(filters) -> score hits -> pick best unused.")
    print("  3. Apply session-memory boost when a past win matches this situation.")
    print()

    memory_titles = set()
    if use_memory and "focus" in profile["arc"][2]["tags"]:  # study-type situation
        past = SESSION_MEMORY["past_sessions"][0]
        memory_titles = set(past["worked"])
        print("  MEMORY BOOST: past session '%s' worked with lo-fi/focus tracks"
              % past["situation"])
        print("  -> weighting [%s] +%d points this run"
              % (", ".join(sorted(memory_titles)), MEMORY_BOOST))
        print()

    picks, used = [], set()
    for i, slot in enumerate(profile["arc"], start=1):
        te = slot["te"] if energy_cap is None else min(slot["te"], energy_cap)
        # score against the (possibly clamped) target so scoring stays honest
        eff_slot = dict(slot, te=te) if energy_cap is not None else slot
        e_min = max(1, te - 3)
        e_max = min(10, te + 3)
        print("  STEP 2.%d  SLOT %d [%s]: target energy~%d, valence~%d, tags=%s"
              % (i, i, slot["role"], te, slot["tv"], slot["tags"]))
        print("    TOOL CALL: search_catalog(mood=%s, energy %d-%d, valence>=%d)"
              % (slot["tags"], e_min, e_max, max(1, slot["tv"] - 3)))
        v_min = max(1, slot["tv"] - 3)
        hits = [t for t in search_catalog(mood=slot["tags"], energy_min=e_min,
                                          energy_max=e_max, valence_min=v_min)
                if t["title"] not in used]
        if not hits:  # widen progressively; never crash on an empty slot
            print("    -> 0 hits at strict filters; widening energy window...")
            hits = [t for t in search_catalog(
                mood=slot["tags"],
                energy_min=max(1, te - 5),
                energy_max=min(10, te + 5))
                if t["title"] not in used]
        if not hits:
            print("    -> still 0; dropping energy/valence filters (mood tags only)...")
            hits = [t for t in search_catalog(mood=slot["tags"])
                    if t["title"] not in used]
        if not hits:
            print("    -> still 0; taking any unused catalog track (last resort)...")
            hits = [t for t in CATALOG if t["title"] not in used]
        if not hits:
            raise RuntimeError("catalog exhausted: more slots than tracks")
        print("    -> %d hits" % len(hits))

        best, best_score, best_boosted = None, None, False
        for t in hits:
            sc, boosted = score_track(t, eff_slot, memory_titles)
            key = (sc, t["title"].lower(), t["artist"].lower())
            if best is None or key > (best_score, best["title"].lower(), best["artist"].lower()):
                best, best_score, best_boosted = t, sc, boosted
        used.add(best["title"])
        picks.append((best, slot["role"], best_boosted))
        flag = "  [MEMORY-BOOSTED]" if best_boosted else ""
        print("    PICK: \"%s\" - %s (score %d)%s"
              % (best["title"], best["artist"], best_score, flag))
    print()
    return picks


# ---------------------------------------------------------------------------
# Agent 3 -- Explainer: one "why it fits" line per song.
# ---------------------------------------------------------------------------
def energy_word(e):
    return "gentle" if e <= 3 else "steady" if e <= 6 else "driving"


def valence_word(v):
    return "low-key" if v <= 4 else "balanced" if v <= 6 else "bright"


ROLE_LINES = {
    "MATCH":   ('meets you where you are - {ew} {genre} (energy {e}/10, valence {v}/10) '
                'at {t} BPM, so the playlist starts honest instead of forced.'),
    "BRIDGE":  ('the turn begins - {vw} warmth (valence {v}/10) at a {ew} {t} BPM; '
                'the tension starts to drain without a jolt.'),
    "LIFT":    ('lifts the floor - {vw} and {ew} (valence {v}/10, {t} BPM); '
                'this is the track your shoulders drop on.'),
    "SETTLE":  ('settles the scatter - {ew} {genre} ({t} BPM, valence {v}/10) '
                'gives your brain one thing to hold onto.'),
    "FOCUS":   ('deep-work fuel - minimal-lyric {genre} at {t} BPM (energy {e}/10); '
                'fills the room without stealing your words.'),
    "SUSTAIN": ('locks in "{desired}" - {ew} {genre}, {t} BPM; built to hold the mood, '
                'not chase it.'),
    "PEAK":    ('the peak - {ew} {genre} at {t} BPM; windows down, volume up, no notes.'),
}


def explain(picks, profile):
    """Agent 3. Prints PLAN + one why-it-fits line per song."""
    print("[Agent 3 - Explainer]  PLAN:")
    print("  1. For each picked song, combine its arc role + catalog attributes")
    print("     (energy, valence, tempo, genre) into one plain-language reason.")
    print("  2. Flag any pick that session memory boosted.")
    print()
    for n, (t, role, boosted) in enumerate(picks, start=1):
        line = ROLE_LINES[role].format(
            ew=energy_word(t["energy"]), vw=valence_word(t["valence"]),
            genre=t["genre"].lower(), e=t["energy"], v=t["valence"],
            t=t["tempo"], desired=profile["desired_word"])
        mem_note = " [memory: this worked for you last time]" if boosted else ""
        print("  %d. \"%s\" - %s [%s]%s" % (n, t["title"], t["artist"], role, mem_note))
        print("     WHY: " + line[0].upper() + line[1:])
    print()


# ---------------------------------------------------------------------------
# Driver: 3 situations back-to-back in one run.
# ---------------------------------------------------------------------------
SITUATIONS = [
    "I'm stressed after a long workday",
    "Road trip with friends this weekend!",
    "I can't focus - I need to study for my exam",
]

BANNER = "=" * 70


def main():
    print(BANNER)
    print("  MUSIC MOOD AGENT -- Demo 4 of 4 - Agentic AI Workshop")
    print("  Real Spotify track catalog (%d tracks) - metadata local, stdlib only" % len(CATALOG))
    print(BANNER)
    print()

    for n, situation in enumerate(SITUATIONS, start=1):
        print("SITUATION %d/%d: \"%s\"" % (n, len(SITUATIONS), situation))
        print("-" * 70)
        profile = interpret(situation)
        picks = build_playlist(profile)
        explain(picks, profile)
        print("  Playlist complete: %d tracks - arc %s"
              % (len(picks), " -> ".join(r for _, r, _ in picks)))
        print(BANNER)
        print()

    print("Done. Same output on every run -- try it twice.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
