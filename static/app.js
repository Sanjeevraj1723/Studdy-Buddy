const $=id=>document.getElementById(id);
document.querySelectorAll('#tabs button').forEach(b=>b.onclick=()=>{
  document.querySelectorAll('#tabs button,section').forEach(e=>e.classList.remove('on'));
  b.classList.add('on');$(b.dataset.t).classList.add('on');
});

/* ---------- Doubt solver ---------- */
let imgFile=null,lastAns='';
$('img').onchange=e=>{
  imgFile=e.target.files[0]||null;
  if(imgFile){$('prev').src=URL.createObjectURL(imgFile);$('prev').style.display='block'}
};
const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
let rec=null;
if(!SR){$('mic').hidden=true}else{
  $('mic').onclick=()=>{
    if(rec){rec.stop();return}
    rec=new SR();rec.lang={English:'en-IN',Tamil:'ta-IN',Hindi:'hi-IN'}[$('lang').value];rec.interimResults=false;
    $('mic').classList.add('rec');$('mic').textContent='⏹ Listening…';
    rec.onresult=e=>{$('q').value+=($('q').value?' ':'')+e.results[0][0].transcript};
    rec.onend=()=>{rec=null;$('mic').classList.remove('rec');$('mic').textContent='🎤 Speak'};
    rec.onerror=()=>{};
    rec.start();
  };
}
$('say').onclick=()=>{
  speechSynthesis.cancel();
  const u=new SpeechSynthesisUtterance(lastAns.slice(0,1500));
  u.lang={English:'en-IN',Tamil:'ta-IN',Hindi:'hi-IN'}[$('lang').value];
  speechSynthesis.speak(u);
};
$('ask').onclick=async()=>{
  const q=$('q').value.trim();
  if(!q&&!imgFile){$('note').textContent='Type, speak, or upload your doubt first.';return}
  $('note').textContent='';$('ask').disabled=true;
  const a=$('ans');a.style.display='block';a.textContent='Thinking…';
  const fd=new FormData();
  fd.append('question',q);fd.append('level',$('lvl').value);fd.append('language',$('lang').value);fd.append('style',$('lev').value);
  if(imgFile)fd.append('image',imgFile);
  try{
    const r=await fetch('/api/ask',{method:'POST',body:fd});
    const d=await r.json();
    if(!r.ok)throw new Error(d.error||'Something went wrong.');
    lastAns=d.answer;a.textContent=d.answer;$('say').hidden=false;
  }catch(e){a.textContent=e.message||'Could not get an answer. Please try again.'}
  $('ask').disabled=false;
};

