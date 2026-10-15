/**
 * EcoProtect Calculator Module (FR-16, Section 11, Section 16)
 * Interfaces with backend C++ scientific engine (eco_engine.exe)
 * providing real-time carbon and water footprint evaluations.
 */

document.addEventListener('DOMContentLoaded', () => {
    initCalculators();
});

function initCalculators() {
    // Mode Switchers
    const carbonTabBtn = document.getElementById('calc-tab-carbon');
    const waterTabBtn = document.getElementById('calc-tab-water');
    const carbonView = document.getElementById('calc-view-carbon');
    const waterView = document.getElementById('calc-view-water');

    if (carbonTabBtn && waterTabBtn) {
        carbonTabBtn.addEventListener('click', () => {
            carbonTabBtn.classList.add('active');
            waterTabBtn.classList.remove('active');
            carbonView.style.display = 'grid';
            waterView.style.display = 'none';
        });

        waterTabBtn.addEventListener('click', () => {
            waterTabBtn.classList.add('active');
            carbonTabBtn.classList.remove('active');
            waterView.style.display = 'grid';
            carbonView.style.display = 'none';
            computeWaterFootprint(); // Initial run
        });
    }

    // Sliders live value synchronization
    setupSliderSync('calc-elec', 'calc-elec-val', ' kWh/mo');
    setupSliderSync('calc-gas', 'calc-gas-val', ' therms/mo');
    setupSliderSync('calc-car', 'calc-car-val', ' km/wk');
    setupSliderSync('calc-transit', 'calc-transit-val', ' km/wk');
    setupSliderSync('calc-flights-short', 'calc-flights-short-val', ' flights/yr');
    setupSliderSync('calc-flights-long', 'calc-flights-long-val', ' flights/yr');
    setupSliderSync('calc-waste', 'calc-waste-val', ' bags/wk');
    setupSliderSync('calc-recycle', 'calc-recycle-val', '%');
    setupSliderSync('calc-members', 'calc-members-val', ' people');

    // Water Sliders
    setupSliderSync('water-shower', 'water-shower-val', ' mins/day');
    setupSliderSync('water-flushes', 'water-flushes-val', ' flushes/day');
    setupSliderSync('water-laundry', 'water-laundry-val', ' loads/wk');
    setupSliderSync('water-dish', 'water-dish-val', ' loads/wk');
    setupSliderSync('water-garden', 'water-garden-val', ' mins/wk');
    setupSliderSync('water-size', 'water-size-val', ' people');

    // Attach real-time calculation triggers (debounced)
    const carbonInputs = document.querySelectorAll('#calc-view-carbon input, #calc-view-carbon select');
    carbonInputs.forEach(el => el.addEventListener('input', debounce(computeCarbonFootprint, 350)));

    const waterInputs = document.querySelectorAll('#calc-view-water input, #calc-view-water select');
    waterInputs.forEach(el => el.addEventListener('input', debounce(computeWaterFootprint, 350)));

    // Run initial baseline calculation
    computeCarbonFootprint();
}

function setupSliderSync(sliderId, displayId, suffix) {
    const slider = document.getElementById(sliderId);
    const display = document.getElementById(displayId);
    if (!slider || !display) return;

    slider.addEventListener('input', () => {
        display.textContent = slider.value + suffix;
    });
}

function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

async function computeCarbonFootprint() {
    const payload = {
        type: 'carbon',
        electricity_kwh: parseFloat(document.getElementById('calc-elec')?.value || 250),
        gas_therms: parseFloat(document.getElementById('calc-gas')?.value || 20),
        car_km: parseFloat(document.getElementById('calc-car')?.value || 120),
        vehicle_type: document.getElementById('calc-vehicle-type')?.value || 'petrol',
        transit_km: parseFloat(document.getElementById('calc-transit')?.value || 40),
        flights_short: parseFloat(document.getElementById('calc-flights-short')?.value || 1),
        flights_long: parseFloat(document.getElementById('calc-flights-long')?.value || 0),
        diet_type: document.getElementById('calc-diet')?.value || 'average',
        waste_bags: parseFloat(document.getElementById('calc-waste')?.value || 2),
        recycling_rate: (parseFloat(document.getElementById('calc-recycle')?.value || 30)) / 100.0,
        household_members: parseInt(document.getElementById('calc-members')?.value || 1)
    };

    const res = await API.calculateImpact(payload);
    if (res && res.status === 'success') {
        renderCarbonResults(res);
    }
}

