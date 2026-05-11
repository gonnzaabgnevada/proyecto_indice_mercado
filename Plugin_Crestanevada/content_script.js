// =============================================
// MOTOR INTEL — Content Script
// =============================================

const BRAND_COLORS = {
  'BMW': '#1C69D3', 'MERCEDES-BENZ': '#00ADEF', 'AUDI': '#BB0A14',
  'VOLKSWAGEN': '#001E50', 'SEAT': '#FA0230', 'TOYOTA': '#EB0A1E',
  'FORD': '#003478', 'PEUGEOT': '#003189', 'CITROEN': '#D31920',
  'KIA': '#05141F', 'HYUNDAI': '#002C5F', 'RENAULT': '#FFCC00',
};

const FUEL_ICONS = {
  'Diésel': '⛽', 'Gasolina': '⛽', 'Híbrido': '🔋', 'Híbrido enchufable': '🔌',
  'Eléctrico': '⚡', 'Gas licuado (GLP)': '🔵', 'Gas natural (CNG)': '🟢',
};

const FUEL_COLORS = {
  'Diésel': '#6B7280',
  'Gasolina': '#F59E0B',
  'Híbrido': '#10B981',
  'Híbrido enchufable': '#06B6D4',
  'Eléctrico': '#8B5CF6',
  'Gas licuado (GLP)': '#3B82F6',
  'Gas natural (CNG)': '#22C55E',
};

// =============================================
// 1. SIDEBAR CREATION
// =============================================
const sidebar = document.createElement('div');
sidebar.id = 'motorintel-sidebar';
sidebar.innerHTML = `
  <div class="mi-sidebar-inner">
    <div class="mi-header">
      <div class="mi-header-brand">
        <div class="mi-logo-mark">M</div>
        <div>
          <div class="mi-logo-title">Motor Intel</div>
          <div class="mi-logo-sub">Análisis de mercado</div>
        </div>
      </div>
      <button id="mi-close-btn" aria-label="Cerrar panel">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
          <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
        </svg>
      </button>
    </div>
    <div class="mi-body" id="mi-body">
      <div class="mi-empty-state">
        <div class="mi-empty-icon">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
        </div>
        <p class="mi-empty-title">Sin análisis activo</p>
        <p class="mi-empty-desc">Haz clic en «Analizar» bajo cualquier anuncio para ver los datos de mercado.</p>
      </div>
    </div>
  </div>
`;
document.body.appendChild(sidebar);

document.getElementById('mi-close-btn').addEventListener('click', () => {
  sidebar.classList.remove('open');
});

// =============================================
// 2. RENDER ANALYTICS VIEW
// =============================================
function calcPercentile(arr, p) {
  const sorted = [...arr].sort((a, b) => a - b);
  const idx = Math.ceil((p / 100) * sorted.length) - 1;
  return sorted[Math.max(0, idx)];
}

function valoracionPrecio(price, p25, p50, p75) {
  if (price <= p25) return { label: 'Muy buen precio', color: '#10B981', icon: '🟢', stars: 5 };
  if (price <= p50) return { label: 'Buen precio', color: '#22C55E', icon: '🟩', stars: 4 };
  if (price <= p75) return { label: 'Precio de mercado', color: '#F59E0B', icon: '🟡', stars: 3 };
  return { label: 'Por encima del mercado', color: '#EF4444', icon: '🔴', stars: 2 };
}

