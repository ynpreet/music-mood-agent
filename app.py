#!/usr/bin/env python3
"""Music Mood Agent -- localhost web UI (stdlib only).

Run:  python3 app.py   then open http://localhost:8005
Serves a guided, personalized tour of demo.py (the tested artifact --
demo.py is never modified here; it is only imported as a module and its
canned subprocess run is unchanged).
"""

import contextlib
import http.server
import io
import json
import mimetypes
import re
import subprocess
import sys
import urllib.parse
from pathlib import Path

HOST = "127.0.0.1"
PORT = 8005
HERE = Path(__file__).resolve().parent
DEMO_PY = HERE / "demo.py"

sys.path.insert(0, str(HERE))
import demo as DEMO  # the tested artifact: imported, never modified

COND_RE = re.compile(
    r"(type 2 diabetes|type 1 diabetes|diabetes|hypertension|high blood pressure|"
    r"kidney disease|ckd|heart disease|depression|asthma|arthritis|copd|hyperlipidemia)"
)

def _capture_canned():
    """Run the canned demo exactly as before (subprocess), capture stdout."""
    proc = subprocess.run(
        [sys.executable, str(DEMO_PY)],
        cwd=str(HERE),
        capture_output=True,
        text=True,
        timeout=600,
    )
    return proc.stdout or proc.stderr

def _capture_fn(fn, params):
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            return fn(params)
    except Exception as exc:  # never crash the page on a bad input
        return "[web-ui] The personalized run hit an error and stopped safely.\n%s: %s" % (type(exc).__name__, exc)

# _capture_custom: personalized handlers may return a dict carrying a follow-up decision.
def _capture_custom(fn, params):
    try:
        res = fn(params)
    except Exception as exc:  # never crash the page on a bad input
        return {"output": "[web-ui] The personalized run hit an error and stopped safely.", "decision": None}
    if isinstance(res, dict):
        res.setdefault("decision", None)
        return res
    return {"output": res, "decision": None}

# ---- personalized run: input handling lives in app.py; demo.py untouched ----

def run_custom(params):
    situation = (params.get("situation") or "").strip()
    if not situation:
        situation = "I'm winding down after a long day and want something calm"
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        print("YOUR SITUATION:", situation)
        print("The same three-agent pipeline interprets YOUR mood and builds YOUR arc.")
        print()
        profile = DEMO.interpret(situation)
        print()
        picks = DEMO.build_playlist(profile)
        print()
        DEMO.explain(picks, profile)
    return out.getvalue()

