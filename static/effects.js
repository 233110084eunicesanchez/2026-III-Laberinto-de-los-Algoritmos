/* Celebraciones de duración limitada: confeti, fuegos de luz y red segura. */
(()=>{
 const live=new Set();
 function play(host,world){
  if(window.LabAppearance?.reduced||matchMedia('(prefers-reduced-motion: reduce)').matches||host.querySelector('.celebration-canvas'))return;
  const canvas=document.createElement('canvas');canvas.className='celebration-canvas';canvas.setAttribute('aria-hidden','true');host.append(canvas);
  const ctx=canvas.getContext('2d');if(!ctx){canvas.remove();return;}
  const w=host.clientWidth,h=host.clientHeight,dpr=Math.min(devicePixelRatio||1,2);canvas.width=w*dpr;canvas.height=h*dpr;ctx.scale(dpr,dpr);
  const rand=(a,b)=>a+Math.random()*(b-a);let frame,deadline;
  const stop=()=>{cancelAnimationFrame(frame);clearTimeout(deadline);canvas.remove();live.delete(stop);};live.add(stop);
  const confetti=Array.from({length:80},()=>({x:rand(0,w),y:rand(-h,0),speed:rand(65,150),drift:rand(-20,20),rotation:rand(0,6),color:['#16be7a','#ffe07c','#fff','#a7efc5'][Math.floor(rand(0,4))]}));
  const bursts=Array.from({length:5},(_,i)=>({x:w*(.12+i*.19),y:h*rand(.12,.43),delay:i*.65,particles:Array.from({length:30},()=>({angle:rand(0,Math.PI*2),speed:rand(35,110),color:Math.random()>.4?'#ffda57':'#75eafa'}))}));
  const nodes=Array.from({length:24},(_,i)=>({x:w*((i%6+.5)/6),y:h*((Math.floor(i/6)+.5)/4)}));
  const start=performance.now();
  function draw(now){
   const t=Math.max(0,(now-start)/1000);if(t>5.4||!canvas.isConnected||window.LabAppearance?.reduced){stop();return;}
   ctx.clearRect(0,0,w,h);ctx.globalAlpha=Math.min(1,(5.4-t)/1.2);
   if(world==='alfa'){
    confetti.forEach(p=>{const y=p.y+t*p.speed;if(y>h+30)return;ctx.save();ctx.translate(p.x+Math.sin(t*2+p.rotation)*18+p.drift*t,y);ctx.rotate(p.rotation+t*2);ctx.fillStyle=p.color;ctx.fillRect(-4,-7,8,14);ctx.restore();});
   }else if(world==='beta'){
    bursts.forEach(b=>{const age=t-b.delay;if(age<0||age>2)return;ctx.save();ctx.globalAlpha*=Math.max(0,1-age/2);b.particles.forEach(p=>{const x=b.x+Math.cos(p.angle)*p.speed*age,y=b.y+Math.sin(p.angle)*p.speed*age+18*age*age;ctx.strokeStyle=p.color;ctx.lineWidth=2;ctx.shadowColor=p.color;ctx.shadowBlur=8;ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(x-Math.cos(p.angle)*9,y-Math.sin(p.angle)*9);ctx.stroke();});ctx.restore();});
   }else{
    ctx.save();ctx.strokeStyle='#47ddff';ctx.fillStyle='#b3fbff';ctx.shadowColor='#21bfff';ctx.shadowBlur=12;
    const activation=Math.min(nodes.length,Math.floor(t*10));nodes.forEach((n,i)=>{if(i>=activation)return;ctx.globalAlpha=Math.min(1,(5.4-t)/1.2)*.55;[i+1,i+6].forEach(j=>{if(j>=activation||j>=nodes.length||(j===i+1&&i%6===5))return;ctx.lineWidth=1.7;ctx.beginPath();ctx.moveTo(n.x,n.y);ctx.lineTo(nodes[j].x,nodes[j].y);ctx.stroke();});ctx.globalAlpha=Math.min(1,(5.4-t)/1.2);ctx.beginPath();ctx.arc(n.x,n.y,4,0,Math.PI*2);ctx.fill();});
    ctx.globalAlpha*=.45;ctx.lineWidth=4;ctx.beginPath();ctx.arc(w/2,h/2,t*Math.max(w,h)/3,0,Math.PI*2);ctx.stroke();ctx.restore();
   }
   frame=requestAnimationFrame(draw);
  }
  deadline=setTimeout(stop,5600);
  frame=requestAnimationFrame(draw);
 }
 window.LabCelebration={play};window.addEventListener('lab-motion',e=>{if(e.detail)for(const stop of [...live])stop();});
})();
