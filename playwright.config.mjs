// Browser tests against the showcase site, served with the same headers as Azure Static Web Apps
// (tools/serve_site.py), so a Content-Security-Policy violation fails the test.
import { defineConfig, devices } from "@playwright/test";

const PORT = Number(process.env.SITE_PORT || 4173);
const python = process.platform === "win32" ? "python" : "python3";

export default defineConfig({
  testDir: "tests/e2e",
  timeout: 60_000,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? [["list"], ["html", { open: "never" }]] : "list",
  use: {
    baseURL: `http://127.0.0.1:${PORT}`,
    trace: "retain-on-failure",
    screenshot: "only-on-failure"
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"], viewport: { width: 1440, height: 900 } } }],
  webServer: {
    command: `${python} tools/serve_site.py --port ${PORT}`,
    url: `http://127.0.0.1:${PORT}/index.html`,
    reuseExistingServer: !process.env.CI,
    timeout: 30_000
  }
});
