/** Google Analytics 4 (gtag.js), loaded only when VITE_GA_ID is set at build time,
 * and never when Do-Not-Track is on. track() is a no-op until init succeeds, so call
 * sites stay clean. Outbound link clicks are captured globally here. */

const GA_ID = import.meta.env.VITE_GA_ID as string | undefined;
let enabled = false;

declare global {
  interface Window {
    dataLayer?: unknown[];
    gtag?: (...args: unknown[]) => void;
  }
}

export function initAnalytics(): void {
  if (!GA_ID) return; // no tag configured (dev, or not yet provided)
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
  window.gtag("config", GA_ID);
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
