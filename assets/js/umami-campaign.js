// Copied unchanged from logicalknight/growth-desk deploy/website/umami-campaign.js (tested there).
// Growth Desk: let only approved, non-sensitive campaign codes reach Umami (docs/ANALYTICS.md).
//
// Use with the pinned Umami v3.4.0 tracker's documented hooks, this file loaded first:
//   <script defer src="/js/umami-campaign.js" data-utm-campaign="spring-pilot,ippc-demo"
//           data-utm-source="linkedin,newsletter" data-utm-medium="social,email"></script>
//   <script defer src="https://stats.example.com/script.js" data-website-id="..." data-exclude-search="true"
//           data-exclude-hash="true" data-before-send="gdUmamiBeforeSend"></script>
//
// data-exclude-search strips the whole query first (so nothing leaks if this file fails to load). This hook then
// writes back at most one value for each of utm_source / utm_medium / utm_campaign, and only a value listed on this
// tag (1-40 characters of a-z 0-9 - _). Everything else in the address (e-mails, tokens, other parameters, free
// text, form contents) is never sent. The same campaign list goes into Growth Desk's UMAMI_CAMPAIGN_CODES.
(function () {
  "use strict";
  var me = document.currentScript;
  var CODE = /^[a-z0-9][a-z0-9_-]{0,39}$/;
  var FIELDS = ["utm_source", "utm_medium", "utm_campaign"];
  var allow = {};
  FIELDS.forEach(function (f) {
    var raw = (me && me.getAttribute("data-" + f.replace("_", "-"))) || "";
    allow[f] = raw.split(",").map(function (v) { return v.trim(); }).filter(function (v) { return CODE.test(v); });
  });

  function approvedQuery(search) {
    var params = new URLSearchParams(search);
    var out = new URLSearchParams();
    FIELDS.forEach(function (f) {
      var values = params.getAll(f);
      if (values.length === 1 && allow[f].indexOf(values[0]) !== -1) out.set(f, values[0]);
    });
    return out.toString();
  }

  function gdUmamiBeforeSend(type, payload) {
    if (!payload || typeof payload.url !== "string") return payload;
    try {
      var u = new URL(payload.url, location.href);
      u.search = approvedQuery(location.search); // always reset: only approved fields survive
      u.hash = "";
      payload.url = u.toString();
    } catch (e) {
      return null; // an address we cannot rewrite safely is not sent at all
    }
    return payload;
  }

  gdUmamiBeforeSend.approvedQuery = approvedQuery; // used by umami-campaign.check.mjs
  window.gdUmamiBeforeSend = gdUmamiBeforeSend;
})();
