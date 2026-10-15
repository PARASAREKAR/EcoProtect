/**
 * EcoProtect - Main Frontend Application Logic
 * Implements navigation, dark-mode toggle, statistics animation,
 * interactive tabs, search indexing, event registration modal,
 * pledge submission & certificate generation, and feedback form.
 */

document.addEventListener('DOMContentLoaded', () => {
    initThemeToggle();
    initMobileNav();
    initScrollSpy();
    initStatsCounter();
    initTabs();
    initSearch();
    initDailyTips();
    initPledgeSystem();
    initEventsModule();
    initFeedbackForm();
    initNewsletterForms();
    initGreenhouseSimulator();
});

// --- 1. Dark Mode System (FR-21) ---
function initThemeToggle() {
    const themeBtn = document.getElementById('theme-toggle-btn');
    const themeIcon = document.getElementById('theme-icon');
    const savedTheme = localStorage.getItem('ecoprotect_theme');
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;

    if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
        document.body.classList.add('dark-mode');
        if (themeIcon) themeIcon.textContent = '☀️';
    } else {
        document.body.classList.remove('dark-mode');
        if (themeIcon) themeIcon.textContent = '🌙';
    }

    if (themeBtn) {
        themeBtn.addEventListener('click', () => {
            const isDark = document.body.classList.toggle('dark-mode');
            localStorage.setItem('ecoprotect_theme', isDark ? 'dark' : 'light');
            if (themeIcon) themeIcon.textContent = isDark ? '☀️' : '🌙';
            showToast(isDark ? 'Dark mode enabled 🌙' : 'Light mode enabled ☀️', 'info');
        });
    }
}

// --- 2. Mobile Navigation & Sticky Header ---
function initMobileNav() {
    const hamburger = document.getElementById('hamburger-btn');
    const navMenu = document.getElementById('nav-menu');

    if (hamburger && navMenu) {
        hamburger.addEventListener('click', () => {
            navMenu.classList.toggle('mobile-open');
        });

        // Close on link click
        navMenu.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                navMenu.classList.remove('mobile-open');
            });
        });
    }
}

// --- 3. ScrollSpy & Smooth Header Transitions ---
function initScrollSpy() {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-menu .nav-link');
    const header = document.querySelector('.site-header');

    window.addEventListener('scroll', () => {
        const scrollY = window.pageYOffset;

        if (header) {
            if (scrollY > 50) {
                header.classList.add('header-scrolled');
            } else {
                header.classList.remove('header-scrolled');
            }
        }

        sections.forEach(current => {
            const sectionHeight = current.offsetHeight;
            const sectionTop = current.offsetTop - 120;
            const sectionId = current.getAttribute('id');

            if (scrollY > sectionTop && scrollY <= sectionTop + sectionHeight) {
                navLinks.forEach(link => {
                    link.classList.remove('active');
                    if (link.getAttribute('href') === `#${sectionId}`) {
                        link.classList.add('active');
                    }
                });
            }
        });
    });
}

// --- 4. Live Statistics Counter Animation (FR-01, FR-29) ---
function initStatsCounter() {
    const statCards = document.querySelectorAll('.stat-value[data-target]');
    let started = false;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !started) {
                statCards.forEach(counter => {
                    const target = parseFloat(counter.getAttribute('data-target'));
                    const isDecimal = target % 1 !== 0;
                    const duration = 2000;
                    const stepTime = 30;
                    const steps = duration / stepTime;
                    const increment = target / steps;
                    let current = 0;

                    const timer = setInterval(() => {
                        current += increment;
                        if (current >= target) {
                            counter.textContent = isDecimal ? target.toFixed(1) : Math.round(target).toLocaleString();
                            clearInterval(timer);
                        } else {
                            counter.textContent = isDecimal ? current.toFixed(1) : Math.round(current).toLocaleString();
                        }
                    }, stepTime);
                });
                started = true;
            }
        });
    }, { threshold: 0.2 });

    const statsBanner = document.querySelector('.stats-banner');
    if (statsBanner) observer.observe(statsBanner);
}

