/** Google Analytics 4 (gtag.js), loaded only on the production host,
 * and never when Do-Not-Track is on. track() is a no-op until init succeeds, so call
 * sites stay clean. Outbound link clicks are captured globally here. */

const GA_ID = "G-KLLV1GCF4E";

function isProductionHost(): boolean {
  const h = location.hostname;
  if (!h || h === "localhost" || h === "127.0.0.1" || h === "[::1]") return false;
  if (/^\d+\.\d+\.\d+\.\d+$/.test(h) || h.includes(":")) return false;
  return !/\.(workers\.dev|netlify\.app|ts\.net)$/.test(h);
}
let enabled = false;

declare global {
  interface Window {
    dataLayer?: unknown[];
    gtag?: (...args: unknown[]) => void;
  }
}

export function initAnalytics(): void {
  if (!isProductionHost()) return; // dev / preview hosts never track
  try {
    const dnt = navigator.doNotTrack ?? (window as unknown as { doNotTrack?: string }).doNotTrack;
    if (dnt === "1" || dnt === "yes") return; // respect Do-Not-Track
  } catch {
    /* navigator unavailable — proceed */
  }

  const s = document.createElement("script");
  s.async = true;
  s.src = `https://www.googletagmanager.com/gtag/js?id=${GA_ID}`;
  document.head.appendChild(s);

  window.dataLayer = window.dataLayer ?? [];
  window.gtag = function gtag() {
    // gtag.js requires the raw arguments object pushed onto dataLayer
    window.dataLayer!.push(arguments);
  };
  window.gtag("js", new Date());
  window.gtag("config", GA_ID, { content_group: "biomed-agents" });
  enabled = true;

  // Outbound clicks: GitHub, repos, papers, OpenAlex, provenance + About links.
  document.addEventListener("click", (e) => {
    const a = (e.target as HTMLElement)?.closest?.("a[href]") as HTMLAnchorElement | null;
    const href = a?.getAttribute("href") ?? "";
    if (!/^https?:\/\//.test(href)) return;
    try {
      track("outbound_click", { url: href.slice(0, 100), host: new URL(href).host });
    } catch {
      /* malformed URL — skip */
    }
  });
}

export function track(name: string, params?: Record<string, unknown>): void {
  if (!enabled) return;
  window.gtag?.("event", name, params ?? {});
}
