/* Logical Knight — site behaviour. All demo data below is fictional. */
(() => {
  "use strict";

  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const root = document.documentElement;
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const motionOK = () => !reduceMotion.matches && !root.classList.contains("motion-paused");

  /* ---------- Navigation ---------- */
  const nav = $(".nav");
  const onScroll = () => nav && nav.classList.toggle("is-scrolled", window.scrollY > 8);
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  const toggle = $(".nav__toggle");
  const menu = $("#mobile-menu");
  if (toggle && menu) {
    const setOpen = (open) => {
      toggle.setAttribute("aria-expanded", String(open));
      toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
      menu.classList.toggle("is-open", open);
      menu.inert = !open;
      document.body.classList.toggle("menu-open", open);
      nav.classList.toggle("is-scrolled", open || window.scrollY > 8);
      if (open) menu.querySelector("a")?.focus();
    };
    menu.inert = true;
    toggle.addEventListener("click", () => setOpen(toggle.getAttribute("aria-expanded") !== "true"));
    menu.addEventListener("click", (e) => { if (e.target.closest("a")) setOpen(false); });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && menu.classList.contains("is-open")) { setOpen(false); toggle.focus(); }
    });
    window.matchMedia("(min-width: 921px)").addEventListener("change", (e) => { if (e.matches) setOpen(false); });
  }

  /* ---------- Reveal on scroll ---------- */
  if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => {
        if (!en.isIntersecting) return;
        en.target.classList.add("is-in");
        en.target.classList.remove("hl-wait");
        io.unobserve(en.target);
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    $$("[data-reveal], .hl-wait").forEach((el) => io.observe(el));
  } else {
    $$("[data-reveal]").forEach((el) => el.classList.add("is-in"));
  }

  /* ---------- Motion toggle ---------- */
  const motionListeners = [];
  const syncMotionButtons = () => {
    const paused = root.classList.contains("motion-paused");
    $$("[data-motion-toggle]").forEach((b) => {
      b.setAttribute("aria-pressed", String(paused));
      const label = b.querySelector("[data-label]");
      if (label) label.textContent = paused ? "Play" : "Pause";
      b.querySelector(".i-pause")?.toggleAttribute("hidden", paused);
      b.querySelector(".i-play")?.toggleAttribute("hidden", !paused);
    });
  };
  $$("[data-motion-toggle]").forEach((b) => b.addEventListener("click", () => {
    root.classList.toggle("motion-paused");
    syncMotionButtons();
    motionListeners.forEach((fn) => fn());
  }));

  /* ---------- JSON / HTTP highlighter ---------- */
  const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  const hlLine = (line) => {
    const e = esc(line);
    if (/^\s*(#|\/\/)/.test(line)) return `<span class="tk-c">${e}</span>`;
    const m = e.match(/^(GET|POST|PUT|PATCH|DELETE|HTTP\/[\d.]+)(\s.*)?$/);
    if (m) return `<span class="tk-m">${m[1]}</span>${m[2] || ""}`;
    return e.replace(/("(?:[^"\\]|\\.)*")(\s*:)?|\b(true|false|null)\b|(-?\b\d+(?:\.\d+)?\b)|([{}[\],])/g,
      (all, str, colon, bool, num, punct) => {
        if (str) return colon ? `<span class="tk-k">${str}</span><span class="tk-p">${colon}</span>` : `<span class="tk-s">${str}</span>`;
        if (bool) return `<span class="tk-b">${bool}</span>`;
        if (num) return `<span class="tk-n">${num}</span>`;
        return `<span class="tk-p">${punct}</span>`;
      });
  };
  const highlight = (text, numbered) => text.replace(/^\n+|\s+$/g, "").split("\n")
    .map((l) => numbered ? `<span class="ln">${hlLine(l) || " "}</span>` : hlLine(l)).join(numbered ? "" : "\n");
  $$("pre[data-hl]").forEach((pre) => {
    pre.dataset.raw = pre.textContent.replace(/^\n+|\s+$/g, "");
    pre.innerHTML = highlight(pre.textContent, pre.dataset.hl === "lines");
  });

  /* ---------- Generic ARIA tabs ---------- */
  const initTabs = (list, onChange) => {
    const tabs = $$('[role="tab"]', list);
    const select = (tab, focus) => {
      tabs.forEach((t) => {
        const on = t === tab;
        t.setAttribute("aria-selected", String(on));
        t.tabIndex = on ? 0 : -1;
        const panel = t.getAttribute("aria-controls") && document.getElementById(t.getAttribute("aria-controls"));
        if (panel && list.dataset.shared === undefined) panel.hidden = !on;
      });
      if (focus) tab.focus();
      onChange && onChange(tab, tabs.indexOf(tab));
    };
    tabs.forEach((t, i) => {
      t.tabIndex = t.getAttribute("aria-selected") === "true" ? 0 : -1;
      t.addEventListener("click", () => select(t));
      t.addEventListener("keydown", (e) => {
        const horiz = list.getAttribute("aria-orientation") !== "vertical";
        const next = horiz ? "ArrowRight" : "ArrowDown";
        const prev = horiz ? "ArrowLeft" : "ArrowUp";
        let j = null;
        if (e.key === next) j = (i + 1) % tabs.length;
        else if (e.key === prev) j = (i - 1 + tabs.length) % tabs.length;
        else if (e.key === "Home") j = 0;
        else if (e.key === "End") j = tabs.length - 1;
        if (j !== null) { e.preventDefault(); select(tabs[j], true); }
      });
    });
    return { select: (i) => select(tabs[i]) };
  };
  $$('[role="tablist"][data-tabs]').forEach((l) => initTabs(l));

  /* ---------- Copy buttons ---------- */
  $$("[data-copy]").forEach((btn) => btn.addEventListener("click", async () => {
    const scope = btn.closest(".code");
    const pre = scope && $$("pre", scope).find((p) => !p.hidden);
    if (!pre) return;
    const label = btn.querySelector("span");
    try {
      await navigator.clipboard.writeText(pre.dataset.raw || pre.textContent);
      if (label) label.textContent = "Copied";
    } catch { if (label) label.textContent = "Select to copy"; }
    setTimeout(() => { if (label) label.textContent = "Copy"; }, 1600);
  }));

  /* ---------- Visibility helper ---------- */
  const whenVisible = (el, cb) => {
    if (!("IntersectionObserver" in window)) { cb(true); return; }
    new IntersectionObserver((es) => es.forEach((e) => cb(e.isIntersecting)), { threshold: 0.15 }).observe(el);
  };

  /* ---------- Hero: cycling outcome record ---------- */
  const cycle = $("[data-cycle]");
  if (cycle) {
    const items = [
      { type: "Facility opening", entity: "Acme Example Industries", where: "Bremen, DE", when: "28 Sep 2026", quote: "“Our new Bremen facility will begin operations…”" },
      { type: "Product launch", entity: "Harbor Example Systems", where: "Rotterdam, NL", when: "27 Sep 2026", quote: "“Vanaf vandaag leverbaar in de hele Benelux…”" },
      { type: "Partnership", entity: "Vale Example Logistics", where: "Lyon, FR", when: "26 Sep 2026", quote: "« Un nouveau partenariat logistique… »" },
    ];
    let i = 0, timer = null, visible = false;
    const fields = $$("[data-f]", cycle);
    const swap = () => {
      i = (i + 1) % items.length;
      fields.forEach((f) => f.classList.add("is-out"));
      setTimeout(() => {
        fields.forEach((f) => { f.textContent = items[i][f.dataset.f]; f.classList.remove("is-out"); });
      }, 350);
    };
    const run = () => {
      clearInterval(timer); timer = null;
      if (visible && motionOK()) timer = setInterval(swap, 4200);
    };
    whenVisible(cycle, (v) => { visible = v; run(); });
    motionListeners.push(run);
  }

  /* ---------- Live demo (fictional data, no network) ---------- */
  const SCENARIOS = [
    {
      key: "facility", source: 1,
      type: "Facility opening", code: "facility_opening",
      company: "Acme Example Industries", place: "Bremen, Germany", loc: "Bremen, DE",
      detected: "28 Sep 2026", ts: "2026-09-28T09:14:03Z", lang: "EN", langCode: "en",
      url: "acme.example/en/sites",
      quote: "Our new Bremen facility will begin operations in the fourth quarter.",
      steps: ["Checked 3 sources", "+1 paragraph on /en/sites", "Evidence captured · source confirmed", "Classified: facility_opening"],
    },
    {
      key: "launch", source: 0,
      type: "Product launch", code: "product_launch",
      company: "Acme Example Industries", place: "Germany", loc: "DE",
      detected: "28 Sep 2026", ts: "2026-09-28T07:52:41Z", lang: "DE", langCode: "de",
      url: "acme.example/de/news",
      quote: "Ab sofort ist die neue Baureihe K7 in ganz Europa erhältlich.",
      steps: ["Checked 3 sources", "New article on /de/news", "Evidence captured · source confirmed", "Classified: product_launch"],
    },
    {
      key: "partner", source: 2,
      type: "Partnership", code: "partnership",
      company: "Acme Example Industries", place: "Lyon, France", loc: "Lyon, FR",
      detected: "27 Sep 2026", ts: "2026-09-27T16:30:12Z", lang: "FR", langCode: "fr",
      url: "acme.example/fr/press",
      quote: "Acme Example Industries annonce un partenariat logistique à Lyon.",
      steps: ["Checked 3 sources", "New release on /fr/press", "Evidence captured · source confirmed", "Classified: partnership"],
    },
  ];
  const SOURCES = ["acme.example/de/news", "acme.example/en/sites", "acme.example/fr/press"];

  const eventJSON = (s) => JSON.stringify({
    event_type: s.code,
    company: s.company,
    location: s.loc,
    detected_at: s.ts,
    evidence: { quote: s.quote, language: s.langCode, source_url: "https://" + s.url },
    verified: true,
  }, null, 2);

  const demo = $("[data-demo]");
  if (demo) {
    const srcEls = $$(".source", demo);
    const stepEls = $$(".pstep", demo);
    const eventView = $("#demo-event", demo);
    const jsonView = $("#demo-json", demo);
    const progress = $(".demo__progress i", demo);
    const live = $("[data-demo-live]", demo);
    const tabsList = $(".demo__tabs", demo);
    const playBtn = $("[data-demo-play]", demo);
    const replayBtn = $("[data-demo-replay]", demo);
    const checkEls = $$(".source__checked", demo);

    const CYCLE = 12500;
    const T = { source: 900, change: 2100, verify: 3500, event: 4900, card: 5700 };
    let idx = 0, t0 = 0, raf = 0, visible = false, userPaused = false, lastPhase = -1, announce = false;
    let checkAges = [14, 41, 8];

    const emptyHTML = `<div class="event-empty"><div>Watching ${SOURCES.length} sources for meaningful change…<span class="scan" aria-hidden="true"></span></div></div>`;
    const cardHTML = (s) => `
      <article class="event anim-in" aria-label="Verified event: ${s.type}, ${s.company}">
        <div class="event__head">
          <div class="event__top">
            <span class="event__type">${s.type}</span>
            <span class="badge badge--gold"><svg viewBox="0 0 12 12" width="11" height="11" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M2.5 6.2l2.3 2.3 4.7-5"/></svg>Verified</span>
          </div>
          <div class="event__company">${s.company}</div>
          <div class="event__place">${s.place}</div>
        </div>
        <div class="event__fields">
          <div><span class="k">Detected</span><span class="v">${s.detected}</span></div>
          <div><span class="k">Language</span><span class="v mono">${s.lang}</span></div>
          <div><span class="k">Event type</span><span class="v mono">${s.code}</span></div>
        </div>
        <div class="event__evidence">
          <span class="k">Original evidence</span>
          <blockquote class="event__quote" lang="${s.langCode}">“${s.quote}”</blockquote>
          <span class="event__src">Source · ${s.url}</span>
        </div>
      </article>`;

    const setSourceStates = (hot) => srcEls.forEach((el, i) => {
      const isHot = i === hot;
      el.classList.toggle("is-hot", isHot);
      $(".source__label", el).textContent = isHot ? "Change detected" : "Monitoring";
    });

    const render = (phase) => {
      if (phase === lastPhase) return;
      lastPhase = phase;
      const s = SCENARIOS[idx];
      stepEls.forEach((el, i) => {
        el.classList.toggle("is-active", i === phase - 1 && phase < 5);
        el.classList.toggle("is-done", i < phase - 1 || phase >= 5);
        $(".pstep__detail", el).textContent = i < phase ? s.steps[i] : "—";
      });
      setSourceStates(phase >= 2 ? s.source : -1);
      if (phase >= 5) {
        eventView.innerHTML = cardHTML(s);
        jsonView.innerHTML = highlight(eventJSON(s));
        if (announce && live) live.textContent = `Verified event: ${s.type}, ${s.company}, ${s.place}.`;
        announce = false;
      } else {
        eventView.innerHTML = emptyHTML;
        jsonView.innerHTML = `<span class="tk-c">// waiting for a verified event…</span>`;
      }
    };
    const phaseAt = (t) => t >= T.card ? 5 : t >= T.event ? 4 : t >= T.verify ? 3 : t >= T.change ? 2 : t >= T.source ? 1 : 0;

    const tabs = initTabs(tabsList, (_, i) => { if (i !== idx) start(i, true); });

    const frame = (now) => {
      const t = now - t0;
      render(phaseAt(t));
      if (progress) progress.style.width = Math.min(100, (t / CYCLE) * 100) + "%";
      if (t >= CYCLE) { start((idx + 1) % SCENARIOS.length, false); return; }
      raf = requestAnimationFrame(frame);
    };
    const running = () => visible && !userPaused && motionOK();
    const start = (i, fromUser) => {
      cancelAnimationFrame(raf);
      idx = i;
      announce = !!fromUser;
      lastPhase = -1;
      $$('[role="tab"]', tabsList).forEach((t, j) => { t.setAttribute("aria-selected", String(j === i)); t.tabIndex = j === i ? 0 : -1; });
      if (!motionOK()) { render(5); if (progress) progress.style.width = "100%"; return; }
      t0 = performance.now();
      if (running()) raf = requestAnimationFrame(frame);
      else render(0);
    };
    let pausedAt = 0;
    const resume = () => {
      cancelAnimationFrame(raf);
      if (!motionOK()) { render(5); return; }
      if (running()) { t0 = performance.now() - pausedAt; raf = requestAnimationFrame(frame); }
    };
    const pause = () => { pausedAt = performance.now() - t0; cancelAnimationFrame(raf); };

    playBtn?.addEventListener("click", () => {
      userPaused = !userPaused;
      playBtn.setAttribute("aria-pressed", String(userPaused));
      $("[data-label]", playBtn).textContent = userPaused ? "Play" : "Pause";
      $(".i-pause", playBtn).toggleAttribute("hidden", userPaused);
      $(".i-play", playBtn).toggleAttribute("hidden", !userPaused);
      userPaused ? pause() : resume();
    });
    replayBtn?.addEventListener("click", () => { userPaused = false; playBtn?.setAttribute("aria-pressed", "false"); start(idx, true); });
    motionListeners.push(() => {
      userPaused = root.classList.contains("motion-paused");
      if (playBtn) {
        playBtn.setAttribute("aria-pressed", String(userPaused));
        $("[data-label]", playBtn).textContent = userPaused ? "Play" : "Pause";
        $(".i-pause", playBtn).toggleAttribute("hidden", userPaused);
        $(".i-play", playBtn).toggleAttribute("hidden", !userPaused);
      }
      userPaused ? pause() : resume();
    });

    setInterval(() => {
      if (!visible) return;
      checkAges = checkAges.map((a) => (a >= 59 ? 2 : a + 1));
      checkEls.forEach((el, i) => { el.textContent = `checked ${checkAges[i]}s ago`; });
    }, 1000);

    let started = false;
    whenVisible(demo, (v) => {
      visible = v;
      if (!v) { if (started) pause(); return; }
      if (!started) { started = true; start(0, false); } else resume();
    });
    reduceMotion.addEventListener("change", () => start(idx, false));
    render(motionOK() ? 0 : 5);
    void tabs;
  }

  /* ---------- Multilingual switcher ---------- */
  const LANGS = {
    de: { q: "„Unser neues Werk in Bremen nimmt im vierten Quartal den Betrieb auf.“", url: "acme.example/de/werke" },
    en: { q: "“Our new Bremen facility will begin operations in the fourth quarter.”", url: "acme.example/en/sites" },
    fr: { q: "« Notre nouveau site de Brême entrera en service au quatrième trimestre. »", url: "acme.example/fr/implantations" },
    it: { q: "«Il nostro nuovo stabilimento di Brema entrerà in funzione nel quarto trimestre.»", url: "acme.example/it/sedi" },
    es: { q: "«Nuestra nueva planta de Bremen comenzará a operar en el cuarto trimestre.»", url: "acme.example/es/centros" },
    nl: { q: "“Onze nieuwe vestiging in Bremen gaat in het vierde kwartaal van start.”", url: "acme.example/nl/vestigingen" },
  };
  const langBox = $("[data-langs]");
  if (langBox) {
    const q = $("[data-lang-quote]", langBox);
    const src = $("[data-lang-src]", langBox);
    const json = $("[data-lang-json]", langBox);
    const list = $('[role="tablist"]', langBox);
    initTabs(list, (tab) => {
      const code = tab.dataset.lang, d = LANGS[code];
      q.textContent = d.q; q.lang = code;
      src.textContent = "Source · " + d.url;
      json.innerHTML = highlight(JSON.stringify({
        event_type: "facility_opening",
        company: "Acme Example Industries",
        location: "Bremen, DE",
        evidence: { language: code, source_url: "https://" + d.url },
        verified: true,
      }, null, 2));
      if (motionOK()) [q, json].forEach((el) => { el.classList.remove("anim-in"); void el.offsetWidth; el.classList.add("anim-in"); });
    });
  }

  /* ---------- Event anatomy: link fields to JSON lines ---------- */
  const anatomy = $("[data-anatomy]");
  if (anatomy) {
    const lines = $$(".ln", anatomy);
    const fields = $$(".field", anatomy);
    const activate = (f) => {
      fields.forEach((x) => { x.classList.toggle("is-on", x === f); x.setAttribute("aria-pressed", String(x === f)); });
      const [a, b] = f.dataset.lines.split("-").map(Number);
      lines.forEach((l, i) => l.classList.toggle("is-on", i + 1 >= a && i + 1 <= (b || a)));
    };
    fields.forEach((f) => {
      f.addEventListener("mouseenter", () => activate(f));
      f.addEventListener("focus", () => activate(f));
      f.addEventListener("click", () => activate(f));
    });
    if (fields[0]) activate(fields[0]);
  }

  /* ---------- Footer year ---------- */
  $$("[data-year]").forEach((el) => { el.textContent = new Date().getFullYear(); });
})();