// --- 5. Interactive Tab Switchers (FR-07, FR-12, FR-13) ---
function initTabs() {
    const tabGroups = document.querySelectorAll('.tab-container');

    tabGroups.forEach(group => {
        const buttons = group.querySelectorAll('.tab-btn');
        const panes = group.querySelectorAll('.tab-pane');

        buttons.forEach(btn => {
            btn.addEventListener('click', () => {
                const targetId = btn.getAttribute('data-tab');

                buttons.forEach(b => b.classList.remove('active'));
                panes.forEach(p => p.classList.remove('active'));

                btn.classList.add('active');
                const targetPane = group.querySelector(`#${targetId}`);
                if (targetPane) targetPane.classList.add('active');
            });
        });
    });
}

// --- 6. Live Search Modal (FR-20) ---
function initSearch() {
    const searchOpenBtn = document.getElementById('search-open-btn');
    const searchModal = document.getElementById('search-modal');
    const searchCloseBtn = document.getElementById('search-close-btn');
    const searchInput = document.getElementById('search-input-field');
    const searchResultsList = document.getElementById('search-results-list');

    if (!searchModal) return;

    // Search Index
    const searchIndex = [
        { title: 'Air Pollution', section: 'problems', desc: 'Smog, PM2.5, respiratory risks, carbon emissions, clean air solutions.' },
        { title: 'Water Pollution', section: 'problems', desc: 'Industrial effluents, ocean plastics, eutrophication, freshwater safety.' },
        { title: 'Soil Contamination', section: 'problems', desc: 'Pesticides, heavy metals, soil biodiversity, regenerative agriculture.' },
        { title: 'Noise Pollution', section: 'problems', desc: 'Urban acoustics, hearing health, wildlife disruption, acoustic buffers.' },
        { title: 'Plastic Crisis & Microplastics', section: 'problems', desc: 'Single-use plastics, ocean gyres, circular bio-polymers, recycling.' },
        { title: 'Climate Change & Global Warming', section: 'climate', desc: 'Greenhouse effect, rising temperatures, Arctic ice loss, Paris climate targets.' },
        { title: 'Biodiversity & Wildlife Sanctuary', section: 'biodiversity', desc: 'Endangered species, IUCN Red List, habitat loss, wildlife corridors.' },
        { title: 'Forest Conservation & Afforestation', section: 'forests', desc: 'Deforestation causes, carbon sinks, community tree planting, indigenous stewards.' },
        { title: 'Water Conservation & Rainwater Harvesting', section: 'water', desc: 'Aquifer recharge, household conservation, greywater reuse, drip irrigation.' },
        { title: 'Waste Management (The 5 R’s)', section: 'waste', desc: 'Reduce, Reuse, Recycle, Recover, Responsible Disposal, waste segregation.' },
        { title: 'Renewable Clean Energy', section: 'energy', desc: 'Solar PV, offshore wind, geothermal, hydroelectric, green hydrogen.' },
        { title: 'Sustainable Lifestyle & Eco Habits', section: 'lifestyle', desc: 'Green transportation, seasonal diet, conscious consumption, home efficiency.' },
        { title: 'Scientific Carbon & Water Calculator', section: 'calculator', desc: 'Interactive C++-powered life-cycle footprint and tree offset calculator.' },
        { title: 'Environmental Events & Campaigns', section: 'events', desc: 'Tree planting drives, beach clean-ups, Earth Day 2026, climate workshops.' }
    ];

    function openSearch() {
        searchModal.classList.add('open');
        setTimeout(() => searchInput?.focus(), 100);
    }

    function closeSearch() {
        searchModal.classList.remove('open');
        if (searchInput) searchInput.value = '';
        renderSearchResults('');
    }

    if (searchOpenBtn) searchOpenBtn.addEventListener('click', openSearch);
    if (searchCloseBtn) searchCloseBtn.addEventListener('click', closeSearch);

    searchModal.addEventListener('click', (e) => {
        if (e.target === searchModal) closeSearch();
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && searchModal.classList.contains('open')) closeSearch();
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            openSearch();
        }
    });

    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            renderSearchResults(e.target.value.trim().toLowerCase());
        });
    }

    function renderSearchResults(query) {
        if (!searchResultsList) return;
        if (!query) {
            searchResultsList.innerHTML = `<li style="text-align: center; color: var(--text-muted); padding: 1.5rem 0;">Type to search environmental topics, solutions, or guides...</li>`;
            return;
        }

        const matches = searchIndex.filter(item =>
            item.title.toLowerCase().includes(query) || item.desc.toLowerCase().includes(query)
        );

        if (matches.length === 0) {
            searchResultsList.innerHTML = `<li style="text-align: center; color: var(--text-muted); padding: 1.5rem 0;">No matching topics found for "${query}".</li>`;
            return;
        }

        searchResultsList.innerHTML = matches.map(item => `
            <li class="search-result-item">
                <a href="#${item.section}" onclick="document.getElementById('search-modal').classList.remove('open')">
                    <div class="search-item-title">${item.title}</div>
                    <div class="search-item-snippet">${item.desc}</div>
                </a>
            </li>
        `).join('');
    }
}

