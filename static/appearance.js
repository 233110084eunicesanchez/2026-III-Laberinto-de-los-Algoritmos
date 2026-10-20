/* Preferencia de movimiento local, sin modificar el tiempo del juego. */
(()=>{
 const media=matchMedia('(prefers-reduced-motion: reduce)');let preference;
 try{preference=localStorage.getItem('lab-motion');}catch{}
 const api=window.LabAppearance={reduced:preference==='reduce'||(!preference&&media.matches)};
 function update(){document.documentElement.classList.toggle('reduce-motion',api.reduced);const b=document.getElementById('motion-toggle');if(b){b.textContent='Animación: '+(api.reduced?'reducida':'completa');b.setAttribute('aria-pressed',String(api.reduced));}window.dispatchEvent(new CustomEvent('lab-motion',{detail:api.reduced}));}
 update();media.addEventListener('change',()=>{if(!preference){api.reduced=media.matches;update();}});
 const b=document.getElementById('motion-toggle');if(b)b.onclick=()=>{api.reduced=!api.reduced;preference=api.reduced?'reduce':'full';try{localStorage.setItem('lab-motion',preference);}catch{}update();};
 document.querySelectorAll('[data-celebrate]').forEach(n=>{if(!api.reduced)window.LabCelebration?.play(n,n.dataset.celebrate);if(n.dataset.celebrate==='omega')document.body.classList.add('is-restored');});
})();
