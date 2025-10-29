// flame-cursor.js
(function(){
  const isMobile = /Android|iPhone|iPad|iPod|webOS/i.test(navigator.userAgent) || window.innerWidth < 900;

  if(!isMobile){
    // create flame element that follows cursor
    const flame = document.createElement('div');
    flame.id = 'cursor-flame';
    flame.style.position = 'fixed';
    flame.style.pointerEvents = 'none';
    flame.style.width = '22px';
    flame.style.height = '30px';
    flame.style.borderRadius = '50% 50% 45% 45% / 60% 60% 40% 40%';
    flame.style.background = 'radial-gradient(circle at 40% 20%, rgba(255,210,120,1), rgba(255,150,60,.9))';
    flame.style.boxShadow = '0 8px 22px rgba(255,180,80,.12)';
    flame.style.transform = 'translate(-50%, -50%)';
    flame.style.zIndex = 99999;
    flame.style.transition = 'transform .06s linear, opacity .3s ease';
    document.body.appendChild(flame);

    let lastX=0, lastY=0;
    document.addEventListener('mousemove', (e)=>{
      flame.style.left = e.clientX + 'px';
      flame.style.top = e.clientY + 'px';
      lastX = e.clientX; lastY = e.clientY;
    });

    document.addEventListener('mousedown', (e)=>{
      flame.style.transform = 'translate(-50%, -50%) scale(1.4)';
      flame.style.opacity = '0.9';
      setTimeout(()=> { flame.style.transform = 'translate(-50%,-50%) scale(1)'; flame.style.opacity = '1' }, 220);
    });

    document.addEventListener('mouseenter', ()=> flame.style.opacity = '1');
    document.addEventListener('mouseleave', ()=> flame.style.opacity = '0');
  } else {
    // leave floating flame visible (already in base template)
    // Add tap glow
    const ff = document.getElementById('floating-flame');
    document.addEventListener('touchstart', (e)=>{
      ff.style.transform = 'scale(1.2)';
      setTimeout(()=> ff.style.transform = '', 250);
    });
  }
})();
