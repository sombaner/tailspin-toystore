import { test, expect } from '@playwright/test';

/**
 * UI + API Integration Tests
 * These tests validate that the UI correctly consumes and displays data from the API,
 * ensuring the full stack integration works as expected.
 */
test.describe('UI + API Integration', () => {
  test('should load home page and display games from API', async ({ page }) => {
    await page.goto('/');
    
    // Verify page loads successfully
    await expect(page).toHaveTitle('Tailspin Toys - Crowdfunding your new favorite game!');
    
    // Check main heading - use more specific selector to avoid multiple h1 elements
    await expect(page.getByRole('heading', { name: 'Welcome to Tailspin Toys' })).toBeVisible();
    
    // Wait for games to load from API (this tests the middleware integration)
    await page.waitForSelector('[data-testid="games-grid"]', { timeout: 10000 });
    
    // Verify games are displayed
    const gameCards = page.locator('[data-testid="game-card"]');
    await expect(gameCards.first()).toBeVisible();
    
    // Verify we have multiple games
    const gameCount = await gameCards.count();
    expect(gameCount).toBeGreaterThan(0);
    
    // Test that each game card displays API data correctly
    const firstGame = gameCards.first();
    await expect(firstGame.locator('[data-testid="game-title"]')).toBeVisible();
    
    // Verify game title is not empty (comes from API)
    const gameTitle = await firstGame.locator('[data-testid="game-title"]').textContent();
    expect(gameTitle?.trim()).toBeTruthy();
    
    // Verify the game has required data attributes (used for navigation)
    const gameId = await firstGame.getAttribute('data-game-id');
    expect(gameId).toBeTruthy();
    expect(Number(gameId)).toBeGreaterThan(0);
  });

  test('should navigate from home to game details with API data', async ({ page }) => {
    await page.goto('/');
    
    // Wait for games to load
    await page.waitForSelector('[data-testid="games-grid"]', { timeout: 10000 });
    
    // Get first game info
    const firstGame = page.locator('[data-testid="game-card"]').first();
    const gameId = await firstGame.getAttribute('data-game-id');
    const gameTitle = await firstGame.getAttribute('data-game-title');
    
    // Click on the game to navigate to details
    await firstGame.click();
    
    // Verify we're on the correct game details page
    await expect(page).toHaveURL(`/game/${gameId}`);
    
    // Wait for game details to load from API
    await page.waitForSelector('[data-testid="game-details"]', { timeout: 10000 });
    
    // Verify the game details are loaded from API
    const detailsTitle = page.locator('[data-testid="game-details-title"]');
    await expect(detailsTitle).toBeVisible();
    await expect(detailsTitle).toHaveText(gameTitle || '');
    
    // Verify other API data is displayed
    await expect(page.locator('[data-testid="game-details-description"]')).toBeVisible();
    
    // Check that publisher or category information is shown (from API)
    const publisherExists = await page.locator('[data-testid="game-details-publisher"]').isVisible();
    const categoryExists = await page.locator('[data-testid="game-details-category"]').isVisible();
    expect(publisherExists || categoryExists).toBeTruthy();
  });

  test('should handle direct game details page load from API', async ({ page }) => {
    // Navigate directly to a game details page (tests API integration)
    await page.goto('/game/1');
    
    // Wait for game details to load
    await page.waitForSelector('[data-testid="game-details"]', { timeout: 10000 });
    
    // Verify title is loaded from API
    const gameTitle = page.locator('[data-testid="game-details-title"]');
    await expect(gameTitle).toBeVisible();
    const titleText = await gameTitle.textContent();
    expect(titleText?.trim()).toBeTruthy();
    
    // Verify description is loaded from API
    const gameDescription = page.locator('[data-testid="game-details-description"]');
    await expect(gameDescription).toBeVisible();
    const descriptionText = await gameDescription.textContent();
    expect(descriptionText?.trim()).toBeTruthy();
    
    // Verify action button is present
    const backButton = page.locator('[data-testid="back-game-button"]');
    await expect(backButton).toBeVisible();
    await expect(backButton).toContainText('Support This Game');
  });

  test('should navigate back to home from game details', async ({ page }) => {
    await page.goto('/game/1');
    
    // Wait for page to load
    await page.waitForSelector('[data-testid="game-details"]', { timeout: 10000 });
    
    // Find and click back link
    const backLink = page.locator('a:has-text("Back to all games")');
    await expect(backLink).toBeVisible();
    await backLink.click();
    
    // Verify we're back on home page
    await expect(page).toHaveURL('/');
    
    // Verify games are loaded again
    await page.waitForSelector('[data-testid="games-grid"]', { timeout: 10000 });
    await expect(page.locator('[data-testid="game-card"]').first()).toBeVisible();
  });

  test('should handle non-existent game gracefully (UI + API error handling)', async ({ page }) => {
    // Navigate to a non-existent game
    await page.goto('/game/99999');
    
    // Page should load without crashing
    await page.waitForTimeout(3000);
    
    // The page should handle the API 404 gracefully
    await expect(page).toHaveTitle(/Game Details - Tailspin Toys/);
    
    // The page should not crash and should potentially show an error or empty state
    // (This tests that the UI handles API errors appropriately)
  });

  test('should maintain consistent data between home and details pages', async ({ page }) => {
    await page.goto('/');
    
    // Wait for games to load
    await page.waitForSelector('[data-testid="games-grid"]', { timeout: 10000 });
    
    // Get game data from home page
    const firstGame = page.locator('[data-testid="game-card"]').first();
    const gameId = await firstGame.getAttribute('data-game-id');
    const homePageTitle = await firstGame.locator('[data-testid="game-title"]').textContent();
    
    // Navigate to details
    await firstGame.click();
    await page.waitForSelector('[data-testid="game-details"]', { timeout: 10000 });
    
    // Get title from details page
    const detailsPageTitle = await page.locator('[data-testid="game-details-title"]').textContent();
    
    // Verify data consistency between pages (both sourced from same API)
    expect(homePageTitle?.trim()).toBe(detailsPageTitle?.trim());
  });

  test('should display featured games section with API data', async ({ page }) => {
    await page.goto('/');
    
    // Look for featured games section
    const featuredHeading = page.getByRole('heading', { name: 'Featured Games' });
    if (await featuredHeading.isVisible()) {
      // If featured games exist, verify they display API data
      await page.waitForSelector('[data-testid="games-grid"]', { timeout: 10000 });
      
      const gameCards = page.locator('[data-testid="game-card"]');
      const gameCount = await gameCards.count();
      expect(gameCount).toBeGreaterThan(0);
      
      // Verify each featured game has proper data from API
      for (let i = 0; i < Math.min(3, gameCount); i++) {
        const game = gameCards.nth(i);
        const title = await game.locator('[data-testid="game-title"]').textContent();
        expect(title?.trim()).toBeTruthy();
      }
    }
  });
});