const canvas = document.getElementById('art');
const ctx = canvas.getContext('2d');
const statusEl = document.getElementById('status');

function hashCode(str){
  let h=0; for(let i=0;i<str.length;i++){ h=((h<<5)-h)+str.charCodeAt(i); h|=0 }
  return h>>>0;
}

function rand(seed){
  let x = seed || 123456789;
  return function(){ x ^= x << 13; x ^= x >>> 17; x ^= x << 5; return (x>>>0)/4294967296 }
}

function pick(arr, r){ return arr[Math.floor(r()*arr.length)] }

function draw(params){
  const { palette, density, blur, motion, geometryBias, symmetry, noiseScale, seed } = params;
  const r = rand(hashCode(seed));
  ctx.fillStyle = '#0a0a0a';
  ctx.fillRect(0,0,canvas.width,canvas.height);

  const n = Math.floor(density * 3500);
  for(let i=0;i<n;i++){
    const t = i * 0.003 * motion;
    const x = canvas.width  * ( (Math.sin(i*noiseScale + t) + 1)/2 * (0.9) + 0.05 );
    const y = canvas.height * ( (Math.cos(i*noiseScale + t) + 1)/2 * (0.9) + 0.05 );
    const color = pick(palette, r);
    ctx.fillStyle = color + Math.floor(120 + symmetry*100).toString(16);
    if(geometryBias === 'lines'){
      ctx.fillRect(x, y, 1 + r()*3, 20*(1-symmetry));
    } else if(geometryBias === 'polys'){
      ctx.beginPath(); ctx.arc(x,y, 1 + r()*3, 0, Math.PI*2); ctx.fill();
    } else if(geometryBias === 'blobs'){
      ctx.beginPath(); ctx.ellipse(x,y, 6*(1+symmetry), 2*(1+symmetry), 0, 0, Math.PI*2); ctx.fill();
    } else {
      ctx.beginPath(); ctx.arc(x,y, 1 + r()*2, 0, Math.PI*2); ctx.fill();
    }
    if(symmetry > 0.6){ ctx.beginPath(); ctx.arc(canvas.width - x, y, 1 + r()*2, 0, Math.PI*2); ctx.fill(); }
  }
  if(blur>0){ ctx.fillStyle = 'rgba(0,0,0,0.08)'; ctx.fillRect(0,0,canvas.width,canvas.height); }
}

async function go(){
  statusEl.textContent = 'Fetching taste…';
  const res = await fetch('/api/preview');
  if(!res.ok){ statusEl.textContent = 'Please connect Spotify.'; return }
  const data = await res.json();
  statusEl.textContent = '';
  draw(data.params);
}

document.getElementById('refresh').addEventListener('click', go);
// auto-run if already authed
fetch('/api/preview').then(r=>{ if(r.ok){ r.json().then(d=>draw(d.params)) } });