#!/usr/bin/env python3
"""
Music Mood Agent -- Demo 4 of 4, Agentic AI Workshop.

Localhost web UI for the demo. STDLIB ONLY (http.server + subprocess).

Run:   python3 app.py
Then:  Open in Chrome: http://localhost:8005

The page shows the demo story, a "Run live demo" button, an agent-trace
panel (PLAN + steps + memory boosts highlighted) and a results panel.
GET /api/run executes `python3 demo.py` in a subprocess and returns its
output as JSON. Fully offline, no API keys, no pip installs.
"""

import http.server
import json
import socketserver
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PORT = 8005
HOST = "127.0.0.1"
DEMO_SCRIPT = HERE / "demo.py"

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Music Mood Agent &mdash; Live Demo (Agentic AI Workshop)</title>
<style>
  :root{
    --bg:#0f1117; --panel:#161a24; --panel2:#1c2230; --ink:#e8eaf2;
    --muted:#9aa3b8; --accent:#7c9aff; --green:#58d68d; --gold:#f2c14e;
    --orange:#ff9f5a; --line:#2a3145;
  }
  *{box-sizing:border-box}
  body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
       background:var(--bg);color:var(--ink);line-height:1.55}
  .wrap{max-width:1080px;margin:0 auto;padding:28px 20px 60px}
  header{border:1px solid var(--line);border-radius:14px;padding:26px 28px;
         background:linear-gradient(135deg,#1a2136 0%,#141a2b 60%,#10141f 100%)}
  .kicker{color:var(--accent);font-weight:700;letter-spacing:.12em;font-size:12px;
          text-transform:uppercase;margin:0 0 8px}
  h1{margin:0 0 10px;font-size:30px;letter-spacing:-.01em}
  header p{color:var(--muted);margin:8px 0;max-width:760px}
  header p strong{color:var(--ink)}
  .arc{display:inline-block;background:var(--panel2);border:1px solid var(--line);
       border-radius:8px;padding:6px 12px;margin-top:8px;font-family:ui-monospace,Menlo,monospace;
       font-size:13px;color:var(--green)}
  .controls{display:flex;gap:14px;align-items:center;margin:22px 0;flex-wrap:wrap}
  button.run{background:linear-gradient(135deg,#5b7dff,#7c9aff);border:0;color:#0b0e16;
             font-weight:800;font-size:17px;padding:14px 30px;border-radius:10px;cursor:pointer}
  button.run:hover:not(:disabled){filter:brightness(1.08)}
  button.run:disabled{opacity:.55;cursor:wait}
  .note{color:var(--muted);font-size:13px}
  .panels{display:grid;grid-template-columns:1fr;gap:18px;margin-top:6px}
  @media(min-width:900px){.panels{grid-template-columns:1.15fr 1fr}}
  .card{background:var(--panel);border:1px solid var(--line);border-radius:12px;overflow:hidden}
  .card h2{margin:0;padding:14px 18px;font-size:15px;letter-spacing:.06em;text-transform:uppercase;
           border-bottom:1px solid var(--line);background:var(--panel2)}
  .card h2 .tag{color:var(--muted);font-weight:400;text-transform:none;letter-spacing:0}
  .trace{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12.5px;
         line-height:1.65;padding:14px 18px;max-height:640px;overflow:auto;white-space:pre-wrap;
         word-break:break-word}
  .ln{padding:2px 8px;border-radius:6px;margin:1px 0}
  .ln-agent{color:#fff;font-weight:800;background:#2b3a63;margin-top:10px}
  .ln-plan{color:var(--accent);background:#1a2340;border-left:3px solid var(--accent)}
  .ln-tool{color:var(--orange);background:#2b2117;border-left:3px solid var(--orange)}
  .ln-pick{color:var(--green);font-weight:700;background:#12291d;border-left:3px solid var(--green)}
  .ln-memory{color:#10141f;background:var(--gold);font-weight:800}
  .ln-situation{color:#fff;font-weight:800;background:#333c55;margin-top:12px;font-size:13.5px}
  .ln-result{color:var(--green);font-weight:700}
  .ln-why{color:var(--muted)}
  .results{padding:14px 18px;max-height:640px;overflow:auto}
  .sit{border:1px solid var(--line);border-radius:10px;margin:0 0 14px;overflow:hidden}
  .sit-head{padding:10px 14px;background:var(--panel2);font-weight:700;font-size:14px}
  .sit-head small{display:block;color:var(--muted);font-weight:400;font-size:12px;margin-top:2px}
  .song{display:flex;gap:12px;padding:10px 14px;border-top:1px solid var(--line)}
  .num{flex:0 0 26px;height:26px;border-radius:50%;background:#2b3a63;color:#fff;font-weight:800;
       font-size:13px;display:flex;align-items:center;justify-content:center;margin-top:2px}
  .song b{color:var(--ink)}
  .role{display:inline-block;font-size:11px;font-weight:800;letter-spacing:.08em;color:var(--green);
        border:1px solid var(--green);border-radius:20px;padding:1px 9px;margin-left:8px;vertical-align:1px}
  .role.boost{color:var(--gold);border-color:var(--gold)}
  .why{color:var(--muted);font-size:13px;margin:4px 0 0}
  .spinner{display:none;align-items:center;gap:10px;color:var(--muted);font-size:14px}
  .spinner.on{display:flex}
  .dot{width:10px;height:10px;border-radius:50%;background:var(--accent);animation:pulse 1s infinite}
  @keyframes pulse{0%,100%{opacity:.25}50%{opacity:1}}
  .err{color:#ff7b7b;background:#2b1616;border:1px solid #5b2323;border-radius:8px;
       padding:10px 14px;margin:10px 0;font-size:14px}
  footer{margin-top:26px;color:var(--muted);font-size:13px}
  footer code{color:var(--ink)}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <p class="kicker">Agentic AI Workshop &middot; Demo 4 of 4</p>
    <h1>&#127925; Music Mood Agent</h1>
    <p>You tell the agent how you feel &mdash; <strong>&ldquo;I&rsquo;m stressed after a long workday&rdquo;</strong> &mdash;
       and it builds you a 5-song playlist shaped as an <strong>emotional arc</strong>:
       <strong>MATCH</strong> the mood you&rsquo;re in, <strong>LIFT</strong> you toward where you want to be,
       then <strong>SUSTAIN</strong> the good mood &mdash; with one &ldquo;why it fits&rdquo; line per song.
       It also <strong>remembers</strong>: if lo-fi got you through studying last time,
       it weights those tracks higher next time.</p>
    <span class="arc">MATCH &rarr; BRIDGE &rarr; LIFT &rarr; SUSTAIN &rarr; SUSTAIN</span>
    <p style="font-size:13px">Three agents do the work: <strong>1&nbsp;&middot;&nbsp;Mood-Interpreter</strong> (situation &rarr; mood profile),
       <strong>2&nbsp;&middot;&nbsp;Playlist-Builder</strong> (uses the <strong>search_catalog</strong> tool + session memory),
       <strong>3&nbsp;&middot;&nbsp;Explainer</strong> (one plain-language reason per song). 100% offline &middot; stdlib only &middot; deterministic output.</p>
  </header>

  <div class="controls">
    <button class="run" id="runBtn">&#9654; Run live demo</button>
    <div class="spinner" id="spinner"><div class="dot"></div><div class="dot" style="animation-delay:.2s"></div><div class="dot" style="animation-delay:.4s"></div> Running <code>python3 demo.py</code>&hellip;</div>
    <span class="note" id="status">Press the button &mdash; the three demo situations play back-to-back below.</span>
  </div>
  <div id="errBox"></div>

  <div class="panels">
    <div class="card">
      <h2>&#129302; Agent trace <span class="tag">&mdash; plans, tool calls &amp; memory boosts</span></h2>
      <div class="trace" id="trace"><span style="color:var(--muted)">No run yet. Hit &ldquo;Run live demo&rdquo; to watch the agents think.</span></div>
    </div>
    <div class="card">
      <h2>&#127911; Playlists <span class="tag">&mdash; the 3 results</span></h2>
      <div class="results" id="results"><span style="color:var(--muted)">Results appear here after a run.</span></div>
    </div>
  </div>

  <footer>Runs <code>python3 demo.py</code> on this machine via <code>GET /api/run</code>.
  No network, no API keys, no installs. Output is byte-identical on every run (see <code>TEST-LOG.md</code>).</footer>
</div>

<script>
const $ = id => document.getElementById(id);
const runBtn = $("runBtn"), spinner = $("spinner"), statusEl = $("status");
const traceEl = $("trace"), resultsEl = $("results"), errBox = $("errBox");

function esc(s){
  return s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
}

function classify(line){
  const t = line.trim();
  if (/^=+$/.test(t) || /^-+$/.test(t)) return "ln";
  if (t.startsWith("SITUATION")) return "ln ln-situation";
  if (t.startsWith("[Agent ")) return "ln ln-agent";
  if (t.includes("MEMORY BOOST") || t.includes("[MEMORY-BOOSTED]")) return "ln ln-memory";
  if (t.includes("PLAN:")) return "ln ln-plan";
  if (/^\\d+\\.\\s/.test(t)) return "ln ln-plan";
  if (t.startsWith("STEP")) return "ln ln-plan";
  if (t.includes("TOOL CALL:")) return "ln ln-tool";
  if (t.startsWith("PICK:")) return "ln ln-pick";
  if (t.startsWith("Playlist complete")) return "ln ln-result";
  if (t.startsWith("WHY:")) return "ln ln-why";
  return "ln";
}

function renderTrace(output){
  traceEl.innerHTML = output.split("\\n")
    .map(l => '<div class="' + classify(l) + '">' + esc(l || " ") + "</div>")
    .join("");
}

function parseResults(output){
  const sits = [];
  let cur = null, whys = [];
  for (const raw of output.split("\\n")){
    const line = raw.trim();
    let m = line.match(/^SITUATION \\d\\/\\d: "(.*)"$/);
    if (m){ cur = {title: m[1], songs: []}; sits.push(cur); whys = []; continue; }
    m = line.match(/^PICK: "([^"]+)" - (.+?) \\(score (\\d+)\\)(.*)$/);
    if (m && cur){
      cur.songs.push({title: m[1], artist: m[2], score: m[3],
                      boosted: m[4].includes("MEMORY-BOOSTED"), why: ""});
      continue;
    }
    // Explain-agent line: '  3. "Title" - Artist [ROLE]' (comes after the
    // PICK lines, so address the song by its printed number).
    m = line.match(/^(\\d+)\\. "([^"]+)" - .+? \\[([A-Z]+)\\](.*)$/);
    if (m && cur){
      const s = cur.songs[parseInt(m[1], 10) - 1];
      if (s && s.title === m[2]){
        s.role = m[3];
        if (m[4].includes("memory:")) s.boosted = true;
      }
      continue;
    }
    m = line.match(/^WHY:\\s?(.*)$/);
    if (m && cur) whys.push(m[1]);
  }
  // Zip WHY lines to songs in order: walk output once more, assigning each
  // WHY line (in Explain-agent order) to the next song of its situation.
  const lines = output.split("\\n");
  let si = -1, songIdx = 0;
  for (const raw of lines){
    const line = raw.trim();
    if (/^SITUATION \\d\\/\\d: /.test(line)){ si++; songIdx = 0; continue; }
    const m = line.match(/^WHY:\\s?(.*)$/);
    if (m && si >= 0 && si < sits.length && songIdx < sits[si].songs.length){
      sits[si].songs[songIdx].why = m[1];
      songIdx++;
    }
  }
  return sits;
}

function renderResults(output){
  const sits = parseResults(output);
  if (!sits.length){
    resultsEl.innerHTML = '<span style="color:var(--muted)">No playlists parsed.</span>';
    return;
  }
  resultsEl.innerHTML = sits.map((s, si) =>
    '<div class="sit"><div class="sit-head">&#128172; Situation ' + (si + 1) +
    '<small>&ldquo;' + esc(s.title) + '&rdquo;</small></div>' +
    s.songs.map((song, i) =>
      '<div class="song"><div class="num">' + (i + 1) + '</div><div>' +
      '<b>&ldquo;' + esc(song.title) + '&rdquo;</b> &mdash; ' + esc(song.artist) +
      '<span class="role' + (song.boosted ? " boost" : "") + '">' +
      esc(song.role || "") + (song.boosted ? " &#9733; MEMORY-BOOSTED" : "") + "</span>" +
      '<div class="why">' + esc(song.why) + '</div>' +
      '</div></div>'
    ).join("") + "</div>"
  ).join("");
}

runBtn.addEventListener("click", async () => {
  runBtn.disabled = true; spinner.classList.add("on");
  errBox.innerHTML = "";
  statusEl.textContent = "Agents are working\u2026";
  try {
    const r = await fetch("/api/run");
    if (!r.ok) throw new Error("server returned HTTP " + r.status);
    const data = await r.json();
    if (!data.ok) throw new Error(data.output || ("demo.py exited " + (data.returncode ?? "?")));
    renderTrace(data.output);
    renderResults(data.output);
    statusEl.textContent = "Done \u2014 same output on every run. Run it again, dare it to surprise you.";
  } catch (e) {
    errBox.innerHTML = '<div class="err">Demo failed: ' + esc(String(e.message || e)) + "</div>";
    statusEl.textContent = "Run failed \u2014 see error above.";
  } finally {
    runBtn.disabled = false; spinner.classList.remove("on");
  }
});
</script>
</body>
</html>
"""

ROUTES = ("GET /", "GET /api/run")


class Handler(http.server.BaseHTTPRequestHandler):
    server_version = "MusicMoodDemo/1.0"

    def log_message(self, fmt, *args):  # keep the console clean for the demo
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _send(self, code, body, ctype):
        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/" or self.path.split("?", 1)[0] == "/":
            self._send(200, PAGE, "text/html")
        elif self.path.split("?", 1)[0] == "/api/run":
            self._run_demo()
        elif self.path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
        else:
            self._send(404, json.dumps({"ok": False, "error": "not found"}),
                       "application/json")

    def _run_demo(self):
        try:
            proc = subprocess.run(
                [sys.executable, str(DEMO_SCRIPT)],
                capture_output=True, text=True, cwd=str(HERE), timeout=120,
            )
            payload = {
                "ok": proc.returncode == 0,
                "output": proc.stdout if proc.returncode == 0 else proc.stderr,
                "returncode": proc.returncode,
            }
        except FileNotFoundError:
            payload = {"ok": False, "output": "demo.py not found next to app.py."}
        except subprocess.TimeoutExpired:
            payload = {"ok": False, "output": "demo.py timed out after 120s."}
        except Exception as e:  # noqa: BLE001 - never 500 the UI on stage
            payload = {"ok": False, "output": "server error: %s" % e}
        self._send(200, json.dumps(payload), "application/json")

    # Only GET is needed; other methods get a clear answer.
    def do_POST(self):
        self._send(405, json.dumps({"ok": False, "error": "use GET"}),
                   "application/json")

    def do_PUT(self):
        self.do_POST()

    def do_DELETE(self):
        self.do_POST()


class ReusableServer(socketserver.TCPServer):
    allow_reuse_address = True


def main():
    if not DEMO_SCRIPT.exists():
        print("ERROR: demo.py not found next to app.py (%s)" % DEMO_SCRIPT,
              file=sys.stderr)
        return 1
    try:
        server = ReusableServer((HOST, PORT), Handler)
    except OSError as e:
        print("ERROR: could not bind %s:%d -- %s" % (HOST, PORT, e), file=sys.stderr)
        print("The port is probably already in use. Stop the other server and retry,",
              file=sys.stderr)
        print("or pick a free port. This demo is hard-wired to port %d." % PORT,
              file=sys.stderr)
        return 2

    print("=" * 60)
    print("  Music Mood Agent -- live demo server (Agentic AI Workshop)")
    print("  Serving: %s" % HERE)
    print("=" * 60)
    print()
    print("  Open in Chrome: http://localhost:%d" % PORT)
    print()
    print("  Press Ctrl+C to stop.")
    sys.stdout.flush()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
