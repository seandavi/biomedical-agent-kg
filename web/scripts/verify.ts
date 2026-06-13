/** Headless smoke test: load the dev server, assert the graph renders. */
import { mkdirSync } from "node:fs";
import { chromium } from "playwright-core";

mkdirSync("shots", { recursive: true });

const URL = process.env.URL ?? "http://localhost:5173/";
const exe =
  process.env.CHROMIUM ??
  `${process.env.HOME}/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome`;

const browser = await chromium.launch({ executablePath: exe, headless: true });
const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });

const errors: string[] = [];
page.on("console", (m) => {
  if (m.type() === "error") errors.push(m.text());
});
page.on("pageerror", (e) => errors.push(`pageerror: ${e.message}`));

await page.goto(URL, { waitUntil: "networkidle" });
await page.waitForTimeout(1500); // let fcose settle

const counts = await page.evaluate(() => {
  const cyEl = document.querySelector("#graph canvas");
  const stats = document.getElementById("stats")?.textContent ?? "";
  const typeChips = document.querySelectorAll("#type-filters .chip").length;
  const facetChips = document.querySelectorAll("#facet-filters .chip").length;
  return { hasCanvas: !!cyEl, stats, typeChips, facetChips };
});

// Tap the first agent node via the exposed cy handle, then assert the panel fills.
const panel = await page.evaluate(() => {
  const cy = (window as unknown as { cy: any }).cy;
  const agent = cy.nodes('[type = "agent"]').first();
  if (agent.empty()) return { tapped: false, title: "", id: "" };
  agent.emit("tap");
  const title = document.querySelector("#panel h2")?.textContent ?? "";
  const id = document.querySelector("#panel .node-id")?.textContent ?? "";
  return { tapped: true, title, id };
});

await page.screenshot({ path: "shots/verify-graph.png" });

console.log(JSON.stringify({ counts, panel, errors }, null, 2));
await browser.close();

const fail = (msg: string) => {
  console.error(`FAIL: ${msg}`);
  process.exit(1);
};
if (!counts.hasCanvas) fail("no graph canvas rendered");
if (counts.typeChips === 0) fail("no type-filter chips built");
if (!panel.tapped || !panel.title) fail("detail panel did not populate on node tap");
if (errors.length) fail("console errors present");
console.log("OK: graph rendered, panel works, no console errors");
