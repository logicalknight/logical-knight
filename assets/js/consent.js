/* Logical Knight: opt-in website analytics (Datenschutz section 3a).
   Nothing analytics-related happens before the visitor chooses "Allow": the Umami tracker is not requested, no
   device attribute is read for it and no event is sent. Ignoring or rejecting the notice leaves analytics off.
   The choice is stored only on this site (logicalknight.com, this browser): localStorage "lk-analytics-consent" =
   "1|allow|YYYY-MM-DD" or "1|reject|YYYY-MM-DD" (version|choice|date), asked again after 365 days or when the version
   changes. No identifier is created. "Privacy settings" in the footer changes or withdraws the choice at any time;
   after withdrawal every further event is dropped (also in other open tabs), and the tracker is not loaded again. */
(() => {
  "use strict";
  const me = document.currentScript;
  if (!me) return;
  const KEY = "lk-analytics-consent";
  const VERSION = "1";
  const MAX_AGE_DAYS = 365;
  const de = (document.documentElement.lang || "en").startsWith("de");
  const T = de ? {
    title: "Optionale Reichweitenmessung",
    text: "Dürfen wir anonym messen, welche Seiten gelesen werden? Dafür nutzen wir Umami auf unserem eigenen Server in Deutschland, ohne Cookies und ohne Werbung. Ohne Ihre Zustimmung wird nichts gemessen; die Website funktioniert genauso.",
    allow: "Messung erlauben", reject: "Ablehnen", more: "Mehr dazu in der Datenschutzerklärung",
    now: (c) => c === "allow" ? "Aktuell: Messung erlaubt." : c === "reject" ? "Aktuell: Messung abgelehnt." : "Aktuell: keine Auswahl, also keine Messung.",
    saved: (c) => c === "allow" ? "Gespeichert: Messung erlaubt." : "Gespeichert: Messung abgelehnt.",
    privacy: "/datenschutz/#reichweitenmessung",
  } : {
    title: "Optional reach measurement",
    text: "May we measure anonymously which pages are read? We use Umami on our own server in Germany, without cookies and without advertising. Without your consent nothing is measured; the website works the same.",
    allow: "Allow analytics", reject: "Reject analytics", more: "More in the privacy policy",
    now: (c) => c === "allow" ? "Currently: analytics allowed." : c === "reject" ? "Currently: analytics rejected." : "Currently: no choice made, so no analytics.",
    saved: (c) => c === "allow" ? "Saved: analytics allowed." : "Saved: analytics rejected.",
    privacy: "/datenschutz/#reach",
  };

  function read() {
    let raw = null;
    try { raw = window.localStorage.getItem(KEY); } catch (e) { return null; }
    const m = /^(\d+)\|(allow|reject)\|(\d{4}-\d{2}-\d{2})$/.exec(raw || "");
    if (!m || m[1] !== VERSION) return null;
    const age = (Date.now() - Date.parse(m[3] + "T00:00:00Z")) / 86400000;
    return age >= 0 && age <= MAX_AGE_DAYS ? m[2] : null;
  }
  function write(choice) {
    try { window.localStorage.setItem(KEY, [VERSION, choice, new Date().toISOString().slice(0, 10)].join("|")); }
    catch (e) { /* storage blocked: the choice applies to this page only */ }
  }

  // Every event passes here first: no consent (now, or withdrawn in any tab) -> nothing is sent.
  let current = read();
  window.gdConsentBeforeSend = function (type, payload) {
    if (read() !== "allow" && current !== "allow") return null;
    if (read() === "reject") return null;
    return typeof window.gdUmamiBeforeSend === "function" ? window.gdUmamiBeforeSend(type, payload) : null;
  };

  let loaded = false;
  function load() {
    if (loaded) return;
    loaded = true;
    const hook = document.createElement("script");
    hook.src = "/assets/js/umami-campaign.js";
    for (const f of ["utm-source", "utm-medium", "utm-campaign"]) {
      const v = me.getAttribute("data-" + f);
      if (v) hook.setAttribute("data-" + f, v);
    }
    hook.onload = () => {
      const s = document.createElement("script");
      s.src = me.getAttribute("data-umami-src");
      s.defer = true;
      const attrs = { "website-id": me.getAttribute("data-website-id"), "domains": me.getAttribute("data-domains"),
        "do-not-track": "true", "exclude-search": "true", "exclude-hash": "true", "before-send": "gdConsentBeforeSend" };
      for (const k in attrs) s.setAttribute("data-" + k, attrs[k]);
      document.head.appendChild(s);
    };
    document.head.appendChild(hook);
  }

  // The notice: a labelled region (not a modal), two equal buttons, nothing preselected.
  let panel = null;
  function show(focus) {
    if (!panel) {
      panel = document.createElement("section");
      panel.className = "consent";
      panel.setAttribute("aria-labelledby", "consent-title");
      panel.innerHTML = '<div class="consent__inner"><h2 id="consent-title" class="consent__title" tabindex="-1"></h2>' +
        '<p class="consent__text"></p><p class="consent__state" role="status"></p><div class="consent__actions">' +
        '<button type="button" class="btn btn--secondary" data-choice="allow"></button>' +
        '<button type="button" class="btn btn--secondary" data-choice="reject"></button></div>' +
        '<p class="consent__more"><a></a></p></div>';
      panel.querySelector(".consent__title").textContent = T.title;
      panel.querySelector(".consent__text").textContent = T.text;
      panel.querySelector('[data-choice="allow"]').textContent = T.allow;
      panel.querySelector('[data-choice="reject"]').textContent = T.reject;
      const a = panel.querySelector(".consent__more a");
      a.textContent = T.more;
      a.href = T.privacy;
      panel.addEventListener("click", (e) => {
        const b = e.target.closest("button[data-choice]");
        if (!b) return;
        decide(b.getAttribute("data-choice"));
      });
      document.body.appendChild(panel);
    }
    panel.querySelector(".consent__state").textContent = T.now(current);
    panel.hidden = false;
    if (focus) panel.querySelector(".consent__title").focus();
  }
  function decide(choice) {
    current = choice;
    write(choice);
    const state = panel && panel.querySelector(".consent__state");
    if (state) state.textContent = T.saved(choice);
    if (choice === "allow") load();
    window.setTimeout(() => { if (panel) panel.hidden = true; }, 1200);
  }

  window.addEventListener("storage", (e) => {   // a choice made in another tab of this site applies here too
    if (e.key !== KEY) return;
    current = read();
    if (current === "allow") load();
  });
  document.addEventListener("click", (e) => {
    const b = e.target.closest("[data-privacy-settings]");
    if (!b) return;
    e.preventDefault();
    show(true);
  });

  if (current === "allow") load();
  else if (current === null) show(false);
})();
