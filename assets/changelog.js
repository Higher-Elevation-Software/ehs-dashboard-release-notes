(function () {
  const iconMap = {
    Feature: '🚀',
    Improvement: '✨',
    Fix: '🐛',
    Security: '🔒',
    Internal: '🛠️',
    Update: '📦',
  };

  const logoSvg = `
    <svg viewBox="0 0 120 60" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M13 44L34 18l13 16-8 10" stroke="#c7f1ff" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M54 45 75 14l21 31" stroke="#96e1ff" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
      <circle cx="100" cy="15" r="4" fill="#d6f5ff"/>
    </svg>`;

  const qs = (s, scope = document) => scope.querySelector(s);
  const qsa = (s, scope = document) => Array.from(scope.querySelectorAll(s));

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    if (!Number.isNaN(d.getTime())) {
      return d.toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      });
    }
    return dateStr;
  };

  function enhanceIndex() {
    const source = qs('#release-source');
    const cardsHost = qs('#release-cards');
    if (!source || !cardsHost) return;

    document.documentElement.classList.add('changelog-enhanced');

    const releases = qsa('li', source).map((li) => ({
      title: (li.dataset.title || li.textContent || '').trim(),
      date: (li.dataset.date || '').trim(),
      rawDate: (li.dataset.rawdate || '').trim(),
      category: (li.dataset.category || 'Update').trim(),
      component: (li.dataset.component || 'Unspecified').trim(),
      environment: (li.dataset.environment || 'production').trim(),
      link: (li.dataset.link || li.querySelector('a')?.getAttribute('href') || '').trim(),
    }));

    const state = {
      category: 'All',
      component: 'All',
      search: '',
    };

    const unique = (arr) => Array.from(new Set(arr)).filter(Boolean);
    const categories = unique(releases.map((r) => r.category));
    const components = unique(releases.map((r) => r.component));

    const filterBar = qs('#filter-bar');
    const countLabel = qs('#release-count');

    // Build search box
    const searchBox = document.createElement('label');
    searchBox.className = 'search-box';
    searchBox.innerHTML = `
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#6f8091" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="7"></circle><line x1="16.65" y1="16.65" x2="21" y2="21"></line></svg>
      <input type="search" aria-label="Search release titles" placeholder="Search releases" />
    `;
    const searchInput = searchBox.querySelector('input');
    searchInput.addEventListener('input', (e) => {
      state.search = (e.target.value || '').toLowerCase();
      render();
    });
    filterBar.appendChild(searchBox);

    const filterGroup = (label, values, key) => {
      const group = document.createElement('div');
      group.className = 'filter-bar';
      const base = document.createElement('span');
      base.className = 'eyebrow';
      base.textContent = label;
      group.appendChild(base);

      const addChip = (value, display) => {
        const chip = document.createElement('button');
        chip.className = 'chip';
        chip.type = 'button';
        chip.textContent = display;
        if (state[key] === value) chip.classList.add('active');
        chip.addEventListener('click', () => {
          state[key] = value;
          render();
        });
        group.appendChild(chip);
      };

      addChip('All', 'All');
      values.forEach((v) => addChip(v, v));
      return group;
    };

    filterBar.appendChild(filterGroup('Category', categories, 'category'));
    filterBar.appendChild(filterGroup('Component', components, 'component'));

    function filtered() {
      return releases.filter((r) => {
        const matchesCategory = state.category === 'All' || r.category === state.category;
        const matchesComponent = state.component === 'All' || r.component === state.component;
        const matchesSearch = !state.search || r.title.toLowerCase().includes(state.search);
        return matchesCategory && matchesComponent && matchesSearch;
      });
    }

    function renderCard(release) {
      const card = document.createElement('article');
      card.className = 'release-card';

      const header = document.createElement('div');
      header.className = 'release-card__header';

      const titleWrap = document.createElement('div');
      titleWrap.className = 'release-card__title';

      const title = document.createElement('h3');
      title.textContent = release.title;
      titleWrap.appendChild(title);

      const metaRow = document.createElement('div');
      metaRow.className = 'meta-row';
      const date = document.createElement('span');
      date.textContent = formatDate(release.date);
      metaRow.appendChild(date);

      const component = document.createElement('span');
      component.className = 'meta-pill';
      component.textContent = release.component;
      metaRow.appendChild(component);

      const environment = document.createElement('span');
      environment.className = 'meta-pill';
      environment.textContent = release.environment;
      metaRow.appendChild(environment);

      titleWrap.appendChild(metaRow);

      const actions = document.createElement('div');
      actions.className = 'release-card__actions';

      const badge = document.createElement('span');
      badge.className = 'category-badge';
      badge.dataset.type = release.category;
      badge.textContent = `${iconMap[release.category] || iconMap.Update} ${release.category}`;
      actions.appendChild(badge);

      const toggle = document.createElement('button');
      toggle.type = 'button';
      toggle.className = 'ghost-button';
      toggle.setAttribute('aria-expanded', 'false');
      toggle.textContent = 'Expand';
      actions.appendChild(toggle);

      header.appendChild(titleWrap);
      header.appendChild(actions);

      const body = document.createElement('div');
      body.className = 'release-card__body';
      body.hidden = true;

      const summary = document.createElement('p');
      summary.className = 'summary-small';
      summary.textContent = 'Loading details…';
      body.appendChild(summary);

      const footer = document.createElement('div');
      footer.className = 'release-card__footer';
      const link = document.createElement('a');
      link.href = release.link;
      link.textContent = 'Open release note ↗';
      link.target = '_blank';
      footer.appendChild(link);
      body.appendChild(footer);

      let loaded = false;
      async function loadSummary() {
        if (loaded || !release.link) return;
        loaded = true;
        try {
          const res = await fetch(release.link);
          const html = await res.text();
          const doc = new DOMParser().parseFromString(html, 'text/html');
          const summaryEl =
            doc.querySelector('.release-summary-card p') ||
            doc.querySelector('.markdown-body p') ||
            doc.querySelector('p');
          const text = summaryEl?.textContent?.trim();
          summary.textContent = text || 'View the full note for details.';
        } catch (err) {
          summary.textContent = 'View the full note for details.';
        }
      }

      toggle.addEventListener('click', () => {
        const expanded = toggle.getAttribute('aria-expanded') === 'true';
        toggle.setAttribute('aria-expanded', String(!expanded));
        toggle.textContent = expanded ? 'Expand' : 'Collapse';
        body.hidden = expanded;
        if (!expanded) loadSummary();
      });

      card.appendChild(header);
      card.appendChild(body);
      return card;
    }

    function render() {
      // Refresh active states
      qsa('.chip', filterBar).forEach((chip) => {
        const label = chip.textContent?.trim();
        const parentLabel = chip.parentElement?.querySelector('.eyebrow')?.textContent;
        const key = parentLabel === 'Category' ? 'category' : parentLabel === 'Component' ? 'component' : null;
        if (!key) return;
        chip.classList.toggle('active', state[key] === label || (label === 'All' && state[key] === 'All'));
      });

      cardsHost.innerHTML = '';
      const list = filtered();
      list.forEach((release) => cardsHost.appendChild(renderCard(release)));
      if (countLabel) countLabel.textContent = `Showing ${list.length} of ${releases.length} updates`;
    }

    render();
  }

  function enhanceReleasePage() {
    const meta = qs('#release-meta');
    if (!meta) return;
    document.documentElement.classList.add('release-enhanced');

    const titleText = meta.dataset.title || qs('h1')?.textContent || 'Release note';
    const component = meta.dataset.component || 'EHS Dashboard';
    const environment = meta.dataset.environment || 'production';
    const category = meta.dataset.category || 'Update';
    const date = meta.dataset.date || meta.dataset.deployTime || '';
    const sha = meta.dataset.sha || '';

    const hero = document.createElement('section');
    hero.className = 'release-hero';
    hero.innerHTML = `
      <div class="hero-shell">
        <div class="hero-grid">
          <div class="brand-mark">
            <div class="brand-logo">${logoSvg}</div>
            <div class="brand-name">EHS-Dashboard</div>
          </div>
          <div class="hero-text">
            <p class="hero-eyebrow">External Access View</p>
            <h1>${titleText}</h1>
            <p class="hero-small-note">${component} • ${formatDate(date)}</p>
          </div>
          <div class="hero-badges">
            <span class="pill">${environment}</span>
            <span class="pill secondary">${category}</span>
          </div>
        </div>
      </div>`;

    // Capture existing body content (excluding assets and meta)
    const contentNodes = qsa('body > *').filter(
      (el) =>
        !el.matches('#release-meta') &&
        !(el.tagName === 'LINK' && el.getAttribute('href')?.includes('changelog.css')) &&
        !(el.tagName === 'SCRIPT' && el.getAttribute('src')?.includes('changelog.js'))
    );

    const main = document.createElement('section');
    main.className = 'release-page-main';

    const metaGrid = document.createElement('div');
    metaGrid.className = 'meta-grid';
    const metaTile = (label, value) => {
      const tile = document.createElement('div');
      tile.className = 'meta-tile';
      tile.innerHTML = `<span>${label}</span><strong>${value}</strong>`;
      return tile;
    };

    [
      metaTile('Component', component),
      metaTile('Environment', environment),
      metaTile('Category', category),
      metaTile('Deployed', formatDate(date)),
      sha ? metaTile('SHA', sha) : null,
    ]
      .filter(Boolean)
      .forEach((tile) => metaGrid.appendChild(tile));

    const summaryCard = document.createElement('div');
    summaryCard.className = 'release-summary-card';
    summaryCard.innerHTML = '<h2>What changed</h2>';

    const metaDetails = qsa('p').find((p) => /Component:/i.test(p.textContent));
    if (metaDetails) metaDetails.classList.add('suppress-original');

    const summarySource = qsa('p').find((p) => !/Component:/i.test(p.textContent));
    const summaryText = summarySource?.textContent?.trim();
    if (summarySource) summarySource.classList.add('suppress-original');

    const summaryPara = document.createElement('p');
    summaryPara.textContent = summaryText || 'See details below for this update.';
    summaryCard.appendChild(summaryPara);

    main.appendChild(summaryCard);
    main.appendChild(metaGrid);

    contentNodes.forEach((node) => main.appendChild(node));

    document.body.appendChild(hero);
    document.body.appendChild(main);
  }

  document.addEventListener('DOMContentLoaded', () => {
    enhanceIndex();
    enhanceReleasePage();
  });
})();
