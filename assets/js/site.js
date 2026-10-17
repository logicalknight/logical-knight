/* Logical Knight company site: mobile menu, gentle scroll reveals, and the contact form that prepares an e-mail.
   No tracking, no storage, no network requests. Every page works without this file. */
(() => {
  "use strict";

  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));

  /* ---------- Header ---------- */
  const header = $(".site-header");
  const toggle = $(".nav-toggle");
  const nav = $("#site-nav");
  if (header) {
    const onScroll = () => header.classList.toggle("is-scrolled", window.scrollY > 8);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }
  if (header && toggle && nav) {
    const setOpen = (open) => {
      header.classList.toggle("is-open", open);
      toggle.setAttribute("aria-expanded", String(open));
      if (open) nav.querySelector("a")?.focus();
    };
    toggle.addEventListener("click", () => setOpen(toggle.getAttribute("aria-expanded") !== "true"));
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && header.classList.contains("is-open")) { setOpen(false); toggle.focus(); }
    });
    window.matchMedia("(min-width: 960px)").addEventListener("change", (e) => { if (e.matches) setOpen(false); });
  }

  /* ---------- Reveal on scroll: only what starts below the fold is hidden, so nothing depends on it ---------- */
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!reduce && "IntersectionObserver" in window) {
    const io = new IntersectionObserver((entries) => entries.forEach((en) => {
      if (!en.isIntersecting) return;
      en.target.classList.remove("is-pending");
      io.unobserve(en.target);
    }), { rootMargin: "0px 0px -6% 0px", threshold: 0.06 });
    $$("[data-reveal]").forEach((el) => {
      if (el.getBoundingClientRect().top > window.innerHeight) { el.classList.add("is-pending"); io.observe(el); }
    });
  }

  /* ---------- Contact: prepare an e-mail in the visitor's own mail app; nothing is sent from the page ---------- */
  const form = $("form.compose");
  if (form) {
    const d = form.dataset;
    const error = $(".field__error", form);
    const sent = $(".compose__sent", form);
    const problem = form.elements.problem;
    form.addEventListener("submit", (ev) => {
      ev.preventDefault();
      const v = (name) => (form.elements[name].value || "").trim();
      if (!v("problem")) {
        problem.setAttribute("aria-invalid", "true");
        error.textContent = document.documentElement.lang === "de"
          ? "Bitte beschreiben Sie kurz, was Ihnen im Weg steht."
          : "Please describe briefly what is getting in the way.";
        error.hidden = false;
        problem.focus();
        return;
      }
      problem.removeAttribute("aria-invalid");
      error.hidden = true;
      const who = [v("name"), v("company")].filter(Boolean).join(", ");
      const subject = who ? `${d.subject} ${d.subjectFrom} ${who}` : d.subject;
      const lines = [];
      if (v("name")) lines.push(`${d.labelName}: ${v("name")}`);
      if (v("company")) lines.push(`${d.labelCompany}: ${v("company")}`);
      lines.push("", `${d.labelProblem}:`, v("problem"));
      if (v("today")) lines.push("", `${d.labelToday}:`, v("today"));
      const href = `mailto:${d.to}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(lines.join("\n"))}`;
      sent.hidden = false;
      window.location.href = href;
    });
  }

  /* ---------- Footer year ---------- */
  $$("[data-year]").forEach((el) => { el.textContent = String(new Date().getFullYear()); });
})();
