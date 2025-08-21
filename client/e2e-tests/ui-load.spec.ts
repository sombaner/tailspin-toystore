import { test, expect, type Page } from '@playwright/test';

// Simple UI load scenario: each worker will iterate multiple times navigating
// the home page, clicking a few game cards, and returning. Control duration
// by PLAYWRIGHT_ITERATIONS and concurrency by WORKERS env vars.
const iterations = parseInt(process.env.PLAYWRIGHT_ITERATIONS || '10', 10);
const vus = parseInt(process.env.PLAYWRIGHT_VUS || '8', 10);

async function exerciseFlow(page: Page, i: number, baseURL: string) {
  // Home
  await test.step(`visit home ${i}`, async () => {
    await page.goto('/');
    await expect(page.getByRole('heading', { name: 'Welcome to Tailspin Toys' })).toBeVisible({ timeout: 10000 });
  });

  // Click first featured game card link if present
  const firstCard = page.locator('main a').first();
  const hasCard = await firstCard.count();
  if (hasCard) {
    await test.step('open first game details', async () => {
      await firstCard.click();
      await expect(page).toHaveURL(/\/game\//, { timeout: 10000 });
      // Basic content check on game page
      await expect(page.locator('h1, h2, h3').first()).toBeVisible({ timeout: 10000 });
    });

    // Back to home
    await test.step('back to home', async () => {
      await page.goto('/');
      await expect(page.getByRole('heading', { name: 'Featured Games' })).toBeVisible({ timeout: 10000 });
    });
  }
}

test.describe.configure({ mode: 'parallel' });

for (let vu = 1; vu <= vus; vu++) {
  test(`ui load flow [vu ${vu}]`, async ({ page, baseURL }) => {
    test.info().annotations.push({ type: 'baseURL', description: baseURL || '' });
    for (let i = 1; i <= iterations; i++) {
      await exerciseFlow(page, i, baseURL || '');
    }
  });
}