function renderAnalysis(datos, anuncioCoche) {
  const body = document.getElementById('mi-body');

  // Filtrar puntos válidos (necesitan precio, km y url)
  const puntos = datos
    .map(r => ({
      price: parseInt(r.price),
      km:    parseInt(r.km),
      fuel:  r.fuel || '',
      year:  r.year || '',
      version: r.version || (r.brand + ' ' + r.model),
      portal:  r.portal || '',
      url:     r.url || '',
    }))
    .filter(r => r.price > 0 && r.km >= 0);

  const precios = puntos.map(r => r.price).sort((a, b) => a - b);
  const kms     = puntos.map(r => r.km).sort((a, b) => a - b);

  const p25 = calcPercentile(precios, 25);
  const p50 = calcPercentile(precios, 50);
  const p75 = calcPercentile(precios, 75);
  const precioMin  = precios[0];
  const precioMax  = precios[precios.length - 1];
  const precioMedio = Math.round(precios.reduce((s, v) => s + v, 0) / precios.length);
  const kmMedio     = kms.length ? Math.round(kms.reduce((s, v) => s + v, 0) / kms.length) : null;
  const precioSugerido = Math.round(p50 * 0.88);

  // Combustibles
  const fuelCount = {};
  datos.forEach(r => { if (r.fuel) fuelCount[r.fuel] = (fuelCount[r.fuel] || 0) + 1; });
  const topFuel = Object.entries(fuelCount).sort((a, b) => b[1] - a[1]);

  // Portales
  const portalCount = {};
  datos.forEach(r => { if (r.portal) portalCount[r.portal] = (portalCount[r.portal] || 0) + 1; });
  const portalPills = Object.entries(portalCount).map(([portal, n]) =>
    `<span class="mi-pill">${portal} <b>${n}</b></span>`
  ).join('');

  // Valoración del anuncio activo
  const precioAnuncio = anuncioCoche.precio ? parseInt(anuncioCoche.precio) : null;
  const valoracion    = precioAnuncio ? valoracionPrecio(precioAnuncio, p25, p50, p75) : null;
  const stars         = valoracion ? '★'.repeat(valoracion.stars) + '☆'.repeat(5 - valoracion.stars) : '';

  body.innerHTML = `
    <div class="mi-section mi-car-header">
      <div class="mi-car-title">${anuncioCoche.titulo}</div>
      <div class="mi-car-meta">${anuncioCoche.año ? `Año ${anuncioCoche.año}` : ''} · <b>${puntos.length}</b> coches en base de datos</div>
    </div>

    ${valoracion && precioAnuncio ? `
    <div class="mi-section mi-valoracion" style="border-left: 3px solid ${valoracion.color}">
      <div class="mi-valoracion-stars" style="color:${valoracion.color}">${stars}</div>
      <div class="mi-valoracion-label" style="color:${valoracion.color}">${valoracion.label}</div>
      <div class="mi-valoracion-precio">${precioAnuncio.toLocaleString('es-ES')} €</div>
      <div class="mi-valoracion-vs">vs. mediana de mercado ${p50.toLocaleString('es-ES')} €</div>
    </div>
    ` : ''}

    <div class="mi-section">
      <div class="mi-section-title">Precio vs Kilómetros</div>
      <div class="mi-scatter-legend">
        <span class="mi-scatter-dot mi-scatter-dot--normal"></span> Mercado
        <span class="mi-scatter-dot mi-scatter-dot--active"></span> Este anuncio
        <span style="margin-left:auto; font-size:10px; color:#94A3B8">Clic en punto → anuncio</span>
      </div>
      <div class="mi-scatter-wrap">
        <canvas id="mi-scatter-canvas"></canvas>
        <div id="mi-tooltip" class="mi-scatter-tooltip"></div>
      </div>
      <div class="mi-scatter-axis-labels">
        <span>← más km</span>
        <span>Precio →</span>
      </div>
    </div>

    <div class="mi-section">
      <div class="mi-section-title">Estadísticas de mercado</div>
      <div class="mi-stats-grid">
        <div class="mi-stat">
          <div class="mi-stat-label">Mediana</div>
          <div class="mi-stat-value">${p50.toLocaleString('es-ES')} €</div>
        </div>
        <div class="mi-stat">
          <div class="mi-stat-label">Media</div>
          <div class="mi-stat-value">${precioMedio.toLocaleString('es-ES')} €</div>
        </div>
        <div class="mi-stat">
          <div class="mi-stat-label">P25 (buen precio)</div>
          <div class="mi-stat-value mi-stat-value--green">${p25.toLocaleString('es-ES')} €</div>
        </div>
        <div class="mi-stat">
          <div class="mi-stat-label">P75 (caro)</div>
          <div class="mi-stat-value mi-stat-value--red">${p75.toLocaleString('es-ES')} €</div>
        </div>
        ${kmMedio ? `
        <div class="mi-stat mi-stat--wide">
          <div class="mi-stat-label">Km medio de mercado</div>
          <div class="mi-stat-value">${kmMedio.toLocaleString('es-ES')} km</div>
        </div>` : ''}
      </div>
    </div>

    <div class="mi-section mi-oferta-section">
      <div class="mi-section-title">Oferta de compra sugerida</div>
      <div class="mi-oferta-price">${precioSugerido.toLocaleString('es-ES')} €</div>
      <div class="mi-oferta-desc">Basado en la mediana del mercado con un margen de negociación del 12%</div>
    </div>

    ${topFuel.length ? `
    <div class="mi-section">
      <div class="mi-section-title">Combustibles más frecuentes</div>
      <div class="mi-fuel-list">
        ${topFuel.slice(0, 4).map(([fuel, n]) => {
          const pct = Math.round((n / datos.length) * 100);
          const color = FUEL_COLORS[fuel] || '#6B7280';
          const icon = FUEL_ICONS[fuel] || '⛽';
          return `
          <div class="mi-fuel-item">
            <div class="mi-fuel-label">${icon} ${fuel}</div>
            <div class="mi-fuel-bar-wrap">
              <div class="mi-fuel-bar" style="width:${pct}%; background:${color}"></div>
            </div>
            <div class="mi-fuel-pct">${pct}%</div>
          </div>`;
        }).join('')}
      </div>
    </div>` : ''}

    ${Object.keys(portalCount).length > 1 ? `
    <div class="mi-section">
      <div class="mi-section-title">Fuentes de datos</div>
      <div class="mi-pills">${portalPills}</div>
    </div>` : ''}
  `;

  // Inicializar scatter plot una vez el HTML está en el DOM
  requestAnimationFrame(() => initScatter(puntos, precioAnuncio, anuncioCoche));
}

