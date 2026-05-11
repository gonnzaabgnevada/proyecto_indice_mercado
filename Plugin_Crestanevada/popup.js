// =============================================
// MOTOR INTEL — Popup
// =============================================

document.addEventListener('DOMContentLoaded', () => {
  const contenedor = document.getElementById('contenedor');
  const searchInput = document.getElementById('search-input');
  const filterFuel = document.getElementById('filter-fuel');
  const statTotal = document.getElementById('stat-total');
  const statMedio = document.getElementById('stat-medio');
  const statHibrido = document.getElementById('stat-hibrido');

  let allCars = [];

  function renderCars(cars) {
    if (cars.length === 0) {
      contenedor.innerHTML = `
        <div class="empty-state">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          <p>Sin resultados</p>
        </div>`;
      return;
    }

    contenedor.innerHTML = '';
    cars.forEach(car => {
      const div = document.createElement('div');
      div.className = 'car-item';
      const fuelColor = {
        'Diésel': '#6B7280', 'Gasolina': '#F59E0B', 'Híbrido': '#10B981',
        'Híbrido enchufable': '#06B6D4', 'Eléctrico': '#8B5CF6',
      }[car.fuel] || '#94A3B8';

      div.innerHTML = `
        <div class="car-header">
          <div class="car-name">${car.brand} ${car.model}</div>
          <div class="car-portal">${car.portal}</div>
        </div>
        <div class="car-meta">
          <span class="car-year">${car.year}</span>
          <span class="car-km">${parseInt(car.km).toLocaleString('es-ES')} km</span>
          <span class="car-fuel" style="color:${fuelColor}">${car.fuel}</span>
        </div>
        <div class="car-price">${parseInt(car.price).toLocaleString('es-ES')} €</div>
      `;
      contenedor.appendChild(div);
    });
  }

  function applyFilters() {
    const query = searchInput.value.toLowerCase();
    const fuel = filterFuel.value;
    const filtered = allCars.filter(c => {
      const matchSearch = !query ||
        `${c.brand} ${c.model} ${c.version}`.toLowerCase().includes(query);
      const matchFuel = !fuel || c.fuel === fuel;
      return matchSearch && matchFuel;
    });
    renderCars(filtered);
  }

  searchInput.addEventListener('input', applyFilters);
  filterFuel.addEventListener('change', applyFilters);

  fetch('http://localhost:5000/get_coches')
    .then(r => r.json())
    .then(data => {
      allCars = data;

      statTotal.textContent = data.length.toLocaleString('es-ES');

      const prices = data.map(c => parseInt(c.price)).filter(Boolean);
      if (prices.length) {
        const avg = Math.round(prices.reduce((s, v) => s + v, 0) / prices.length);
        statMedio.textContent = avg.toLocaleString('es-ES') + ' €';
      }

      const electricos = data.filter(c =>
        c.fuel === 'Eléctrico' || c.fuel?.includes('Híbrido')
      ).length;
      const pct = prices.length ? Math.round((electricos / data.length) * 100) : 0;
      statHibrido.textContent = pct + '%';

      // Populate fuel filter
      const fuels = [...new Set(data.map(c => c.fuel).filter(Boolean))];
      fuels.forEach(f => {
        const opt = document.createElement('option');
        opt.value = f;
        opt.textContent = f;
        filterFuel.appendChild(opt);
      });

      renderCars(data);
    })
    .catch(() => {
      contenedor.innerHTML = `
        <div class="error-state">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
            <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
          </svg>
          <p>¿Está encendido <code>app.py</code>?</p>
        </div>`;
    });
});