PAGE = '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n<title>Music Mood Agent &mdash; Live Demo</title>\n<style>\n:root{\n  --bg:#0b1220; --bg2:#0e1626; --panel:#131e33; --panel2:#182742;\n  --ink:#eaf0f9; --muted:#9db0c9; --faint:#6b7f99;\n  --teal:#2dd4bf; --teal-dim:rgba(45,212,191,.12);\n  --accent:#5aa9ff; --warn:#fbbf24; --danger:#f87171; --ok:#34d399;\n  --line:#233451; --radius:14px;\n}\n*{box-sizing:border-box}\nbody{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;\n  background:var(--bg);color:var(--ink);line-height:1.6}\nheader{background:linear-gradient(135deg,#0a2540 0%,#0e3a5c 60%,#0b4f4a 100%);\n  padding:42px 32px 34px;border-bottom:1px solid var(--line)}\n.wrap{max-width:1060px;margin:0 auto}\nheader h1{margin:0 0 8px;font-size:30px;letter-spacing:-.01em}\nheader .sub{margin:0;color:#c8d6ea;font-size:16px;max-width:800px}\n.badge{display:inline-block;margin-top:14px;font-size:11.5px;letter-spacing:.1em;\n  text-transform:uppercase;color:#06281f;background:var(--teal);\n  padding:5px 14px;border-radius:999px;font-weight:800}\nmain{padding:8px 32px 48px}\nsection.card{background:var(--panel);border:1px solid var(--line);\n  border-radius:var(--radius);padding:26px 28px;margin:26px 0}\nsection.card h2{margin:0 0 12px;font-size:18px;color:var(--teal)}\nsection.card h2 .n{display:inline-block;width:28px;height:28px;border-radius:50%;\n  background:var(--teal-dim);border:1px solid var(--teal);color:var(--teal);\n  text-align:center;line-height:26px;font-size:14px;margin-right:10px}\nsection.card p{margin:0 0 12px;color:#d5e0f1;font-size:15.5px}\nsection.card p:last-child{margin-bottom:0}\n.watch{list-style:none;margin:6px 0 0;padding:0}\n.watch li{position:relative;padding:8px 0 8px 30px;color:#d5e0f1;font-size:15px;\n  border-bottom:1px dashed var(--line)}\n.watch li:last-child{border-bottom:0}\n.watch li::before{content:"\\25b8";position:absolute;left:8px;color:var(--teal);font-weight:700}\nlabel.f{display:block;margin:14px 0 6px;font-size:13px;font-weight:700;\n  letter-spacing:.04em;text-transform:uppercase;color:var(--muted)}\ninput[type=text],input[type=number],select,textarea{\n  width:100%;background:var(--bg2);border:1px solid var(--line);color:var(--ink);\n  border-radius:10px;padding:11px 14px;font-size:15px;font-family:inherit}\ntextarea{min-height:76px;resize:vertical}\ninput:focus,select:focus,textarea:focus{outline:none;border-color:var(--teal)}\n.row2{display:grid;grid-template-columns:1fr 1fr;gap:14px}\n@media(max-width:700px){.row2{grid-template-columns:1fr}}\n.btnrow{display:flex;gap:14px;align-items:center;margin-top:20px;flex-wrap:wrap}\nbutton.run{background:linear-gradient(135deg,#14b8a6,#0d9488);border:0;\n  color:#04211c;font-weight:800;font-size:17px;padding:15px 34px;\n  border-radius:12px;cursor:pointer;box-shadow:0 6px 22px rgba(45,212,191,.25)}\nbutton.run:hover{filter:brightness(1.08)}\nbutton.run:disabled{opacity:.45;cursor:default;box-shadow:none}\nbutton.ghost{background:transparent;border:1px solid var(--teal);color:var(--teal);\n  font-weight:700;font-size:15px;padding:13px 26px;border-radius:12px;cursor:pointer}\nbutton.ghost:hover{background:var(--teal-dim)}\nbutton.ghost:disabled{opacity:.45;cursor:default}\n.hint{color:var(--muted);font-size:13.5px}\n.spinner{display:none;align-items:center;gap:10px;color:var(--muted);font-size:14px;margin-top:14px}\n.spinner.show{display:flex}\n.dot{width:12px;height:12px;border-radius:50%;background:var(--teal);\n  animation:pulse 1s infinite ease-in-out}\n@keyframes pulse{0%,100%{transform:scale(.6);opacity:.5}50%{transform:scale(1.2);opacity:1}}\n#output{display:none;margin-top:6px}\n#output.show{display:block}\n.out{background:#0a0f1c;border:1px solid var(--line);border-radius:12px;\n  padding:20px 22px;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;\n  font-size:13px;line-height:1.6;white-space:pre-wrap;word-wrap:break-word;\n  max-height:640px;overflow:auto;color:#c9d6ea}\n.sechead{color:var(--accent);font-weight:800;margin:18px 0 2px;font-size:13.5px}\n.sechead:first-child{margin-top:0}\n.seccap{background:var(--teal-dim);border-left:3px solid var(--teal);\n  padding:8px 12px;margin:4px 0 12px;border-radius:0 8px 8px 0;\n  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;\n  font-size:13.5px;color:#bfe9e2}\n.tok-orch{color:var(--accent);font-weight:700}\n.tok-tool{color:var(--ok);font-weight:700}\n.tok-guard{color:var(--warn);font-weight:700}\n.tok-mem{color:#c084fc;font-weight:700}\n#takeaways{display:none}\n#takeaways.show{display:block}\n.take{background:rgba(52,211,153,.07);border:1px solid rgba(52,211,153,.4);\n  border-radius:var(--radius);padding:22px 26px;margin:26px 0}\n.take h2{color:var(--ok);margin:0 0 10px;font-size:18px}\n.take ul{margin:0;padding-left:20px}\n.take li{margin:8px 0;color:#d5e0f1;font-size:15px}\ntable.dec{width:100%;border-collapse:collapse;margin-top:12px;font-size:14px}\ntable.dec th{background:var(--panel2);color:var(--teal);text-align:left;\n  padding:10px 12px;font-size:12px;letter-spacing:.06em;text-transform:uppercase;\n  border-bottom:1px solid var(--line)}\ntable.dec td{padding:10px 12px;border-bottom:1px solid var(--line);vertical-align:top}\n.pill{display:inline-block;padding:3px 12px;border-radius:999px;font-weight:800;font-size:12px}\n.pill.v{background:var(--ok);color:#04281c}\n.pill.s{background:var(--faint);color:#0b1220}\nfooter{padding:26px 32px 40px;color:var(--faint);font-size:13.5px;text-align:center}\nfooter a{color:var(--teal);text-decoration:none}\nfooter a:hover{text-decoration:underline}\ndetails.raw{margin-top:14px}\ndetails.raw summary{cursor:pointer;color:var(--muted);font-size:13.5px}\n/* --- music mood revamp: why-section + sidebar layout --- */\n.care-layout{display:grid;grid-template-columns:minmax(0,1fr) 340px;gap:26px;align-items:start}\n.care-main{min-width:0}\n.care-sidebar{position:sticky;top:20px;min-width:0}\n@media(max-width:960px){.care-layout{grid-template-columns:1fr}.care-sidebar{position:static}}\n.side-card{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:20px;margin-bottom:20px}\n.side-card h3{margin:0 0 10px;font-size:15px;color:var(--teal)}\n.side-vid{margin-bottom:18px}\n.side-vid:last-child{margin-bottom:0}\n.side-vid iframe{width:100%;aspect-ratio:16/9;border:0;border-radius:10px;display:block;background:#000}\n.side-vid p{font-size:13px;color:var(--muted);margin:8px 0 0;line-height:1.5}\n.why-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;margin:16px 0}\n@media(max-width:700px){.why-grid{grid-template-columns:1fr}}\n.why-grid figure{margin:0}\n.why-grid img{width:100%;aspect-ratio:16/10;object-fit:cover;border-radius:10px;border:1px solid var(--line);display:block;background:#0a0f1c}\n.why-grid figcaption{font-size:12.5px;color:var(--muted);margin-top:6px;line-height:1.5}\n.chal{list-style:none;margin:10px 0 0;padding:0}\n.chal li{position:relative;padding:7px 0 7px 28px;color:#d5e0f1;font-size:15px}\n.chal li::before{content:"!";position:absolute;left:9px;color:var(--warn);font-weight:800}\n.bloglist{list-style:none;margin:0;padding:0}\n.bloglist li{margin:0 0 14px;padding-bottom:14px;border-bottom:1px dashed var(--line)}\n.bloglist li:last-child{margin-bottom:0;padding-bottom:0;border-bottom:0}\n.bloglist a{color:var(--teal);font-weight:700;font-size:14px;text-decoration:none}\n.bloglist a:hover{text-decoration:underline}\n.bloglist .outlet{font-size:12px;color:var(--faint)}\n.bloglist p{font-size:13px;color:var(--muted);margin:4px 0 0;line-height:1.5}\n\n</style>\n</head>\n<body>\n<header><div class="wrap">\n  <h1>Music Mood Agent</h1>\n  <p class="sub">Tell it how you feel. It builds the arc: meet you, lift you, keep you there.</p>\n</div></header>\n<main><div class="wrap care-layout"><div class="care-main">\n<section class="card" id="why">\n  <h2><span class="n">&#9835;</span>Why does this matter in real life?</h2>\n  <p>Music is the fastest emotional lever most of us own. The right song can sharpen your focus before an exam, push you through the last mile of a workout, or soften the tension of a long day &mdash; and everyone has felt the opposite: a sad ballad drifting over a party, aggressive rock at a quiet dinner, one wrong track souring the exact moment it was meant to make.</p>\n  <p>That is because music does not just accompany a mood, it steers it. Therapists use it in clinical settings to calm anxiety, athletes build whole rituals around it, and parents have known since forever that a lullaby does what a lecture cannot.</p>\n  <p>But getting the music right every single time is a job nobody signed up for. We are all amateur DJs of our own emotions, hitting skip on autopilot &mdash; and a fixed playlist cannot respond when your mood shifts mid-evening.</p>\n  <div class="why-grid">\n    <figure><img src="/assets/img/headphones-focus.svg" alt="Person wearing headphones, focused and absorbed in the music" loading="lazy"><figcaption>Lost in it: the right song sharpens focus and turns a hard hour into a flow hour.</figcaption></figure>\n    <figure><img src="/assets/img/festival-crowd.svg" alt="Concert crowd with hands in the air at a music festival" loading="lazy"><figcaption>A crowd moving as one &mdash; shared music turns strangers into a single mood.</figcaption></figure>\n    <figure><img src="/assets/img/relaxing-home.svg" alt="Woman relaxing at home listening to music on headphones" loading="lazy"><figcaption>Winding down: calm music tells the body the day is over.</figcaption></figure>\n    <figure><img src="/assets/img/party-friends.svg" alt="Friends dancing and celebrating together at a party" loading="lazy"><figcaption>The vibe depends on the soundtrack: at a party, the music <i>is</i> the moment.</figcaption></figure>\n  </div>\n  <p><b>The purpose of this demo:</b> it shows an AI agent that reads your situation and the person you are in it, then designs the arc &mdash; meet you where you are, lift you to where you want to be, and keep you there. Try it on yourself below.</p>\n  <p><b>The challenges it tackles:</b></p>\n  <ul class="chal">\n    <li>Playlists are static &mdash; moods aren\'t. A fixed queue can\'t respond when your evening takes a turn.</li>\n    <li>The wrong music at the wrong moment kills the vibe. A party needs lift, a wind-down needs softness &mdash; one queue can\'t do both.</li>\n    <li>Nobody wants to DJ their own emotions all day. Picking the perfect track for every moment is a full-time job we all do badly on autopilot.</li>\n  </ul>\n</section>\n\n\n<section class="card" id="story">\n  <h2><span class="n">1</span>The story</h2>\n  <p>Playlists have a vibe you can\'t explain — and no service shapes the <b>emotional arc</b> of a listening session.</p>\n<p>This demo is an agent that does. You describe your situation in plain words — <i>"stressed after a long workday"</i> — Agent 1 interprets your mood and designs a five-slot emotional arc, Agent 2 searches a mock Spotify-style catalog slot by slot, and Agent 3 tells you <i>why</i> each song fits. It even remembers what worked last time: watch for the <b>[MEMORY-BOOSTED]</b> picks in the study session.</p>\n</section>\n\n<section class="card" id="watch">\n  <h2><span class="n">2</span>What to watch for</h2>\n  <ul class="watch">\n<li>Watch Agent 1 turn plain words into a mood profile with a 5-slot arc: MATCH → LIFT → SUSTAIN.</li>\n<li>Watch Agent 2 call its search tool once per slot — target energy, valence, tags — and pick the best unused track.</li>\n<li>In Situation 3, watch memory kick in: tracks that worked last study session get boosted.</li>\n<li>Every pick comes with a why-it-fits line. No black-box recommendations.</li>\n  </ul>\n</section>\n\n\n\n<section class="card" id="tryown">\n  <h2><span class="n">✎</span>Try your own</h2>\n  <p>Describe your situation in your own words — the agent will read your mood, design an arc, and build you a five-song playlist.</p>\n  <label class="f" for="m_text">Your situation</label>\n  <input type="text" id="m_text" value="I\'m winding down after a long day and want something calm">\n  <label class="f" for="m_occ">Occasion</label>\n  <select id="m_occ">\n    <option value="">Just my mood</option>\n    <option>Studying / exam prep</option>\n    <option>Workout</option>\n    <option>Dinner with friends</option>\n    <option>Road trip</option>\n    <option>Morning routine</option>\n  </select>\n  <div class="btnrow">\n    <button class="ghost" id="customRun">Build my playlist</button>\n    <span class="hint">Same inputs → same output. Deterministic.</span>\n  </div>\n  <div class="spinner" id="cspin"><div class="dot"></div>Reading your mood…</div>\n</section>\n\n\n<section class="card" id="runbox">\n  <h2><span class="n">3</span>Run the demo</h2>\n  <p>Click below to run the full canned demonstration. It takes a few seconds.</p>\n  <div class="btnrow">\n    <button class="run" id="run">&#9654; Run live demo</button>\n  </div>\n  <div class="spinner" id="spin"><div class="dot"></div><span>The agent is reading your mood and building the arc…</span></div>\n  <div id="output">\n    <div class="out" id="outtext"></div>\n    <details class="raw"><summary>Show raw terminal output</summary>\n      <div class="out" id="rawtext"></div>\n    </details>\n  </div>\n</section>\n\n<section class="card" id="takeaways" style="display:none">\n  <div class="take">\n    <h2>What just happened</h2>\n    <ul>\n<li>Three situations, three different arcs — the same engine, different emotional targets.</li>\n<li>The arc guarantee: MATCH your current mood first (an honest start), LIFT toward where you want to be, SUSTAIN once you\'re there.</li>\n<li>Session memory is real: the study session re-weighted tracks that worked before.</li>\n<li>Try your own: describe your situation in “Try your own” and get your five-song arc.</li>\n    </ul>\n  </div>\n</section>\n\n</div>\n<aside class="care-sidebar">\n  <div class="side-card">\n    <h3>Learn more</h3>\n    <p style="font-size:13.5px;color:var(--muted);margin:0 0 14px">Want to go deeper on music, mood, and the brain? Start with these.</p>\n    <div class="side-vid">\n      <iframe src="https://www.youtube-nocookie.com/embed/R0JKCYZ8hng" title="TED-Ed: How playing an instrument benefits your brain" loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>\n      <p>TED-Ed: Anita Collins explains the fireworks that go off in your brain when music hits &mdash; the neuroscience of why music moves us.</p>\n    </div>\n    <div class="side-vid">\n      <iframe src="https://www.youtube-nocookie.com/embed/x-0s1xyan98" title="Bilateral Stimulation Music Therapy for anxiety, stress, PTSD" loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>\n      <p>A therapist-designed hour of bilateral music for anxiety, stress, and PTSD &mdash; music as a clinical tool, not just entertainment.</p>\n    </div>\n    <div class="side-vid">\n      <iframe src="https://www.youtube-nocookie.com/embed/kZJ8BfEu-P8" title="This Is Your Brain On Music - How Music Benefits The Brain" loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>\n      <p>A tour of how listening changes the brain &mdash; dopamine, memory, even exercise &mdash; with the studies behind each claim.</p>\n    </div>\n  </div>\n  <div class="side-card">\n    <h3>Go deeper &mdash; articles</h3>\n    <ul class="bloglist">\n      <li><a href="https://neurolaunch.com/how-does-music-affect-your-mood/" target="_blank" rel="noopener">Music\'s Impact on Mood and Emotions</a> <span class="outlet">&middot; NeuroLaunch</span>\n        <p>How music hijacks the brain\'s reward circuitry to shift your emotional state &mdash; the mechanics in plain language.</p></li>\n      <li><a href="https://www.earth.com/science/music-has-the-power-to-change-the-mood-of-our-memories/" target="_blank" rel="noopener">Music has the power to reshape the \'mood\' of our old memories</a> <span class="outlet">&middot; Earth.com</span>\n        <p>Georgia Tech research showing that soundtracks can re-tint the emotional tone of difficult memories &mdash; and the effect sticks.</p></li>\n      <li><a href="https://www.themarginalian.org/2015/01/29/music-brain-ted-ed/" target="_blank" rel="noopener">How Playing Music Benefits Your Brain More than Any Other Activity</a> <span class="outlet">&middot; The Marginalian</span>\n        <p>Maria Popova on the TED-Ed lesson: why making music changes the body\'s most important organ.</p></li>\n    </ul>\n  </div>\n</aside>\n\n</div></main>\n<footer><div class="wrap">\n  <a href="https://github.com/ynpreet/music-mood-agent" target="_blank" rel="noopener">View the project on GitHub</a>\n  &nbsp;&middot;&nbsp; All data in this demo is synthetic / fictional.\n</div></footer>\n\n<script>\nconst SECTIONS = [["SITUATION 1/3", "Stressed after a long workday: the agent meets you where you are, then lifts."], ["SITUATION 2/3", "Road trip with friends: a high-energy arc with different targets."], ["SITUATION 3/3", "Can\'t focus, exam tomorrow: watch for [MEMORY-BOOSTED] \\u2014 past wins weighted higher."]];\nfunction esc(s){return s.replace(/&/g,\'&amp;\').replace(/</g,\'&lt;\').replace(/>/g,\'&gt;\');}\nfunction decorate(line){\n  let h = esc(line);\n  h = h.replace(/\\[ORCHESTRATOR\\]/g,\'<span class="tok-orch">[ORCHESTRATOR]</span>\');\n  h = h.replace(/\\[TOOL [^\\]]+\\]/g,function(m){return \'<span class="tok-tool">\'+m+\'</span>\';});\n  h = h.replace(/\\[MEMORY\\]/g,\'<span class="tok-mem">[MEMORY]</span>\');\n  h = h.replace(/GUARDRAIL/g,\'<span class="tok-guard">GUARDRAIL</span>\');\n  return h;\n}\nfunction renderOut(text){\n  document.getElementById(\'rawtext\').textContent = text;\n  const lines = text.split(\'\\n\');\n  let html = \'\';\n  for(const line of lines){\n    let matched = null;\n    for(const s of SECTIONS){ if(line.indexOf(s.m) !== -1){ matched = s; break; } }\n    if(matched){\n      html += \'<div class="sechead">\'+decorate(line)+\'</div>\'+\n              \'<div class="seccap">\'+matched.c+\'</div>\';\n      continue;\n    }\n    html += decorate(line) + \'\\n\';\n  }\n  document.getElementById(\'outtext\').innerHTML = html;\n  document.getElementById(\'output\').classList.add(\'show\');\n  document.getElementById(\'output\').scrollIntoView({behavior:\'smooth\',block:\'start\'});\n}\nfunction showTakeaways(){\n  const t = document.getElementById(\'takeaways\');\n  t.style.display=\'block\'; t.classList.add(\'show\');\n  t.scrollIntoView({behavior:\'smooth\',block:\'start\'});\n}\ndocument.getElementById(\'run\').addEventListener(\'click\',function(){\n  const btn=this, spin=document.getElementById(\'spin\');\n  btn.disabled=true; spin.classList.add(\'show\');\n  fetch(\'/api/run\').then(r=>r.json()).then(j=>{\n    spin.classList.remove(\'show\'); btn.disabled=false;\n    renderOut(j.output);\n    if(typeof loadDecisionTable===\'function\') loadDecisionTable();\n    showTakeaways();\n  }).catch(e=>{spin.classList.remove(\'show\');btn.disabled=false;alert(\'Run failed: \'+e);});\n});\n\nfunction collectCustom(){\n  const t=document.getElementById(\'m_text\').value.trim();\n  const occ=document.getElementById(\'m_occ\').value;\n  return {situation: occ ? t+\'. Occasion: \'+occ : t};\n}\n\nfunction wireCustom(){\n  const b=document.getElementById(\'customRun\');\n  if(!b) return;\n  b.addEventListener(\'click\',function(){\n    const spin=document.getElementById(\'cspin\');\n    b.disabled=true; spin.classList.add(\'show\');\n    fetch(\'/api/custom\',{method:\'POST\',headers:{\'Content-Type\':\'application/json\'},\n      body:JSON.stringify(collectCustom())})\n    .then(r=>r.json()).then(j=>{\n      spin.classList.remove(\'show\'); b.disabled=false;\n      if(j.error){alert(j.error);return;}\n      renderOut(j.output); showTakeaways();\n    }).catch(e=>{spin.classList.remove(\'show\');b.disabled=false;alert(\'Run failed: \'+e);});\n  });\n}\nwireCustom();\n</script>\n</body>\n</html>\n'