/* ---------- Timetable ---------- */
const DAYS=['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];
const COL=['#c9b8ff','#ffd3a8','#a8e6cf','#ffb3c1','#a8d8ff','#fff1a8','#d3f0a0','#f5b8f0'];
$('days').innerHTML=DAYS.map((d,i)=>`<label><input type="checkbox" value="${d}" ${i<6?'checked':''}>${d}</label>`).join('');
const subs=$('subs');
function addSub(v=''){
  if(subs.children.length>=8)return;
  const d=document.createElement('div');d.className='sub';
  d.innerHTML='<input placeholder="Subject name" aria-label="Subject name"><button class="btn alt" type="button" aria-label="Remove">✕</button>';
  d.firstChild.value=v;d.lastChild.onclick=()=>{d.remove();chk()};
  subs.appendChild(d);chk();
}
function chk(){$('addS').disabled=subs.children.length>=8;$('addS').textContent=subs.children.length>=8?'Max 8 subjects':'+ Add subject'}
['Maths','Physics','Chemistry','English'].forEach(addSub);
$('addS').onclick=()=>addSub();
let ttText='';
$('gen').onclick=()=>{
  const S=[...subs.querySelectorAll('input')].map(i=>i.value.trim()).filter(Boolean);
  const D=[...document.querySelectorAll('#days input:checked')].map(i=>i.value);
  if(!S.length||!D.length){$('tt').textContent='Add at least one subject and one day.';return}
  const n=Math.min(10,Math.max(1,+$('ns').value||4)),len=Math.min(180,Math.max(15,+$('ln').value||45));
  const [h,m]=$('st').value.split(':').map(Number);let t0=(h||0)*60+(m||0);
  const f=x=>String(Math.floor(x/60)%24).padStart(2,'0')+':'+String(x%60).padStart(2,'0');
  let k=0,html='<table><tr><th>Time</th>'+D.map(d=>`<th>${d}</th>`).join('')+'</tr>',txt='';
  const cells=D.map(()=>[]);
  for(let r=0;r<n;r++)D.forEach((_,c)=>cells[c].push(k++%S.length));
  for(let r=0;r<n;r++){
    const s=t0+r*(len+10);
    html+=`<tr><td><b>${f(s)}–${f(s+len)}</b></td>`;
    txt+=`${f(s)}-${f(s+len)}: `;
    D.forEach((d,c)=>{const i=cells[c][r];html+=`<td style="background:${COL[i]};color:#222">${S[i].replace(/</g,'&lt;')}</td>`;txt+=`${d}=${S[i]}  `});
    html+='</tr>';txt+='\n';
  }
  $('tt').innerHTML=html+'</table>';ttText='Study-Buddy Timetable\n\n'+txt;$('dl').hidden=false;
};
$('dl').onclick=()=>{
  const url=URL.createObjectURL(new Blob([ttText],{type:'text/plain'}));
  const a=document.createElement('a');a.href=url;a.download='timetable.txt';a.click();URL.revokeObjectURL(url);
};

/* ---------- Warm-up ---------- */
let bt=null;
$('br').onclick=()=>{
  if(bt){clearInterval(bt);bt=null;$('circ').classList.remove('big');$('circ').textContent='Ready';$('br').textContent='Start';return}
  let s=0,phase=true;$('br').textContent='Stop';
  const step=()=>{
    if(s>=60){clearInterval(bt);bt=null;$('circ').textContent='Well done! 🎉';$('circ').classList.remove('big');$('br').textContent='Start';return}
    $('circ').classList.toggle('big',phase);$('circ').textContent=phase?'Breathe in':'Breathe out';phase=!phase;s+=4;
  };
  step();bt=setInterval(step,4000);
};
const ST=['Neck rolls','Shoulder shrugs','Arm stretch overhead','Wrist and finger circles','Stand and touch toes','Look far away (rest your eyes)'];
let sti=null;
$('sb').onclick=()=>{
  clearInterval(sti);let i=0,t=20;
  const show=()=>{$('stre').textContent=`${ST[i]} (${t}s)`};show();
  sti=setInterval(()=>{
    t--;if(t<=0){i++;t=20}
    if(i>=ST.length){clearInterval(sti);$('stre').textContent='All done! Back to studying 💪';return}
    show();
  },1000);
};
const TZ=[['What has keys but cannot open locks?','A keyboard (or piano).'],['If 5 machines make 5 items in 5 minutes, how long do 100 machines take to make 100 items?','5 minutes.'],['What comes next: 2, 6, 12, 20, 30, ?','42 (differences grow by 2).'],['I speak without a mouth and hear without ears. What am I?','An echo.'],['A bat and ball cost ₹110 together. The bat costs ₹100 more than the ball. Ball price?','₹5.'],['Which number is next: 1, 1, 2, 3, 5, 8, ?','13 (Fibonacci).']];
let cur=null;
$('tb').onclick=()=>{cur=TZ[Math.floor(Math.random()*TZ.length)];$('tz').textContent=cur[0];$('tr').hidden=false};
$('tr').onclick=()=>{if(cur)$('tz').textContent=cur[0]+'\n→ '+cur[1]};

/* ---------- Study cards ---------- */
let cards=[],ci=0,fl=false;
try{cards=JSON.parse(localStorage.getItem('sb_cards')||'[]')}catch(e){cards=[]}
if(!Array.isArray(cards))cards=[];
const saveC=()=>{try{localStorage.setItem('sb_cards',JSON.stringify(cards))}catch(e){}};
function showC(){
  $('cs').hidden=!cards.length;
  if(!cards.length)return;
  ci=(ci+cards.length)%cards.length;
  const c=cards[ci];
  $('fc').textContent=fl?c.b:c.f;
  $('fc').classList.toggle('back',fl);
  $('cc').textContent=`Card ${ci+1} of ${cards.length} · ${fl?'answer':'question'}`;
}
function flipC(){fl=!fl;showC()}
$('fc').onclick=flipC;$('cfl').onclick=flipC;
$('fc').onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();flipC()}};
$('cp').onclick=()=>{ci--;fl=false;showC()};
$('cx').onclick=()=>{ci++;fl=false;showC()};
$('csh').onclick=()=>{for(let i=cards.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[cards[i],cards[j]]=[cards[j],cards[i]]}ci=0;fl=false;saveC();showC()};
$('cd').onclick=()=>{cards.splice(ci,1);fl=false;saveC();showC()};
$('ca').onclick=()=>{
  const f=$('cf').value.trim(),b=$('cb').value.trim();
  if(!f||!b){$('cn').textContent='Fill in both the front and the back.';return}
  cards.push({f,b});ci=cards.length-1;fl=false;$('cf').value='';$('cb').value='';$('cn').textContent='Card added.';saveC();showC();
};
$('cg').onclick=async()=>{
  const t=$('ct').value.trim();
  if(!t){$('cn').textContent='Enter a topic first.';return}
  $('cg').disabled=true;$('cn').textContent='Making cards…';
  try{
    const r=await fetch('/api/cards',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({topic:t,level:$('lvl').value})});
    const d=await r.json();
    if(!r.ok)throw new Error(d.error||'Could not make cards.');
    const ok=(d.cards||[]).filter(x=>x&&x.f&&x.b).map(x=>({f:String(x.f),b:String(x.b)}));
    if(!ok.length)throw new Error('Could not make cards. Please try again.');
    ci=cards.length;cards.push(...ok);fl=false;saveC();showC();$('cn').textContent='Added '+ok.length+' cards.';
  }catch(e){$('cn').textContent=e.message||'Could not make cards. Please try again.'}
  $('cg').disabled=false;
};
showC();