// =============================================
// SCATTER PLOT — Canvas 2D
// =============================================
function initScatter(puntos, precioAnuncio, anuncioCoche) {
  const wrap   = document.querySelector('.mi-scatter-wrap');
  const canvas = document.getElementById('mi-scatter-canvas');
  const tooltip = document.getElementById('mi-tooltip');
  if (!canvas || !wrap) return;

  // Tamaño real del canvas = tamaño del contenedor
  const W = wrap.clientWidth  || 370;
  const H = 220;
  canvas.width  = W;
  canvas.height = H;
  canvas.style.width  = W + 'px';
  canvas.style.height = H + 'px';

  const PAD = { top: 10, right: 14, bottom: 28, left: 52 };
  const plotW = W - PAD.left - PAD.right;
  const plotH = H - PAD.top  - PAD.bottom;

  // Rangos — con margen 5% para que los puntos no toquen el borde
  const prices = puntos.map(p => p.price);
  const kms    = puntos.map(p => p.km);
  const minP = Math.min(...prices), maxP = Math.max(...prices);
  const minK = Math.min(...kms),    maxK = Math.max(...kms);
  const padP = (maxP - minP) * 0.05 || 1000;
  const padK = (maxK - minK) * 0.05 || 5000;
  const domainPriceMin = minP - padP, domainPriceMax = maxP + padP;
  const domainKmMin    = minK - padK, domainKmMax    = maxK + padK;

  // Funciones de escala
  const scaleX = price => PAD.left + ((price - domainPriceMin) / (domainPriceMax - domainPriceMin)) * plotW;
  const scaleY = km    => PAD.top  + (1 - (km - domainKmMin) / (domainKmMax - domainKmMin)) * plotH;

  // Para hit-testing guardamos posición de cada punto
  const puntosPos = puntos.map(p => ({
    ...p,
    cx: scaleX(p.price),
    cy: scaleY(p.km),
  }));

  const ctx = canvas.getContext('2d');

  function draw(hoveredIdx) {
    ctx.clearRect(0, 0, W, H);

    // Grid lines
    ctx.strokeStyle = '#E2E8F0';
    ctx.lineWidth = 0.5;
    const nGridX = 4, nGridY = 4;
    for (let i = 0; i <= nGridX; i++) {
      const x = PAD.left + (i / nGridX) * plotW;
      ctx.beginPath(); ctx.moveTo(x, PAD.top); ctx.lineTo(x, PAD.top + plotH); ctx.stroke();
    }
    for (let i = 0; i <= nGridY; i++) {
      const y = PAD.top + (i / nGridY) * plotH;
      ctx.beginPath(); ctx.moveTo(PAD.left, y); ctx.lineTo(PAD.left + plotW, y); ctx.stroke();
    }

    // Axis labels — X (precio) bottom
    ctx.fillStyle = '#94A3B8';
    ctx.font = '9px -apple-system, system-ui, sans-serif';
    ctx.textAlign = 'center';
    for (let i = 0; i <= nGridX; i++) {
      const val = domainPriceMin + (i / nGridX) * (domainPriceMax - domainPriceMin);
      const x   = PAD.left + (i / nGridX) * plotW;
      ctx.fillText(Math.round(val / 1000) + 'k€', x, H - 6);
    }

    // Axis labels — Y (km) left
    ctx.textAlign = 'right';
    for (let i = 0; i <= nGridY; i++) {
      const val = domainKmMax - (i / nGridY) * (domainKmMax - domainKmMin);
      const y   = PAD.top + (i / nGridY) * plotH;
      const label = val >= 1000 ? Math.round(val / 1000) + 'k' : Math.round(val);
      ctx.fillText(label, PAD.left - 5, y + 3);
    }

    // Puntos
    puntosPos.forEach((p, i) => {
      const isHovered = i === hoveredIdx;
      const isAnuncio = precioAnuncio && Math.abs(p.price - precioAnuncio) < 200;
      const fuelColor = FUEL_COLORS[p.fuel] || '#94A3B8';

      ctx.beginPath();
      ctx.arc(p.cx, p.cy, isHovered ? 7 : (isAnuncio ? 7 : 4), 0, Math.PI * 2);

      if (isAnuncio) {
        ctx.fillStyle = '#EF4444';
        ctx.strokeStyle = '#fff';
        ctx.lineWidth = 2;
        ctx.fill();
        ctx.stroke();
      } else {
        ctx.fillStyle = isHovered ? fuelColor : fuelColor + 'BB';
        ctx.strokeStyle = isHovered ? '#fff' : 'transparent';
        ctx.lineWidth = isHovered ? 1.5 : 0;
        ctx.fill();
        if (isHovered) ctx.stroke();
      }
    });
  }

  draw(-1);

  // Hit testing — mouse move
  canvas.addEventListener('mousemove', (e) => {
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;

    let found = -1;
    let minDist = 10; // px threshold
    puntosPos.forEach((p, i) => {
      const d = Math.hypot(p.cx - mx, p.cy - my);
      if (d < minDist) { minDist = d; found = i; }
    });

    draw(found);

    if (found >= 0) {
      const p = puntosPos[found];
      canvas.style.cursor = p.url ? 'pointer' : 'default';

      const fuelIcon = FUEL_ICONS[p.fuel] || '⛽';
      tooltip.innerHTML = `
        <div class="mi-tt-version">${p.version}</div>
        <div class="mi-tt-row">
          <span class="mi-tt-price">${p.price.toLocaleString('es-ES')} €</span>
          <span class="mi-tt-km">${p.km.toLocaleString('es-ES')} km</span>
        </div>
        <div class="mi-tt-meta">${fuelIcon} ${p.fuel} · ${p.year} · ${p.portal}</div>
        ${p.url ? '<div class="mi-tt-link">↗ Ver anuncio</div>' : ''}
      `;

      // Posición del tooltip — evitar que se salga
      const ttW = 220, ttH = 90;
      let tx = p.cx + 12;
      let ty = p.cy - ttH / 2;
      if (tx + ttW > W) tx = p.cx - ttW - 12;
      if (ty < PAD.top) ty = PAD.top;
      if (ty + ttH > H - PAD.bottom) ty = H - PAD.bottom - ttH;

      tooltip.style.left    = tx + 'px';
      tooltip.style.top     = ty + 'px';
      tooltip.style.opacity = '1';
    } else {
      canvas.style.cursor   = 'default';
      tooltip.style.opacity = '0';
    }
  });

  canvas.addEventListener('mouseleave', () => {
    tooltip.style.opacity = '0';
    draw(-1);
  });

  // Click — abrir URL
  canvas.addEventListener('click', (e) => {
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;

    let found = -1, minDist = 10;
    puntosPos.forEach((p, i) => {
      const d = Math.hypot(p.cx - mx, p.cy - my);
      if (d < minDist) { minDist = d; found = i; }
    });

    if (found >= 0 && puntosPos[found].url) {
      window.open(puntosPos[found].url, '_blank', 'noopener');
    }
  });
}