// --- 7. Rotating Daily Environmental Tips (FR-15) ---
function initDailyTips() {
    const tipTextEl = document.getElementById('daily-tip-text');
    const nextTipBtn = document.getElementById('next-tip-btn');

    const tips = [
        "Turn off lights and electronics when leaving a room to cut idle phantom power consumption.",
        "Fix dripping faucets immediately—a single leaking tap can waste over 11,000 liters of water annually.",
        "Carry a reusable stainless-steel water bottle and canvas shopping tote to eliminate daily single-use plastics.",
        "Incorporate at least two plant-based meals per week to shrink your dietary carbon and water footprint.",
        "Wash clothes in cold water with full loads; 90% of a washing machine's energy goes toward heating water.",
        "Opt for walking, bicycling, or public transit for trips under 3 km to immediately reduce urban smog.",
        "Set your home thermostat 1-2 degrees higher in summer and lower in winter for major energy savings.",
        "Start a simple kitchen counter compost bin to convert vegetable peels and coffee grounds into rich soil nutrients."
    ];

    let tipIndex = Math.floor(Math.random() * tips.length);
    if (tipTextEl) tipTextEl.textContent = tips[tipIndex];

    if (nextTipBtn && tipTextEl) {
        nextTipBtn.addEventListener('click', () => {
            tipIndex = (tipIndex + 1) % tips.length;
            tipTextEl.style.opacity = '0';
            setTimeout(() => {
                tipTextEl.textContent = tips[tipIndex];
                tipTextEl.style.opacity = '1';
                tipTextEl.style.transition = 'opacity 0.3s ease';
            }, 200);
        });
    }

    // Daily Tips Checklist
    const tipCheckboxes = document.querySelectorAll('.daily-habit-checkbox');
    tipCheckboxes.forEach(cb => {
        cb.addEventListener('change', () => {
            const count = document.querySelectorAll('.daily-habit-checkbox:checked').length;
            const progressEl = document.getElementById('habit-progress-badge');
            if (progressEl) progressEl.textContent = `${count} of ${tipCheckboxes.length} Completed Today`;
            if (count === tipCheckboxes.length) {
                showToast("🌟 Fantastic! You completed all daily environmental habits!", "success");
            }
        });
    });
}

// --- 8. "One Planet, One Responsibility" Campaign & Digital Certificate (FR-42) ---
function initPledgeSystem() {
    const pledgeForm = document.getElementById('pledge-form');
    if (!pledgeForm) return;

    pledgeForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const name = document.getElementById('pledge-name')?.value.trim();
        const email = document.getElementById('pledge-email')?.value.trim();
        const city = document.getElementById('pledge-city')?.value.trim();

        const checkedPledges = Array.from(document.querySelectorAll('input[name="pledge_items"]:checked')).map(el => el.value);

        if (!name || !email) {
            showToast('Please provide your name and email to sign the pledge.', 'error');
            return;
        }

        if (checkedPledges.length === 0) {
            showToast('Please select at least one environmental commitment.', 'error');
            return;
        }

        const res = await API.submitPledge({
            name,
            email,
            city: city || 'Global Citizen',
            pledges: checkedPledges
        });

        if (res && res.status === 'success') {
            showToast('Pledge signed! Generating your official digital certificate...', 'success');
            renderPledgeCertificate(name, res.badge_id, checkedPledges.length);
            pledgeForm.reset();
        } else {
            showToast(res.message || 'Error recording pledge.', 'error');
        }
    });
}