class Handler(http.server.BaseHTTPRequestHandler):
    server_version = "WorkshopUI/1.0"

    def _send(self, body, ctype="text/html; charset=utf-8"):
        data = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _json(self, obj):
        self._send(json.dumps(obj), "application/json; charset=utf-8")

    def _read_json(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
        except (TypeError, ValueError):
            length = 0
        raw = self.rfile.read(length) if length else b"{}"
        try:
            return json.loads(raw.decode("utf-8") or "{}")
        except Exception:
            return {}

    def _serve_asset(self, path):
        safe = (HERE / path.lstrip("/")).resolve()
        try:
            safe.relative_to(HERE / "assets")
        except ValueError:
            return self.send_error(403, "forbidden")
        if not safe.is_file():
            return self.send_error(404, "not found")
        ctype, _ = mimetypes.guess_type(str(safe))
        data = safe.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype or "application/octet-stream")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "public, max-age=3600")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = urllib.parse.urlsplit(self.path).path
        if path in ("/", "/index.html"):
            self._send(PAGE)
        elif path == "/api/run":
            self._json({"output": _capture_canned()})
        elif path.startswith("/assets/"):
            self._serve_asset(path)
        else:
            self.send_error(404, "not found")

    def do_POST(self):
        path = urllib.parse.urlsplit(self.path).path
        if path == "/api/custom":
            params = self._read_json()
            self._json(_capture_custom(run_custom, params))
        else:
            self.send_error(404, "not found")

    def log_message(self, fmt, *args):
        sys.stderr.write("ui: " + (fmt % args) + "\n")


def main():
    server = http.server.ThreadingHTTPServer((HOST, PORT), Handler)
    print("Music Mood Agent demo UI -> http://localhost:8005")
    print("Press Ctrl-C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped.")


if __name__ == "__main__":
    main()
