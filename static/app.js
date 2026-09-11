const $ = (selector) => document.querySelector(selector);
const query = $('#query');
const button = $('#researchButton');
const states = {welcome: $('#welcome'), loading: $('#loading'), result: $('#result')};
let activeReportId = null;

function show(name){ Object.entries(states).forEach(([key, el]) => el.classList.toggle('hidden', key !== name)); }
function toast(message){ const el=$('#toast'); el.textContent=message; el.classList.remove('hidden'); setTimeout(()=>el.classList.add('hidden'),5000); }
function escapeHtml(text){ const div=document.createElement('div'); div.textContent=text; return div.innerHTML; }
function markdown(text){
  let html=escapeHtml(text);
  html=html.replace(/^### (.+)$/gm,'<h3>$1</h3>').replace(/^## (.+)$/gm,'<h2>$1</h2>').replace(/^# (.+)$/gm,'<h1>$1</h1>');
  html=html.replace(/\*\*(.+?)\*\*/g,'<strong>$1</strong>').replace(/\[(\d+)\]/g,'<a href="#source-$1">[$1]</a>');
  html=html.replace(/^(?:- |\* )(.+)$/gm,'<li>$1</li>').replace(/(?:<li>.*<\/li>\n?)+/g,m=>`<ul>${m}</ul>`);
  return html.split(/\n\n+/).map(block=>/^<(h\d|ul)/.test(block)?block:`<p>${block.replace(/\n/g,'<br>')}</p>`).join('');
}
function render(data){
  activeReportId=data.id; $('#exportButton').disabled=false;
  $('#resultDate').textContent=new Date(data.created_at).toLocaleString();
  $('#resultCount').textContent=`${data.sources.length} sources reviewed`;
  $('#report').innerHTML=markdown(data.report);
  $('#sourceBadge').textContent=data.sources.length;
  $('#sources').innerHTML=data.sources.map((s,i)=>`<a id="source-${i+1}" class="source" href="${escapeHtml(s.url)}" target="_blank" rel="noopener"><small>${String(i+1).padStart(2,'0')} · ${escapeHtml(s.domain)}</small><strong>${escapeHtml(s.title)}</strong><p>${escapeHtml((s.snippet||'').slice(0,130))}</p></a>`).join('');
  show('result'); loadHistory();
}
async function runResearch(){
  const text=query.value.trim(); if(text.length<3){toast('Enter a research question first.');query.focus();return;}
  button.disabled=true; show('loading');
  const messages=['Finding relevant sources…','Reading and comparing evidence…','Building your cited report…']; let index=0;
  const timer=setInterval(()=>{$('#loadingText').textContent=messages[Math.min(++index,messages.length-1)]},2200);
  try{
    const response=await fetch('/api/research',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({query:text,depth:$('#depth').value,focus:$('#focus').value})});
    const data=await response.json(); if(!response.ok) throw new Error(data.detail||'Research failed'); render(data);
  }catch(error){show('welcome');toast(error.message)}finally{clearInterval(timer);button.disabled=false;}
}
async function loadHistory(){
  try{const rows=await fetch('/api/history').then(r=>r.json()); $('#history').innerHTML=rows.length?rows.map(r=>`<button class="history-item" data-id="${r.id}" title="${escapeHtml(r.query)}">${escapeHtml(r.query)}</button>`).join(''):'<div class="muted">No saved reports yet.</div>';}catch{}
}
async function openReport(id){try{const data=await fetch(`/api/reports/${id}`).then(r=>r.json());query.value=data.query;render(data);document.querySelector('.sidebar').classList.remove('open');}catch{toast('Could not open that report.')}}
button.addEventListener('click',runResearch); query.addEventListener('keydown',e=>{if((e.ctrlKey||e.metaKey)&&e.key==='Enter')runResearch()});
document.querySelectorAll('.prompt-card').forEach(card=>card.addEventListener('click',()=>{query.value=card.dataset.query;query.focus();}));
$('#history').addEventListener('click',e=>{const item=e.target.closest('[data-id]');if(item)openReport(item.dataset.id)});
$('#newResearch').addEventListener('click',()=>{query.value='';activeReportId=null;$('#exportButton').disabled=true;show('welcome');query.focus();document.querySelector('.sidebar').classList.remove('open')});
$('#exportButton').addEventListener('click',()=>{if(activeReportId)location.href=`/api/reports/${activeReportId}/export`});
$('#menuButton').addEventListener('click',()=>document.querySelector('.sidebar').classList.toggle('open'));
loadHistory();