function renderPledgeCertificate(name, badgeId, count) {
    const cardContainer = document.getElementById('pledge-certificate-wrap');
    if (!cardContainer) return;

    const dateStr = new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });

    cardContainer.innerHTML = `
        <div class="pledge-badge-card" style="animation: modalPop 0.4s ease;">
            <div class="badge-seal">🌍</div>
            <h3 style="font-size: 1.5rem; font-weight: 800; margin-bottom: 0.5rem; color: #ffffff;">CERTIFICATE OF COMMITMENT</h3>
            <p style="font-size: 0.85rem; color: #a7f3d0; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 1.25rem;">One Planet, One Responsibility Campaign</p>
            <div style="background: rgba(255, 255, 255, 0.12); padding: 1.25rem; border-radius: 8px; margin-bottom: 1.25rem; border: 1px dashed rgba(255,255,255,0.3);">
                <p style="font-size: 0.9rem; color: #e2e8f0; margin-bottom: 0.35rem;">This certifies that</p>
                <div style="font-size: 1.6rem; font-weight: 800; color: #ffffff; text-decoration: underline; text-decoration-color: #34d399;">${escapeHTML(name)}</div>
                <p style="font-size: 0.88rem; color: #e2e8f0; margin-top: 0.5rem;">has solemnly pledged ${count} sustainable actions to protect the Earth's climate and biodiversity.</p>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: #cbd5e1; border-top: 1px solid rgba(255,255,255,0.2); padding-top: 0.75rem;">
                <span>ID: <strong>${badgeId}</strong></span>
                <span>Date: <strong>${dateStr}</strong></span>
            </div>
            <button class="btn btn-sm btn-outline" style="margin-top: 1rem; color: white; border-color: white;" onclick="window.print()">🖨️ Print / Save Certificate</button>
        </div>
    `;
}

// --- 9. Events Module & Ticket Booking (FR-17) ---
function initEventsModule() {
    const filterPills = document.querySelectorAll('.event-filter-bar .filter-pill');
    const eventsContainer = document.getElementById('events-cards-grid');

    if (filterPills.length > 0) {
        filterPills.forEach(pill => {
            pill.addEventListener('click', async () => {
                filterPills.forEach(p => p.classList.remove('active'));
                pill.classList.add('active');
                const cat = pill.getAttribute('data-category');
                loadEvents(cat);
            });
        });
    }

    // Modal elements
    const regModal = document.getElementById('event-register-modal');
    const modalClose = document.getElementById('event-modal-close');
    const regForm = document.getElementById('event-register-form');

    if (modalClose && regModal) {
        modalClose.addEventListener('click', () => regModal.classList.remove('open'));
        regModal.addEventListener('click', (e) => {
            if (e.target === regModal) regModal.classList.remove('open');
        });
    }

    if (regForm) {
        regForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const eventId = document.getElementById('reg-event-id')?.value;
            const name = document.getElementById('reg-name')?.value.trim();
            const email = document.getElementById('reg-email')?.value.trim();
            const phone = document.getElementById('reg-phone')?.value.trim();
            const tickets = parseInt(document.getElementById('reg-tickets')?.value || 1);

            if (!name || !email) {
                showToast('Please fill in your name and email.', 'error');
                return;
            }

            const res = await API.registerEvent(eventId, { name, email, phone, tickets });
            if (res && res.status === 'success') {
                showToast(`🎉 ${res.message}`, 'success');
                regModal.classList.remove('open');
                regForm.reset();
                loadEvents(); // Reload counts
            } else {
                showToast(res.message || 'Registration failed.', 'error');
            }
        });
    }

    // Load initial events
    loadEvents('all');
}

