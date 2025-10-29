// main.js: simple UI helpers
document.addEventListener('DOMContentLoaded', () => {
  // loader
  const loader = document.getElementById('loader');
  setTimeout(()=> loader.classList.add('loaded'), 800);
  setTimeout(()=> loader && loader.style && (loader.style.display='none'), 1200);

  // mobile menu toggle
  const mm = document.querySelector('.mobile-menu');
  mm && mm.addEventListener('click', () => {
    const nav = document.querySelector('.nav');
    if(nav.style.display === 'flex') nav.style.display = '';
    else nav.style.display = 'flex';
  });

  // fade-in small animation for blog cards
  const cards = document.querySelectorAll('.blog-card, .product-card');
  cards.forEach((c,i) => {
    c.style.opacity = 0;
    c.style.transform = 'translateY(8px)';
    setTimeout(()=> {
      c.style.transition = 'opacity .45s ease, transform .45s ease';
      c.style.opacity = 1;
      c.style.transform = 'translateY(0)';
    }, 120 + i*80);
  });

  // click anywhere on desktop to create a quick small flame burst
  document.addEventListener('click', (e) => {
    if(window.innerWidth < 900) return;
    const burst = document.createElement('div');
    burst.style.position = 'fixed';
    burst.style.left = (e.clientX - 10) + 'px';
    burst.style.top = (e.clientY - 20) + 'px';
    burst.style.width = '28px'; burst.style.height='36px';
    burst.style.borderRadius='40%';
    burst.style.background='radial-gradient(circle at 40% 20%, rgba(255,200,120,1), rgba(255,150,60,.9))';
    burst.style.boxShadow='0 10px 26px rgba(255,170,80,0.18)';
    burst.style.pointerEvents='none';
    burst.style.opacity='1';
    burst.style.transform='scale(.6)';
    burst.style.transition='opacity .9s ease, transform .9s ease';
    document.body.appendChild(burst);
    setTimeout(()=>{ burst.style.opacity='0'; burst.style.transform='scale(1.6)'; }, 40);
    setTimeout(()=> burst.remove(), 1000);
  });
});
