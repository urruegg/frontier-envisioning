// Shared helpers for the DOM tests: load the built blueprint into happy-dom and drive it like a user.
import { Browser } from "happy-dom";
import fs from "node:fs";
import path from "node:path";

export const DEFAULT_HTML = path.join("build", "demo", "Frontier Company Blueprint - Template (Caldova sample).html");
export const PREVIEW_HTML = process.env.BLUEPRINT_PREVIEW_HTML || path.join("build", "demo-finops-preview", "Frontier Company Blueprint - Template (Caldova sample).html");
export const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
export const txt = (el) => ((el && el.textContent) || "").replace(/\s+/g, " ").trim();

export async function openBlueprint(file = process.env.BLUEPRINT_HTML || DEFAULT_HTML, options = {}) {
  if (!fs.existsSync(file)) throw new Error(`${file} not found - run: python tools/dev.py demo`);
  let html = fs.readFileSync(file, "utf8");
  if (options.change) html = html.replace(/(<script[^>]+id="bp-data"[^>]*>)([\s\S]*?)(<\/script>)/, (_, a, json, b) => {
    const data = JSON.parse(json);
    options.change(data);
    return a + JSON.stringify(data).replace(/</g, "\\u003c") + b;
  });
  const browser = new Browser({
    settings: {
      enableJavaScriptEvaluation: true,
      disableJavaScriptFileLoading: true,
      disableCSSFileLoading: true,
      suppressInsecureJavaScriptEnvironmentWarning: true
    }
  });
  const page = browser.newPage();
  page.url = "https://localhost/blueprint.html";
  const window = page.mainFrame.window;
  for (const [key, value] of Object.entries(options.storage || {})) window.localStorage.setItem(key, value);
  const errors = [];
  window.addEventListener("error", (e) => errors.push("window error: " + ((e.error && e.error.stack) || e.message)));
  window.console.error = (...a) => errors.push("console.error: " + a.map((x) => (x && x.stack) || String(x)).join(" "));
  window.matchMedia = window.matchMedia || (() => ({ matches: false, addEventListener() {}, removeEventListener() {} }));
  page.content = html;
  await page.waitUntilComplete();
  await wait(300);
  const doc = window.document;
  return {
    window,
    doc,
    errors,
    view: () => doc.getElementById("view"),
    go: async (hash) => {
      window.location.hash = hash;
      window.dispatchEvent(new window.HashChangeEvent("hashchange"));
      await wait(40);
    },
    click: async (el, ms = 30) => {
      el.dispatchEvent(new window.MouseEvent("click", { bubbles: true }));
      await wait(ms);
    },
    notes: () => {
      // workshop notes are kept in localStorage as one JSON object per blueprint
      const all = {};
      for (const key of Object.keys(window.localStorage)) {
        try {
          Object.assign(all, JSON.parse(window.localStorage.getItem(key) || "{}"));
        } catch {
          /* not a notes entry */
        }

      }
      return all;
    },
    close: async () => browser.close()
  };
}

export async function acknowledgePreview(bp) {
  const button = bp.doc.querySelector("#finops-preview-ack");
  if (!button) throw new Error("Missing explicit viewer acknowledgement");
  button.click();
  await wait(30);
}
