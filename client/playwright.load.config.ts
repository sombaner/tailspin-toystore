import { defineConfig, devices } from '@playwright/test';

// Load-test configuration: targets an external/base URL, no local dev server.
const workers = process.env.WORKERS ? parseInt(process.env.WORKERS, 10) : 16;
const baseURL = process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:4321';

export default defineConfig({
  testDir: './e2e-tests',
  testMatch: ['ui-load.spec.ts'],
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: 0,
  workers,
  reporter: 'list',
  use: {
    baseURL,
    trace: 'off',
    // Being explicit to avoid accidental headful mode on CI
    headless: true,
    channel: 'chrome',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  // Intentionally no webServer here; we are hitting a deployed/external endpoint.
});
