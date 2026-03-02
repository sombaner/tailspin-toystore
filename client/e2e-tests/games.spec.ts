import { test, expect } from '@playwright/test';

test.describe('Game Listing and Navigation', () => {
  test('should display games with titles on index page', async ({ page }) => {
    await page.goto('/');
    
    // Wait for the games to load
    await page.waitForSelector('[data-testid="games-grid"]', { timeout: 10000 });
    
    // Check that games are displayed
    const gameCards = page.locator('[data-testid="game-card"]');
    
    // Wait for at least one game card to be visible
    await expect(gameCards.first()).toBeVisible();
    
    // Check that we have at least one game
    const gameCount = await gameCards.count();
    expect(gameCount).toBeGreaterThan(0);
    
    // Check that each game card has a title
    const firstGameCard = gameCards.first();
    await expect(firstGameCard.locator('[data-testid="game-title"]')).toBeVisible();
    
    // Verify that game titles are not empty
    const gameTitle = await firstGameCard.locator('[data-testid="game-title"]').textContent();
    expect(gameTitle?.trim()).toBeTruthy();
  });

  test('should navigate to correct game details page when clicking on a game', async ({ page }) => {
    await page.goto('/');
    
    // Wait for games to load
    await page.waitForSelector('[data-testid="games-grid"]', { timeout: 10000 });
    
    // Get the first game card and its data attributes
    const firstGameCard = page.locator('[data-testid="game-card"]').first();
    const gameId = await firstGameCard.getAttribute('data-game-id');
    const gameTitle = await firstGameCard.getAttribute('data-game-title');
    
    // Click on the first game
    await firstGameCard.click();
    
    // Verify we're on the correct game details page
    await expect(page).toHaveURL(`/game/${gameId}`);
    
    // Verify the game details page loads
    await page.waitForSelector('[data-testid="game-details"]', { timeout: 10000 });
    
    // Verify the title matches what we clicked on
    const detailsTitle = page.locator('[data-testid="game-details-title"]');
    await expect(detailsTitle).toHaveText(gameTitle || '');
  });

  test('should display game details with all required information', async ({ page }) => {
    // Navigate to a specific game (we'll use game ID 1 as an example)
    await page.goto('/game/1');
    
    // Wait for game details to load
    await page.waitForSelector('[data-testid="game-details"]', { timeout: 10000 });
    
    // Check that the game title is present and not empty
    const gameTitle = page.locator('[data-testid="game-details-title"]');
    await expect(gameTitle).toBeVisible();
    const titleText = await gameTitle.textContent();
    expect(titleText?.trim()).toBeTruthy();
    
    // Check that the game description is present and not empty
    const gameDescription = page.locator('[data-testid="game-details-description"]');
    await expect(gameDescription).toBeVisible();
    const descriptionText = await gameDescription.textContent();
    expect(descriptionText?.trim()).toBeTruthy();
    
    // Check that either publisher or category (or both) are present
    const publisherExists = await page.locator('[data-testid="game-details-publisher"]').isVisible();
    const categoryExists = await page.locator('[data-testid="game-details-category"]').isVisible();
    expect(publisherExists && categoryExists).toBeTruthy();
    
    // If publisher exists, check it has content
    if (publisherExists) {
      const publisherText = await page.locator('[data-testid="game-details-publisher"]').textContent();
      expect(publisherText?.trim()).toBeTruthy();
    }
    
    // If category exists, check it has content
    if (categoryExists) {
      const categoryText = await page.locator('[data-testid="game-details-category"]').textContent();
      expect(categoryText?.trim()).toBeTruthy();
    }
  });

  test('should display a button to back the game', async ({ page }) => {
    await page.goto('/game/1');
    
    // Wait for game details to load
    await page.waitForSelector('[data-testid="game-details"]', { timeout: 10000 });
    
    // Check that the back game button is present
    const backButton = page.locator('[data-testid="back-game-button"]');
    await expect(backButton).toBeVisible();
    await expect(backButton).toContainText('Support This Game');
    
    // Verify the button is clickable
    await expect(backButton).toBeEnabled();
  });

  test('should be able to navigate back to home from game details', async ({ page }) => {
    await page.goto('/game/1');
    
    // Wait for the page to load
    await page.waitForSelector('[data-testid="game-details"]', { timeout: 10000 });
    
    // Find and click the back to all games link
    const backLink = page.locator('a:has-text("Back to all games")');
    await expect(backLink).toBeVisible();
    await backLink.click();
    
    // Verify we're back on the home page
    await expect(page).toHaveURL('/');
    await page.waitForSelector('[data-testid="games-grid"]', { timeout: 10000 });
  });

  test('should handle navigation to non-existent game gracefully', async ({ page }) => {
    // Navigate to a game that doesn't exist
    await page.goto('/game/99999');
    
    // The page should load without crashing
    // Check if there's an error message or if it handles gracefully
    await page.waitForTimeout(3000);
    
    // The page should either show an error or handle it gracefully
    // We expect the page to not crash and still have a valid title
    await expect(page).toHaveTitle(/Game Details - Tailspin Toys/);
  });

  test('should display search input and filter games', async ({ page }) => {
    await page.goto('/');
    
    // Wait for the games to load
    await page.waitForSelector('[data-testid="games-grid"]', { timeout: 10000 });
    
    // Check that the search input is visible
    const searchInput = page.locator('[data-testid="game-search-input"]');
    await expect(searchInput).toBeVisible();
    
    // Get the initial number of games
    const initialGameCount = await page.locator('[data-testid="game-card"]').count();
    expect(initialGameCount).toBeGreaterThan(0);
    
    // Type a search query that likely won't match any game
    await searchInput.fill('zzzznonexistent');
    
    // Wait for the debounced search to trigger and results to update
    await page.waitForTimeout(500);
    
    // Either no games-grid or zero game cards
    const gameCards = page.locator('[data-testid="game-card"]');
    const count = await gameCards.count();
    expect(count).toBe(0);
  });

  test('should show comment textbox when Support This Game is clicked', async ({ page }) => {
    await page.goto('/game/1');
    
    // Wait for game details to load
    await page.waitForSelector('[data-testid="game-details"]', { timeout: 10000 });
    
    // Verify comment section is not visible initially
    await expect(page.locator('[data-testid="support-comment-section"]')).not.toBeVisible();
    
    // Click the Support This Game button
    const backButton = page.locator('[data-testid="back-game-button"]');
    await backButton.click();
    
    // Verify the comment section is now visible
    const commentSection = page.locator('[data-testid="support-comment-section"]');
    await expect(commentSection).toBeVisible();
    
    // Verify the textarea is present and can accept input
    const commentInput = page.locator('[data-testid="support-comment-input"]');
    await expect(commentInput).toBeVisible();
    await commentInput.fill('This game looks amazing and supports a great cause!');
    await expect(commentInput).toHaveValue('This game looks amazing and supports a great cause!');
  });
});