async function loadEvents(category = 'all') {
    const container = document.getElementById('events-cards-grid');
    if (!container) return;

    container.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 2rem; color: var(--text-muted);">Loading upcoming environmental events...</div>`;

    const events = await API.getEvents(category);
    if (!events || events.length === 0) {
        container.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 2rem; color: var(--text-muted);">No events found in this category.</div>`;
        return;
    }

    container.innerHTML = events.map(evt => {
        const dateObj = new Date(evt.event_date);
        const day = dateObj.getDate() || '15';
        const month = dateObj.toLocaleString('default', { month: 'short' }) || 'OCT';
        const remaining = Math.max(0, evt.capacity - evt.registered_count);

        return `
            <div class="event-card">
                <div class="event-card-header">
                    <span class="event-cat-tag">${escapeHTML(evt.category)}</span>
                    <div class="event-date-badge">
                        <div style="font-size: 1.15rem; line-height: 1;">${day}</div>
                        <div style="font-size: 0.7rem; text-transform: uppercase;">${month}</div>
                    </div>
                </div>
                <div class="event-card-body">
                    <h3 class="event-title">${escapeHTML(evt.title)}</h3>
                    <div class="event-meta">
                        <div class="event-meta-item">📍 ${escapeHTML(evt.location)}</div>
                        <div class="event-meta-item">🏛️ Organized by ${escapeHTML(evt.organizer)}</div>
                    </div>
                    <p class="event-desc">${escapeHTML(evt.description)}</p>
                    <div class="event-footer">
                        <span class="event-seats">🎟️ ${remaining} seats left</span>
                        <button class="btn btn-primary btn-sm" onclick="openEventRegisterModal(${evt.id}, '${escapeHTML(evt.title)}')">Register Free</button>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

window.openEventRegisterModal = function(id, title) {
    const modal = document.getElementById('event-register-modal');
    const titleEl = document.getElementById('reg-modal-event-title');
    const idInput = document.getElementById('reg-event-id');

    if (modal && titleEl && idInput) {
        titleEl.textContent = title;
        idInput.value = id;
        modal.classList.add('open');
    }
};

// --- 10. Contact & Feedback Form (FR-19) ---
function initFeedbackForm() {
    const form = document.getElementById('contact-feedback-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const name = document.getElementById('fb-name')?.value.trim();
        const email = document.getElementById('fb-email')?.value.trim();
        const category = document.getElementById('fb-category')?.value || 'general';
        const subject = document.getElementById('fb-subject')?.value.trim();
        const message = document.getElementById('fb-message')?.value.trim();

        if (!name || !email || !subject || !message) {
            showToast('Please fill in all required fields.', 'error');
            return;
        }

        const res = await API.submitFeedback({ name, email, category, subject, message });
        if (res && res.status === 'success') {
            showToast(res.message, 'success');
            form.reset();
        } else {
            showToast(res.message || 'Error submitting feedback.', 'error');
        }
    });
}

// --- 11. Newsletter Subscriptions ---
function initNewsletterForms() {
    const forms = document.querySelectorAll('.newsletter-form');
    forms.forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const input = form.querySelector('input[type="email"]');
            const email = input?.value.trim();
            if (!email) return;

            const res = await API.subscribeNewsletter(email);
            if (res && (res.status === 'success' || res.status === 'info')) {
                showToast(res.message, 'success');
                form.reset();
            } else {
                showToast(res.message || 'Subscription failed.', 'error');
            }
        });
    });
}

// --- 12. Interactive Greenhouse Effect Visualizer (Section 8) ---
function initGreenhouseSimulator() {
    const slider = document.getElementById('ghg-slider');
    const ppmVal = document.getElementById('ghg-ppm-val');
    const tempAnomaly = document.getElementById('ghg-temp-val');
    const heatRayLayer = document.getElementById('ghg-heat-layer');

    if (!slider) return;

    slider.addEventListener('input', () => {
        const ppm = parseInt(slider.value);
        if (ppmVal) ppmVal.textContent = `${ppm} ppm`;

        // Pre-industrial baseline: 280 ppm = 0.0 C
        // Formula estimation: deltaT = 3.0 * ln(ppm/280) / ln(2)
        const deltaT = 3.0 * (Math.log(ppm / 280) / Math.LN2);
        if (tempAnomaly) {
            tempAnomaly.textContent = `+${deltaT.toFixed(2)} °C above pre-industrial`;
            tempAnomaly.style.color = deltaT > 1.5 ? '#ef4444' : '#f59e0b';
        }

        if (heatRayLayer) {
            const opacity = Math.min(0.9, Math.max(0.1, (ppm - 280) / 400));
            heatRayLayer.style.opacity = opacity;
        }
    });
}

// Utility: HTML Sanitizer
function escapeHTML(str) {
    if (!str) return '';
    return str.replace(/[&<>'"]/g,
        tag => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            "'": '&#39;',
            '"': '&quot;'
        }[tag] || tag)
    );
}
