/* Reflect Group wave mark for secondary pages: the same 80-bar wave profile as the site, breathing gently. */
window.reflectMark=function(c){
  const ctx=c.getContext('2d'); if(!ctx) return;
  const BARS=80, stops=[[0x6b/255,0x57/255,0x40/255],[0xdc/255,0xcf/255,0xbb/255],[0xb8/255,0x9d/255,0x78/255],[0x8f/255,0x7a/255,0x5c/255],[0x8a/255,0x75/255,0x57/255]];
  const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
  const col=deg=>{ const n=stops.length, p=((deg%360)+360)%360/360*n, i=Math.floor(p)%n, f=p-Math.floor(p), a=stops[i], b=stops[(i+1)%n]; return 'rgb('+[0,1,2].map(k=>Math.round((a[k]+(b[k]-a[k])*f)*255)).join(',')+')'; };
  const prof=(base,op,ip)=>{ const wo=0.5+0.5*Math.sin(3*base+op), wi=0.5+0.5*Math.sin(3*base+ip); return [0.69*(1-0.12*wi), 1+0.18*wo]; };
  const dpr=Math.min(devicePixelRatio||1,2), W=c.width/dpr, H=c.height/dpr; ctx.setTransform(dpr,0,0,dpr,0,0);
  const R=Math.min(W,H)*0.33, cx=W/2, cy=H/2, t0=performance.now();
  function frame(now){
    const ptw=reduce?0:(now-t0)/1000, spin=ptw*0.6, op=1.2+spin, ip=1.2-spin;
    ctx.clearRect(0,0,W,H); ctx.lineWidth=(2*Math.PI*R/BARS)*0.46; ctx.lineCap='butt';
    for(let i=0;i<BARS;i++){ const base=i*Math.PI*2/BARS, deg=i*360/BARS, r=deg*Math.PI/180; const [ri,ro]=prof(base,op,ip);
      ctx.strokeStyle=col(deg); ctx.beginPath(); ctx.moveTo(cx+Math.cos(r)*R*ri,cy-Math.sin(r)*R*ri); ctx.lineTo(cx+Math.cos(r)*R*ro,cy-Math.sin(r)*R*ro); ctx.stroke(); }
    if(!reduce&&!document.hidden) requestAnimationFrame(frame); else if(!reduce) setTimeout(()=>requestAnimationFrame(frame),500);
  }
  requestAnimationFrame(frame);
};
