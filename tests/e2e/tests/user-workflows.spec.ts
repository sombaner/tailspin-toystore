import { test, expect } from '@playwright/test';

/**
 * End-to-End User Workflows
 * These tests simulate complete user journeys through the application,
 * validating that all UI and API integrations work together seamlessly.
 */
test.describe('Complete User Workflows', () => {
  test('user browsing workflow: home -> game details -> back -> different game', async ({ page }) => {
    // Start at home page
    await page.goto('/');
    await expect(page).toHaveTitle('Tailspin Toys - Crowdfunding your new favorite game!');
    
    // Wait for games to load from API
    await page.waitForSelector('[data-testid="games-grid"]', { timeout: 10000 });
    
    // Get the first two games
    const gameCards = page.locator('[data-testid="game-card"]');
    const gameCount = await gameCards.count();
    expect(gameCount).toBeGreaterThanOrEqual(2); // Need at least 2 games for this test
    
    // Store first game info
    const firstGame = gameCards.first();
    const firstGameId = await firstGame.getAttribute('data-game-id');
    const firstGameTitle = await firstGame.locator('[data-testid="game-title"]').textContent();
    
    // Store second game info  
    const secondGame = gameCards.nth(1);
    const secondGameId = await secondGame.getAttribute('data-game-id');
    const secondGameTitle = await secondGame.locator('[data-testid="game-title"]').textContent();
    
    // Click first game
    await firstGame.click();
    await expect(page).toHaveURL(`/game/${firstGameId}`);
    await page.waitForSelector('[data-testid="game-details"]', { timeout: 10000 });
    
    // Verify first game details loaded correctly
    await expect(page.locator('[data-testid="game-details-title"]')).toHaveText(firstGameTitle || '');
    
    // Navigate back to home
    await page.locator('a:has-text("Back to all games")').click();
    await expect(page).toHaveURL('/');
    await page.waitForSelector('[data-testid="games-grid"]', { timeout: 10000 });
    
    // Click second game
    const secondGameReloaded = page.locator('[data-testid="game-card"]').nth(1);
    await secondGameReloaded.click();
    await expect(page).toHaveURL(`/game/${secondGameId}`);
    await page.waitForSelector('[data-testid="game-details"]', { timeout: 10000 });
    
    // Verify second game details loaded correctly
    await expect(page.locator('[data-testid="game-details-title"]')).toHaveText(secondGameTitle || '');
  });

  test('user exploration workflow: browse games and view multiple details', async ({ page }) => {
    await page.goto('/');
    
    // Wait for games to load
    await page.waitForSelector('[data-testid="games-grid"]', { timeout: 10000 });
    
    const gameCards = page.locator('[data-testid="game-card"]');
    const gameCount = await gameCards.count();
    const gamesToTest = Math.min(3, gameCount); // Test up to 3 games
    
    for (let i = 0; i < gamesToTest; i++) {
      // Go back to home if not first iteration
      if (i > 0) {
        await page.goto('/');
        await page.waitForSelector('[data-testid="games-grid"]', { timeout: 10000 });
      }
      
      // Get current game info
      const currentGame = page.locator('[data-testid="game-card"]').nth(i);
      const gameId = await currentGame.getAttribute('data-game-id');
      const gameTitle = await currentGame.locator('[data-testid="game-title"]').textContent();
      
      // Click on game
      await currentGame.click();
      await expect(page).toHaveURL(`/game/${gameId}`);
      
      // Wait for details to load
      await page.waitForSelector('[data-testid="game-details"]', { timeout: 10000 });
      
      // Verify details are correct
      await expect(page.locator('[data-testid="game-details-title"]')).toHaveText(gameTitle || '');
      await expect(page.locator('[data-testid="game-details-description"]')).toBeVisible();
      
      // Verify action button is present and functional
      const supportButton = page.locator('[data-testid="back-game-button"]');
      await expect(supportButton).toBeVisible();
      await expect(supportButton).toContainText('Support This Game');
    }
  });

  test('user navigation workflow: using browser navigation', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('[data-testid="games-grid"]', { timeout: 10000 });
    
    // Click on first game
    const firstGame = page.locator('[data-testid="game-card"]').first();
    const gameId = await firstGame.getAttribute('data-game-id');
    await firstGame.click();
    
    await expect(page).toHaveURL(`/game/${gameId}`);
    await page.waitForSelector('[data-testid="game-details"]', { timeout: 10000 });
    
    // Use browser back button
    await page.goBack();
    await expect(page).toHaveURL('/');
    await page.waitForSelector('[data-testid="games-grid"]', { timeout: 10000 });
    
    // Use browser forward button
    await page.goForward();
    await expect(page).toHaveURL(`/game/${gameId}`);
    await page.waitForSelector('[data-testid="game-details"]', { timeout: 10000 });
    
    // Direct navigation via URL
    await page.goto('/');
    await expect(page).toHaveURL('/');
    await page.waitForSelector('[data-testid="games-grid"]', { timeout: 10000 });
  });

  test('error handling workflow: graceful handling of edge cases', async ({ page }) => {
    // Test direct navigation to non-existent game
    await page.goto('/game/99999');
    
    // Should not crash, should handle gracefully
    await page.waitForTimeout(2000);
    await expect(page).toHaveTitle(/Game Details - Tailspin Toys/);
    
    // Try to navigate back to home from error state
    await page.goto('/');
    await page.waitForSelector('[data-testid="games-grid"]', { timeout: 10000 });
    
    // Verify home page still works after error
    const gameCards = page.locator('[data-testid="game-card"]');
    await expect(gameCards.first()).toBeVisible();
  });

  test('responsive layout workflow: page loads and functions properly', async ({ page }) => {
    await page.goto('/');
    
    // Check that the page is responsive and content is properly laid out
    await page.waitForSelector('[data-testid="games-grid"]', { timeout: 10000 });
    
    // Verify main navigation and layout elements - use more specific selectors
    await expect(page.getByRole('heading', { name: 'Welcome to Tailspin Toys' })).toBeVisible();
    await expect(page.locator('[data-testid="games-grid"]')).toBeVisible();
    
    // Test game interaction still works
    const firstGame = page.locator('[data-testid="game-card"]').first();
    await expect(firstGame).toBeVisible();
    
    const gameId = await firstGame.getAttribute('data-game-id');
    await firstGame.click();
    
    await expect(page).toHaveURL(`/game/${gameId}`);
    await page.waitForSelector('[data-testid="game-details"]', { timeout: 10000 });
    
    // Verify details page layout
    await expect(page.locator('[data-testid="game-details-title"]')).toBeVisible();
    await expect(page.locator('[data-testid="game-details-description"]')).toBeVisible();
  });

  test('performance workflow: pages load within reasonable time', async ({ page }) => {
    const startTime = Date.now();
    
    // Navigate to home page
    await page.goto('/');
    await page.waitForSelector('[data-testid="games-grid"]', { timeout: 10000 });
    
    const homeLoadTime = Date.now() - startTime;
    expect(homeLoadTime).toBeLessThan(10000); // Should load within 10 seconds
    
    // Navigate to game details
    const detailsStartTime = Date.now();
    const firstGame = page.locator('[data-testid="game-card"]').first();
    await firstGame.click();
    
    await page.waitForSelector('[data-testid="game-details"]', { timeout: 10000 });
    
    const detailsLoadTime = Date.now() - detailsStartTime;
    expect(detailsLoadTime).toBeLessThan(5000); // Details should load within 5 seconds
  });

  test('data consistency workflow: API data remains consistent across navigation', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('[data-testid="games-grid"]', { timeout: 10000 });
    
    // Collect all game data from home page
    const gameCards = page.locator('[data-testid="game-card"]');
    const gameCount = await gameCards.count();
    const homePageGameData = [];
    
    for (let i = 0; i < Math.min(3, gameCount); i++) {
      const game = gameCards.nth(i);
      const id = await game.getAttribute('data-game-id');
      const title = await game.locator('[data-testid="game-title"]').textContent();
      homePageGameData.push({ id, title });
    }
    
    // Visit each game's details page and verify data consistency
    for (const gameData of homePageGameData) {
      await page.goto(`/game/${gameData.id}`);
      await page.waitForSelector('[data-testid="game-details"]', { timeout: 10000 });
      
      const detailsTitle = await page.locator('[data-testid="game-details-title"]').textContent();
      expect(detailsTitle?.trim()).toBe(gameData.title?.trim());
    }
  });
});