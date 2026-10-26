/* Old or short addresses (build_site.py REDIRECTS): go to the page in data-target and keep only the approved campaign
   codes, filtered by umami-campaign.js (loaded just before this file with the same list as the analytics tag). Any
   other query value, and the fragment, is dropped. Sends nothing. Without JavaScript the meta refresh still leads to
   the page, without the codes. */
(() => {
  "use strict";
  const target = document.currentScript?.getAttribute("data-target") || "";
  const filter = window.gdUmamiBeforeSend?.approvedQuery;
  if (!/^\/[a-z0-9/-]*$/.test(target) || target.startsWith("//") || !filter) return;
  const query = filter(location.search);
  location.replace(target + (query ? "?" + query : ""));
})();
