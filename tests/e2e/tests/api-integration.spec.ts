import { test, expect } from '@playwright/test';

/**
 * API Integration Tests
 * These tests validate that the API endpoints are working correctly
 * and returning expected data structures.
 */
test.describe('API Integration', () => {
  const API_BASE_URL = 'http://localhost:5100';

  test('should have API server running and responsive', async ({ request }) => {
    // Test that the Flask API server is accessible
    const response = await request.get(`${API_BASE_URL}/api/games`);
    expect(response.status()).toBe(200);
    
    const games = await response.json();
    expect(Array.isArray(games)).toBeTruthy();
  });

  test('should return games with correct structure', async ({ request }) => {
    const response = await request.get(`${API_BASE_URL}/api/games`);
    expect(response.status()).toBe(200);
    
    const games = await response.json();
    expect(games.length).toBeGreaterThan(0);
    
    // Validate the structure of game objects
    const firstGame = games[0];
    expect(firstGame).toHaveProperty('id');
    expect(firstGame).toHaveProperty('title');
    expect(firstGame).toHaveProperty('description');
    expect(firstGame).toHaveProperty('publisher');
    expect(firstGame).toHaveProperty('category');
    expect(firstGame).toHaveProperty('starRating');
    
    // Validate data types
    expect(typeof firstGame.id).toBe('number');
    expect(typeof firstGame.title).toBe('string');
    expect(typeof firstGame.description).toBe('string');
    expect(typeof firstGame.starRating).toBe('number');
    
    // Validate that title and description are not empty
    expect(firstGame.title.trim()).toBeTruthy();
    expect(firstGame.description.trim()).toBeTruthy();
  });

  test('should return individual game by ID', async ({ request }) => {
    // First get all games to get a valid ID
    const gamesResponse = await request.get(`${API_BASE_URL}/api/games`);
    const games = await gamesResponse.json();
    
    if (games.length > 0) {
      const gameId = games[0].id;
      
      // Test getting individual game
      const gameResponse = await request.get(`${API_BASE_URL}/api/games/${gameId}`);
      expect(gameResponse.status()).toBe(200);
      
      const game = await gameResponse.json();
      expect(game.id).toBe(gameId);
      expect(game).toHaveProperty('title');
      expect(game).toHaveProperty('description');
    }
  });

  test('should handle non-existent game gracefully', async ({ request }) => {
    const response = await request.get(`${API_BASE_URL}/api/games/99999`);
    expect(response.status()).toBe(404);
    
    const error = await response.json();
    expect(error).toHaveProperty('error');
    expect(error.error).toBe('Game not found');
  });

  test('should handle API server being available via middleware', async ({ page }) => {
    // Test that the Astro middleware correctly forwards API requests
    const response = await page.request.get('/api/games');
    expect(response.status()).toBe(200);
    
    const games = await response.json();
    expect(Array.isArray(games)).toBeTruthy();
  });
});