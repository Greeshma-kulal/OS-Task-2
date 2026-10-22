import json, time
from pathlib import Path
from threading import Lock

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "generated_html"

class EventRecorder:
    def __init__(self, title, kind, people, resources):
        self.title, self.kind, self.people, self.resources = title, kind, people, resources
        self.started = time.monotonic()
        self.events = []
        self.lock = Lock()

    def record(self, actor, state, message, **extra):
        event = {"t": round(time.monotonic()-self.started, 3), "actor": actor,
                 "state": state, "message": message}
        event.update(extra)
        with self.lock:
            self.events.append(event)
        print(f'{event["t"]:6.3f}s | {actor:>2} | {state:<10} | {message}')

    def write_html(self, filename, final_value=None):
        with self.lock:
            events = list(self.events)
        data = json.dumps({"title": self.title, "kind": self.kind, "people": self.people,
                           "resources": self.resources, "events": events, "final_value": final_value})
        page = TEMPLATE.replace("__DATA__", data.replace("</", "<\\/"))
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output = OUTPUT_DIR / filename
        output.write_text(page, encoding="utf-8")
        print(f"\nGenerated {output.resolve()} ({len(events)} recorded events)")

TEMPLATE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Synchronization Replay</title>
<style>
:root{--ink:#26352f;--muted:#66756d;--paper:#f3f6f2;--green:#34785f;--gold:#d1a13e;--blue:#5c82b5;--line:#dfe7e0}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:15px Arial,sans-serif}
main{max-width:1120px;margin:auto;padding:26px 18px}h1{margin:0;font-size:clamp(25px,4vw,36px)}h2{margin:4px 0 14px}.sub,.hint{color:var(--muted);line-height:1.5}
.panel,.controls{background:#fff;border:1px solid var(--line);border-radius:15px;padding:16px;margin:12px 0;box-shadow:0 2px 8px #20332808}
.controls{display:flex;align-items:center;gap:9px;flex-wrap:wrap}.controls label{display:flex;align-items:center;gap:6px}
button,select{padding:9px 13px;border:1px solid #cbd8ce;border-radius:9px;background:#fff;color:var(--ink);cursor:pointer;font-weight:600}
button.primary{background:var(--green);color:#fff;border-color:var(--green)}button:disabled{opacity:.5;cursor:not-allowed}
#status{margin-left:auto;color:var(--muted);font-weight:600}#progress{width:100%;flex-basis:100%;margin-top:4px;accent-color:var(--green)}
.grid{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(280px,.85fr);gap:14px;align-items:stretch}
#stage{position:relative;min-height:480px;background:#fafcfa;border:1px solid #edf1ed;border-radius:12px;overflow:hidden}
.resource{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:34%;min-height:112px;border:3px solid #c8b28e;background:#eee5d6;border-radius:18px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px;text-align:center;padding:12px;z-index:1}
.person{position:absolute;width:82px;min-height:76px;border:2px solid #d2ddd5;border-radius:15px;background:#eaf0ec;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;font-size:12px;transition:background .18s,border-color .18s,transform .18s;text-align:center;padding:7px;z-index:2}
.person b{font-size:14px}.person span{font-size:12px;text-transform:capitalize}
.person.active{background:#dce9fb;border-color:var(--blue)}.person.busy{background:#d7eee2;border-color:var(--green);box-shadow:0 0 0 4px #34785f20}.person.waiting{background:#fff0c9;border-color:var(--gold)}
.fork{position:absolute;border-radius:9px;padding:6px 8px;background:#e5eee7;border:1px solid #b7cabb;font-size:11px;font-weight:600;z-index:3;white-space:nowrap}
.fork.held{background:#d7eee2;border-color:var(--green);color:#21533f}
.stats{display:flex;gap:9px;flex-wrap:wrap;margin:12px 0}.stat{background:#f1f5f1;padding:10px 12px;border-radius:10px;min-width:95px;flex:1}.stat small{display:block;color:var(--muted);margin-bottom:3px}.stat b{font-size:21px}
#message{min-height:24px;line-height:1.5;margin-bottom:0}.timeline-panel{min-width:0}#timeline{padding-left:24px;max-height:430px;overflow:auto;font-size:12px;line-height:1.7;color:var(--muted)}#timeline li{padding:2px 4px;border-radius:5px}#timeline li.current{background:#edf5ef;color:var(--ink);font-weight:700}
@media(max-width:760px){main{padding:16px 10px}.grid{grid-template-columns:1fr}#stage{min-height:430px}.resource{width:38%;min-height:90px;font-size:13px}.person{width:70px;min-height:66px}.fork{font-size:10px;padding:5px}}
</style></head><body><main>
<p style="font-size:11px;letter-spacing:2px;font-weight:bold;color:var(--green)">OPERATING SYSTEMS · RECORDED EXECUTION</p>
<h1 id="title"></h1><p class="sub">Replay based on events captured by the Python synchronization program.</p>
<section class="controls"><button id="play" class="primary">Play</button> <button id="pause">Pause</button> <button id="reset">Reset</button>
<label> Speed <select id="speed"><option value="1">1×</option><option value="2">2×</option><option value=".5">0.5×</option></select></label><span id="status">Ready</span><input id="progress" type="range" min="0" max="0" value="0"></section>
<section class="grid"><div class="panel"><div id="stage"></div><div class="stats"><div class="stat"><small>Events</small><b id="count">0</b></div><div class="stat"><small>Position</small><b id="position">0/0</b></div><div class="stat"><small>Final value</small><b id="finalValue">—</b></div></div><p id="message">No events.</p></div>
<div class="panel"><h2>Execution timeline</h2><ol id="timeline"></ol><p class="hint">Use playback controls or the slider to inspect recorded states.</p></div></section>
<p class="hint">This page replays the captured execution trace. It does not invent a separate sequence of states.</p></main>
<script>
const D=__DATA__,stage=document.querySelector('#stage'),timeline=document.querySelector('#timeline');
const progress=document.querySelector('#progress'),status=document.querySelector('#status'),message=document.querySelector('#message');
let i=0,timer=null,paused=false;
document.querySelector('#title').textContent=D.title;document.querySelector('#count').textContent=D.events.length;
document.querySelector('#finalValue').textContent=D.final_value==null?'—':D.final_value;progress.max=Math.max(0,D.events.length-1);
function el(tag,cls,text){const x=document.createElement(tag);x.className=cls||'';x.textContent=text||'';return x}
function setup(){
 if(D.kind==='rw'){
  const db=el('div','resource');db.id='db';
  db.innerHTML='<b>SHARED DATA</b><span id="dbs">Available</span><strong id="value">0</strong>';stage.append(db);
  const spots=[['50%','8%'],['82%','50%'],['50%','82%'],['18%','50%'],['50%','22%']];
  D.people.forEach((p,n)=>{const a=el('div','person');a.id='a'+p;
   a.style.left=spots[n][0];a.style.top=spots[n][1];a.style.transform='translate(-50%,-50%)';
   a.innerHTML='<b>'+p+'</b><span>Waiting</span>';stage.append(a)});
 }else{
  const table=el('div','resource');table.style.width='36%';table.style.minHeight='126px';
  table.innerHTML='<b>SHARED TABLE</b><span>4 philosophers</span><strong>4 forks</strong>';stage.append(table);
  const peoplePos=[['50%','9%'],['83%','50%'],['50%','88%'],['17%','50%']];
  const forkPos=[['70%','24%'],['70%','72%'],['24%','72%'],['24%','24%']];
  D.people.forEach((p,n)=>{const a=el('div','person');a.id='a'+p;
   a.style.left=peoplePos[n][0];a.style.top=peoplePos[n][1];a.style.transform='translate(-50%,-50%)';
   a.innerHTML='<b>'+p+'</b><span>Thinking</span>';stage.append(a)});
  D.resources.forEach((r,n)=>{const f=el('div','fork',r+': free');f.id='f'+r;
   f.style.left=forkPos[n][0];f.style.top=forkPos[n][1];f.style.transform='translate(-50%,-50%)';stage.append(f)});
 }
}
function render(n){
 if(!D.events.length)return;i=Math.max(0,Math.min(n,D.events.length-1));const e=D.events[i];
 D.people.forEach(p=>{const a=document.querySelector('#a'+p);if(a)a.classList.remove('active','busy','waiting')});
 const a=document.querySelector('#a'+e.actor);
 if(a){a.classList.add(['waiting','hungry','acquiring'].includes(e.state)?'waiting':(['writing','eating'].includes(e.state)?'busy':'active'));a.querySelector('span').textContent=e.state}
 if(D.kind==='rw'){const db=document.querySelector('#db');db.classList.remove('active','busy');document.querySelector('#dbs').textContent=e.state==='reading'?'Readers reading':e.state==='writing'?'Writer writing':'Available';if(e.state==='reading')db.classList.add('active');if(e.state==='writing')db.classList.add('busy');if(e.value!==undefined)document.querySelector('#value').textContent=e.value}
 else D.resources.forEach(r=>{const f=document.querySelector('#f'+r);const owner=(e.owners||{})[r];f.textContent=r+': '+(owner||'free');f.classList.toggle('held',Boolean(owner))});
 message.textContent=e.message;document.querySelector('#position').textContent=(i+1)+'/'+D.events.length;progress.value=i;
 [...timeline.children].forEach((li,n)=>li.classList.toggle('current',n===i));
}
D.events.forEach(e=>{const li=el('li','',e.t.toFixed(3)+'s · '+e.actor+' · '+e.message);timeline.append(li)});
function stop(){if(timer){clearTimeout(timer);timer=null}}
function advance(){if(paused||i>=D.events.length-1){stop();status.textContent=paused?'Paused':'Finished';document.querySelector('#play').disabled=false;return}
 const gap=Math.max(200,Math.min(1200,(((D.events[i+1].t-D.events[i].t)||.35)*1000)/Number(document.querySelector('#speed').value)));
 timer=setTimeout(()=>{render(i+1);advance()},gap)}
document.querySelector('#play').onclick=()=>{stop();paused=false;if(i>=D.events.length-1)render(0);status.textContent='Playing';advance()};
document.querySelector('#pause').onclick=()=>{paused=true;stop();document.querySelector('#play').disabled=false;status.textContent='Paused'};
document.querySelector('#reset').onclick=()=>{stop();paused=false;render(0);document.querySelector('#play').disabled=false;status.textContent='Ready'};
progress.oninput=()=>{stop();paused=true;render(Number(progress.value));document.querySelector('#play').disabled=false;status.textContent='Paused'};
setup();if(D.events.length)render(0);else status.textContent='No events';
</script></body></html>"""