// =============================================
// 3. API CALL
// =============================================
async function fetchDatos(titulo, year) {
  try {
    const resp = await fetch(
      `http://127.0.0.1:5000/get_coches?full_title=${encodeURIComponent(titulo)}&year=${year}`
    );
    return await resp.json();
  } catch (e) {
    console.error('[MotorIntel] Error conectando con app.py', e);
    return null;
  }
}

// =============================================
// 4. BADGE INJECTION
// =============================================
function inyectarBadges() {
  const tarjetas = document.querySelectorAll('.mt-ListAds-item');
  tarjetas.forEach((tarjeta) => {
    if (tarjeta.querySelector('.mi-badge')) return;

    const linkTitulo = tarjeta.querySelector('.mt-CardAd-infoTitleLink') ||
      tarjeta.querySelector('h2[data-testid="card-ad-title"] a');
    const titulo = linkTitulo ? linkTitulo.innerText.trim() : '';
    if (!titulo || titulo.includes('Coches nuevos')) return;

    let año = '';
    tarjeta.querySelectorAll('.mt-CardAd-attrItem').forEach(item => {
      if (/^(19|20)\d{2}$/.test(item.innerText.trim())) año = item.innerText.trim();
    });

    let precio = '';
    const precioEl = tarjeta.querySelector('.mt-CardAdPrice-cash, [class*="price"], .mt-CardAdPrice');
    if (precioEl) {
      const match = precioEl.innerText.replace(/\./g, '').match(/(\d+)/);
      if (match) precio = match[1];
    }

    const badge = document.createElement('button');
    badge.className = 'mi-badge';
    badge.innerHTML = `
      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true">
        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
      </svg>
      Analizar${año ? ' · ' + año : ''}
    `;

    badge.addEventListener('click', async (e) => {
      e.stopPropagation();
      e.preventDefault();
      sidebar.classList.add('open');

      document.getElementById('mi-body').innerHTML = `
        <div class="mi-loading">
          <div class="mi-spinner"></div>
          <div class="mi-loading-text">Consultando base de datos…</div>
          <div class="mi-loading-sub">${titulo}</div>
        </div>
      `;

      const datos = await fetchDatos(titulo, año);

      if (datos && datos.length > 0) {
        renderAnalysis(datos, { titulo, año, precio });
      } else {
        document.getElementById('mi-body').innerHTML = `
          <div class="mi-error">
            <div class="mi-error-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
            </div>
            <p class="mi-error-title">Sin resultados</p>
            <p class="mi-error-desc">No hay coincidencias en la base de datos para <b>${titulo}</b>${año ? ' del año ' + año : ''}.</p>
          </div>
        `;
      }
    });

    const zonaPrecio = tarjeta.querySelector('.mt-CardAdPrice');
    if (zonaPrecio) zonaPrecio.insertAdjacentElement('afterend', badge);
  });
}

setInterval(inyectarBadges, 1200);