function renderCarbonResults(res) {
    const totalEl = document.getElementById('carbon-total-tonnes');
    const badgeEl = document.getElementById('carbon-score-badge');
    const treesEl = document.getElementById('carbon-trees-needed');
    const compGlobalEl = document.getElementById('carbon-comp-global');
    const compParisEl = document.getElementById('carbon-comp-paris');
    const engineEl = document.getElementById('carbon-engine-indicator');

    if (totalEl) totalEl.textContent = res.total_tonnes.toFixed(2);
    if (badgeEl) badgeEl.textContent = res.eco_rating;
    if (treesEl) treesEl.textContent = res.trees_needed;

    if (compGlobalEl) {
        const sign = res.global_comparison_pct >= 0 ? '+' : '';
        compGlobalEl.textContent = `${sign}${res.global_comparison_pct}% vs Global Avg (4.5t)`;
        compGlobalEl.style.color = res.global_comparison_pct > 0 ? '#ef4444' : '#10b981';
    }

    if (compParisEl) {
        const sign = res.paris_target_comparison_pct >= 0 ? '+' : '';
        compParisEl.textContent = `${sign}${res.paris_target_comparison_pct}% vs Paris Target (2.0t)`;
    }

    if (engineEl) engineEl.textContent = res.engine || 'C++17 Scientific Engine';

    // Breakdown Bars (Proportional to max component)
    const maxVal = Math.max(res.home_energy_kg, res.transport_kg, res.aviation_kg, res.diet_kg, res.waste_kg, 1);
    setBar('bar-energy', res.home_energy_kg, maxVal, `${res.home_energy_kg.toFixed(0)} kg`);
    setBar('bar-transport', res.transport_kg, maxVal, `${res.transport_kg.toFixed(0)} kg`);
    setBar('bar-aviation', res.aviation_kg, maxVal, `${res.aviation_kg.toFixed(0)} kg`);
    setBar('bar-diet', res.diet_kg, maxVal, `${res.diet_kg.toFixed(0)} kg`);
    setBar('bar-waste', res.waste_kg, maxVal, `${res.waste_kg.toFixed(0)} kg`);

    // Recommendations
    const recoList = document.getElementById('carbon-reco-list');
    if (recoList && res.recommendations) {
        recoList.innerHTML = res.recommendations
            .map(r => `<li style="margin-bottom: 0.4rem; font-size: 0.85rem; color: var(--text-secondary);">🌱 ${r}</li>`)
            .join('');
    }
}

async function computeWaterFootprint() {
    const payload = {
        type: 'water',
        shower_minutes: parseFloat(document.getElementById('water-shower')?.value || 8),
        toilet_flushes: parseFloat(document.getElementById('water-flushes')?.value || 5),
        laundry_loads: parseFloat(document.getElementById('water-laundry')?.value || 3),
        dish_loads: parseFloat(document.getElementById('water-dish')?.value || 5),
        garden_mins: parseFloat(document.getElementById('water-garden')?.value || 0),
        low_flow: document.getElementById('water-lowflow')?.checked || false,
        household_size: parseInt(document.getElementById('water-size')?.value || 1)
    };

    const res = await API.calculateImpact(payload);
    if (res && res.status === 'success') {
        renderWaterResults(res);
    }
}

function renderWaterResults(res) {
    const litersEl = document.getElementById('water-daily-liters');
    const tierEl = document.getElementById('water-tier-badge');
    const m3El = document.getElementById('water-annual-m3');
    const benchEl = document.getElementById('water-comp-bench');
    const engineEl = document.getElementById('water-engine-indicator');

    if (litersEl) litersEl.textContent = res.daily_liters_per_capita.toFixed(1);
    if (tierEl) tierEl.textContent = res.conservation_tier;
    if (m3El) m3El.textContent = res.annual_cubic_meters;

    if (benchEl) {
        const sign = res.global_benchmark_pct >= 0 ? '+' : '';
        benchEl.textContent = `${sign}${res.global_benchmark_pct}% vs Standard (140 L/day)`;
        benchEl.style.color = res.global_benchmark_pct > 0 ? '#ef4444' : '#10b981';
    }

    if (engineEl) engineEl.textContent = res.engine || 'C++17 Scientific Engine';

    const recoList = document.getElementById('water-reco-list');
    if (recoList && res.recommendations) {
        recoList.innerHTML = res.recommendations
            .map(r => `<li style="margin-bottom: 0.4rem; font-size: 0.85rem; color: var(--text-secondary);">💧 ${r}</li>`)
            .join('');
    }
}

function setBar(id, val, max, labelText) {
    const bar = document.getElementById(id);
    const label = document.getElementById(`${id}-val`);
    if (bar) {
        const pct = Math.min(100, Math.max(5, (val / max) * 100));
        bar.style.width = `${pct}%`;
    }
    if (label) {
        label.textContent = labelText;
    }
}
