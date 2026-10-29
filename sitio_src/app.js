// Aula del Futuro · comportamiento común a todas las páginas.
// Todo es mejora progresiva: sin JavaScript la web se lee y se navega igual.
(() => {
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => [...c.querySelectorAll(s)];
  const RAIZ = document.documentElement.dataset.raiz || '';

  /* ---------- Menú lateral en móvil (popover + scroll snap) ---------- */
  const drawer = $('#drawer');
  const abrir = $('#drawer-open');
  const movil = matchMedia('(max-width: 900px)');
  if (drawer && abrir && 'showPopover' in HTMLElement.prototype) {
    const scroller = $('.Drawer-scroller', drawer);
    const sheet = $('.Drawer-sheet', drawer);
    const main = $('main');
    const abierto = () => drawer.matches(':popover-open');
    async function openDrawer() {
      if (!movil.matches) return;
      drawer.showPopover();
      if (!CSS.supports('scroll-initial-target', 'nearest')) {
        scroller.scrollTo({ left: scroller.offsetWidth, behavior: 'instant' });
        await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
      }
      scroller.scrollTo({ left: 0, behavior: 'auto' });
    }
    function closeDrawer() {
      if (!abierto()) return;
      scroller.scrollTo({ left: scroller.offsetWidth, behavior: 'auto' });
    }
    function onOpened() { main.inert = true; abrir.setAttribute('aria-expanded', 'true'); sheet.focus(); }
    function onClosed() {
      if (abierto()) drawer.hidePopover();
      main.inert = false;
      abrir.setAttribute('aria-expanded', 'false');
    }
    const umbral = 1 / window.innerWidth;
    new IntersectionObserver(entries => {
      if (!movil.matches || !abierto()) return;
      const e = entries.at(-1);
      if (e.intersectionRatio < umbral) onClosed();
      if (e.intersectionRatio >= .99) onOpened();
    }, { root: drawer, threshold: [umbral, .99] }).observe(sheet);
    abrir.addEventListener('click', openDrawer);
    $('.cerrar-menu', drawer)?.addEventListener('click', closeDrawer);
    drawer.addEventListener('click', e => { if (movil.matches && !sheet.contains(e.target)) closeDrawer(); });
    document.addEventListener('keydown', e => { if (e.key === 'Escape') closeDrawer(); });
    if (!CSS.supports('animation-timeline: scroll()')) {
      scroller.addEventListener('scroll', () => {
        if (!movil.matches) return;
        drawer.style.setProperty('--drawer-backdrop', Math.max(0, 1 - scroller.scrollLeft / sheet.offsetWidth));
      });
    }
    movil.addEventListener('change', () => { if (!movil.matches && abierto()) { drawer.hidePopover(); onClosed(); } });
  }

  /* ---------- Archivos de Drive: vista previa bajo demanda ---------- */
  $$('figure.drive[data-id]').forEach(f => {
    const acciones = $('.acciones', f);
    const b = document.createElement('button');
    b.type = 'button'; b.className = 'boton'; b.textContent = 'Vista previa';
    b.setAttribute('aria-expanded', 'false');
    acciones.prepend(b);
    b.addEventListener('click', () => {
      const ya = $('iframe', f);
      if (ya) { ya.remove(); b.textContent = 'Vista previa'; b.setAttribute('aria-expanded', 'false'); return; }
      const fr = document.createElement('iframe');
      fr.src = `https://drive.google.com/file/d/${f.dataset.id}/preview`;
      fr.title = 'Vista previa: ' + (f.dataset.nombre || 'archivo de Drive');
      fr.loading = 'lazy'; fr.allow = 'autoplay; fullscreen';
      f.append(fr);
      b.textContent = 'Cerrar vista previa'; b.setAttribute('aria-expanded', 'true');
    });
  });

  /* ---------- Fotos: imágenes de Drive con alternativa y visor ---------- */
  document.addEventListener('error', e => {
    const img = e.target;
    if (img.tagName !== 'IMG') return;
    if (img.dataset.alt && img.src !== img.dataset.alt) { img.src = img.dataset.alt; return; }
    img.classList.add('rota');
  }, true);
  const visor = $('#visor');
  if (visor && typeof visor.showModal === 'function') {
    const vimg = $('img', visor);
    $$('.galeria button').forEach(b => b.addEventListener('click', () => {
      const img = $('img', b);
      vimg.src = img.currentSrc || img.src;
      vimg.alt = img.alt;
      visor.showModal();
    }));
    if (!('closedBy' in HTMLDialogElement.prototype)) {
      visor.addEventListener('click', e => {
        if (e.target !== visor) return;
        const r = visor.getBoundingClientRect();
        const dentro = r.top <= e.clientY && e.clientY <= r.top + r.height && r.left <= e.clientX && e.clientX <= r.left + r.width;
        if (!dentro) visor.close();
      });
    }
  }

  /* ---------- Filtro de situaciones de aprendizaje ---------- */
  const filtro = $('#filtro-sda');
  if (filtro) {
    const items = $$('#rejilla > li');
    const out = $('#filtro-n');
    const norm = s => s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
    const textos = items.map(li => norm(li.dataset.texto || li.textContent));
    filtro.addEventListener('input', () => {
      const q = norm(filtro.value.trim());
      let n = 0;
      items.forEach((li, i) => { const ok = !q || textos[i].includes(q); li.hidden = !ok; n += ok; });
      out.textContent = n === 1 ? '1 situación' : `${n} situaciones`;
    });
  }

  /* ---------- Buscador global (página buscar.html) ---------- */
  const caja = $('#resultados');
  if (caja) {
    const q = new URLSearchParams(location.search).get('q') || '';
    $$('form.buscador input[name=q]').forEach(i => { i.value = q; });
    const s = document.createElement('script');
    s.src = RAIZ + 'assets/indice.js';
    s.onload = () => pinta(q);
    document.head.append(s);
    function pinta(q) {
      const norm = s => s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
      const nq = norm(q.trim());
      const titulo = $('#titulo-busqueda');
      if (nq.length < 2) { titulo.textContent = 'Buscar en el sitio'; caja.innerHTML = '<li class="vacio-aviso">Escribe al menos dos letras en el buscador.</li>'; return; }
      const res = window.INDICE.filter(p => p.n.includes(nq) || p.x.includes(nq))
        .sort((a, b) => (b.n.includes(nq) - a.n.includes(nq)));
      titulo.textContent = `${res.length} resultado${res.length === 1 ? '' : 's'} para «${q}»`;
      document.title = `Buscar «${q}» · Aula del Futuro IES Valle del Jerte`;
      const esc = t => t.replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
      caja.innerHTML = res.slice(0, 150).map(p => {
        const i = p.x.indexOf(nq);
        let frag = '';
        if (i >= 0) {
          const a = Math.max(0, i - 80);
          frag = (a ? '…' : '') + esc(p.t.slice(a, i)) + '<mark>' + esc(p.t.slice(i, i + nq.length)) + '</mark>' + esc(p.t.slice(i + nq.length, i + nq.length + 130)) + '…';
        }
        return `<li class="resultado"><div class="donde">${esc(p.d)}</div><a href="${RAIZ + p.u}">${esc(p.ti)}</a>${frag ? `<p>${frag}</p>` : ''}</li>`;
      }).join('') || '<li class="vacio-aviso">No hay coincidencias. Prueba con otra palabra o con el apellido de un docente.</li>';
    }
  }
})();
