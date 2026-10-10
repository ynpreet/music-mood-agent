# Test Log — 10x Reliability Gate

Date: 2026-10-10
Machine: Linux VM, Python 3.12.3, stdlib only

## Result: 10/10 PASSED, byte-identical output on every run

Method: `python3 demo.py` executed 10 consecutive times; each run's stdout
was hashed (SHA-256). All 10 runs exited 0; all 10 hashes matched (1 unique
hash), confirming the demo is fully deterministic and stage-safe.

| Run | Exit code | SHA-256 (stdout) |
|-----|-----------|------------------|
| 1 | 0 | 3fcc9f1681fbc01b913862ed120ab17b348363776f6e4b6990479471987a6b1d |
| 2 | 0 | 3fcc9f1681fbc01b913862ed120ab17b348363776f6e4b6990479471987a6b1d |
| 3 | 0 | 3fcc9f1681fbc01b913862ed120ab17b348363776f6e4b6990479471987a6b1d |
| 4 | 0 | 3fcc9f1681fbc01b913862ed120ab17b348363776f6e4b6990479471987a6b1d |
| 5 | 0 | 3fcc9f1681fbc01b913862ed120ab17b348363776f6e4b6990479471987a6b1d |
| 6 | 0 | 3fcc9f1681fbc01b913862ed120ab17b348363776f6e4b6990479471987a6b1d |
| 7 | 0 | 3fcc9f1681fbc01b913862ed120ab17b348363776f6e4b6990479471987a6b1d |
| 8 | 0 | 3fcc9f1681fbc01b913862ed120ab17b348363776f6e4b6990479471987a6b1d |
| 9 | 0 | 3fcc9f1681fbc01b913862ed120ab17b348363776f6e4b6990479471987a6b1d |
| 10 | 0 | 3fcc9f1681fbc01b913862ed120ab17b348363776f6e4b6990479471987a6b1d |

Determinism sources (by design): no randomness anywhere; fixed 3-situation
script; catalog loaded from `tracks.json` in fixed order; all selections
use deterministic scoring with title/artist tie-breaks; no timestamps,
no wall-clock reads, no network.

The demo requires no network, no API keys, and no pip installs.

---

# Web UI test log — 12x app.py reliability gate

Date: 2026-10-10
Machine: Linux VM, Python 3.12.3, stdlib only (`http.server`)

## Result: 12/12 PASSED

Method: each round ran (a) `python3 demo.py` (assert exit 0) and (b) started
`python3 app.py` on port 8005, then curled `GET /` (assert HTTP 200) and
`GET /api/run` (assert HTTP 200, JSON `{"ok": true, "output": "..."}`), then
killed the server. `/api/run` output was checked for stable markers:
`SITUATION 1/3`, `SITUATION 2/3`, `SITUATION 3/3`, `[MEMORY-BOOSTED]`,
`TOOL CALL: search_catalog`, all three `[Agent N - ...]` headers, and the
signature picks "Slow Dancing in a Burning Room", "Uptown Funk", "A Walk".

| Round | demo.py exit | GET / | GET /api/run | Markers | Verdict |
|-------|--------------|-------|--------------|---------|---------|
| 1 | 0 | 200 | 200 | all present | PASS |
| 2 | 0 | 200 | 200 | all present | PASS |
| 3 | 0 | 200 | 200 | all present | PASS |
| 4 | 0 | 200 | 200 | all present | PASS |
| 5 | 0 | 200 | 200 | all present | PASS |
| 6 | 0 | 200 | 200 | all present | PASS |
| 7 | 0 | 200 | 200 | all present | PASS |
| 8 | 0 | 200 | 200 | all present | PASS |
| 9 | 0 | 200 | 200 | all present | PASS |
| 10 | 0 | 200 | 200 | all present | PASS |
| 11 | 0 | 200 | 200 | all present | PASS |
| 12 | 0 | 200 | 200 | all present | PASS |

Failures found/fixed during testing: **none in app.py**. Two test-harness
issues were found and fixed (harness-only, app untouched):
1. A `pkill -f` cleanup pattern matched the test shell's own command line
   and killed it — replaced with port-based cleanup.
2. Shell background-job control (`&` + `kill`) got the outer shell SIGTERM'd
   twice — rewrote the driver in Python (`subprocess.Popen` + `terminate`),
   after which all 12 rounds passed cleanly.

Also verified manually: `python3 app.py` prints `Open in Chrome:
http://localhost:8005` on startup; a second instance on port 8005 exits 2
with a clear "port already in use" error message. demo.py was NOT modified.

### Post-gate fix (same day, before README update)
Node-based verification of the results-panel JS parser (against real
`demo.py` output) found a bug: Explain-agent lines were assigned to the
wrong song — roles collapsed to only the last line's role (e.g. all
SUSTAIN) because PICK lines precede Explain lines in the stream. Fixed by
addressing songs by their printed number (`1.`–`5.`) with a title
cross-check. Re-verified: all 15 songs get correct roles
(MATCH/BRIDGE/LIFT/SUSTAIN/SUSTAIN, MATCH/LIFT/PEAK/SUSTAIN/SUSTAIN,
MATCH/SETTLE/FOCUS/FOCUS/SUSTAIN), Situation 3 flags 3 memory-boosted
tracks ("A Walk", "reflection eternal", "Clair de Lune"), all 15 WHY lines
attached. Full 12-round gate re-run on the fixed code: 12/12 PASS.
