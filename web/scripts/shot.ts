/**
 * Design-loop screenshotter: capture the app in several states/viewports so we
 * can critique real renders. Output -> shots/<label>.png. Reports console errors.
 *
 *   bun run scripts/shot.ts [tag]      # tag prefixes filenames (e.g. "v2")
 */
import { mkdirSync } from "node:fs";
import { chromium } from "playwright-core";

const URL = process.env.URL ?? "http://localhost:5173/";
const exe =
  process.env.CHROMIUM ??
  `${process.env.HOME}/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome`;
const tag = process.argv[2] ? `${process.argv[2]}-` : "";

mkdirSync("shots", { recursive: true });

const browser = await chromium.launch({ executablePath: exe, headless: true });
const errors: string[] = [];

async function capture(
  label: string,
  width: number,
  height: number,
  prep?: (page: import("playwright-core").Page) => Promise<void>,
) {
  const page = await browser.newPage({ viewport: { width, height } });
  page.on("console", (m) => m.type() === "error" && errors.push(`[${label}] ${m.text()}`));
  page.on("pageerror", (e) => errors.push(`[${label}] pageerror: ${e.message}`));
  await page.goto(URL, { waitUntil: "networkidle" });
  await page.waitForTimeout(1600); // let fcose settle
  if (prep) await prep(page);
  await page.waitForTimeout(500);
  await page.screenshot({ path: `shots/${tag}${label}.png` });
  await page.close();
}

const selectAgent = async (page: import("playwright-core").Page) => {
  await page.evaluate(() => {
    const cy = (window as unknown as { cy: any }).cy;
    cy.nodes('[type = "agent"]').first().emit("tap");
  });
};

const enableCites = async (page: import("playwright-core").Page) => {
  await page.click("#cites-toggle").catch(() => {});
};

await capture("01-default", 1400, 900);
await capture("02-selected", 1400, 900, selectAgent);
await capture("03-cites", 1400, 900, enableCites);
await capture("04-narrow", 760, 1000);
await capture("05-narrow-drawer", 760, 1000, async (page) => {
  await page.click("#menu-btn").catch(() => {});
});

await browser.close();
console.log(JSON.stringify({ errors }, null, 2));
console.log(errors.length ? "DONE (with console errors)" : "DONE clean");
