import { test, expect, Page } from '@playwright/test';

const TEST_EMAIL = 'marco.rossi@email.it';
const TEST_PASSWORD = 'password123';

/**
 * Helper: logs in via the /it/login page and waits for navigation to complete.
 * After login, NextAuth stores session in httpOnly cookie.
 */
async function login(page: Page) {
  await page.goto('/it/login');
  await page.waitForLoadState('networkidle');

  await page.locator('input[type="email"]').fill(TEST_EMAIL);
  await page.locator('input[type="password"]').fill(TEST_PASSWORD);
  await page.locator('button[type="submit"]').click();

  await page.waitForURL('**/it/jobs', { timeout: 15000 });
}

// =========================================================================
// Test Group 1: Talents List Page (public, no auth)
// =========================================================================
test.describe('Talents List Page', () => {
  // -----------------------------------------------------------------------
  // Test 1: Page renders with public talents
  // -----------------------------------------------------------------------
  test('page renders with public talents', async ({ page }) => {
    await page.goto('/it/talenti');

    // Wait for the page heading to appear
    await expect(page.locator('h1')).toContainText('Scopri i Talenti', { timeout: 15000 });

    // Marco Rossi (public) should be visible
    await expect(page.getByText('Marco Rossi')).toBeVisible({ timeout: 10000 });

    // Andrea Conti (private, is_public=0) should NOT be visible
    await expect(page.getByText('Andrea Conti')).not.toBeVisible();

    // Verify at least 4 talent cards are visible (6 public users total, page_size=10)
    const talentCards = page.locator('[role="button"]');
    await expect(talentCards).toHaveCount(6, { timeout: 10000 });
  });

  // -----------------------------------------------------------------------
  // Test 2: Search talents by name
  // -----------------------------------------------------------------------
  test('search talents by name', async ({ page }) => {
    await page.goto('/it/talenti');
    await expect(page.locator('h1')).toContainText('Scopri i Talenti', { timeout: 15000 });

    // Wait for initial load
    await expect(page.getByText('Marco Rossi')).toBeVisible({ timeout: 10000 });

    // Type "Giulia" in the search input
    const searchInput = page.getByPlaceholder('Cerca per nome, ruolo o competenza...');
    await searchInput.fill('Giulia');

    // Wait for debounce (350ms) + API response
    await page.waitForTimeout(500);

    // Giulia Bianchi should be visible
    await expect(page.getByText('Giulia Bianchi')).toBeVisible({ timeout: 10000 });

    // Marco Rossi should NOT be visible (filtered out)
    await expect(page.getByText('Marco Rossi')).not.toBeVisible({ timeout: 5000 });
  });

  // -----------------------------------------------------------------------
  // Test 3: Filter by experience level
  // -----------------------------------------------------------------------
  test('filter by experience level', async ({ page }) => {
    await page.goto('/it/talenti');
    await expect(page.locator('h1')).toContainText('Scopri i Talenti', { timeout: 15000 });

    // Wait for initial load
    await expect(page.getByText('Marco Rossi')).toBeVisible({ timeout: 10000 });

    // Click "Senior" filter button
    await page.locator('button[aria-pressed]', { hasText: 'Senior' }).click();

    // Wait for API response
    await page.waitForTimeout(500);

    // Marco Rossi (senior) should be visible
    await expect(page.getByText('Marco Rossi')).toBeVisible({ timeout: 10000 });

    // Luca Ferrari (mid) should NOT be visible
    await expect(page.getByText('Luca Ferrari')).not.toBeVisible({ timeout: 5000 });
  });

  // -----------------------------------------------------------------------
  // Test 4: Filter by availability
  // -----------------------------------------------------------------------
  test('filter by availability', async ({ page }) => {
    await page.goto('/it/talenti');
    await expect(page.locator('h1')).toContainText('Scopri i Talenti', { timeout: 15000 });

    // Wait for initial load
    await expect(page.locator('[role="button"]').first()).toBeVisible({ timeout: 10000 });

    // Click "Disponibile" filter button
    await page.locator('button[aria-pressed]', { hasText: 'Disponibile' }).click();

    // Wait for API response
    await page.waitForTimeout(500);

    // Talent cards should still be shown (all seed public users are available)
    const talentCards = page.locator('[role="button"]');
    const count = await talentCards.count();
    expect(count).toBeGreaterThanOrEqual(1);
  });

  // -----------------------------------------------------------------------
  // Test 5: Empty state
  // -----------------------------------------------------------------------
  test('shows empty state for non-existent search', async ({ page }) => {
    await page.goto('/it/talenti');
    await expect(page.locator('h1')).toContainText('Scopri i Talenti', { timeout: 15000 });

    // Wait for initial load
    await expect(page.locator('[role="button"]').first()).toBeVisible({ timeout: 10000 });

    // Search for a name that doesn't exist
    const searchInput = page.getByPlaceholder('Cerca per nome, ruolo o competenza...');
    await searchInput.fill('ZZZZNONEXISTENT');

    // Wait for debounce (350ms) + API response
    await page.waitForTimeout(500);

    // Empty state message should be shown
    await expect(page.getByText('Nessun talento trovato')).toBeVisible({ timeout: 10000 });
    await expect(page.getByText('Prova a modificare i filtri o la ricerca.')).toBeVisible();
  });
});

// =========================================================================
// Test Group 2: Talent Detail Page (public, no auth)
// =========================================================================
test.describe('Talent Detail Page', () => {
  // -----------------------------------------------------------------------
  // Test 6: Navigate to talent detail
  // -----------------------------------------------------------------------
  test('navigate to talent detail from list', async ({ page }) => {
    await page.goto('/it/talenti');
    await expect(page.locator('h1')).toContainText('Scopri i Talenti', { timeout: 15000 });

    // Wait for talents to load and click Marco Rossi's card
    const marcoCard = page.locator('[role="button"]', { hasText: 'Marco Rossi' });
    await expect(marcoCard).toBeVisible({ timeout: 10000 });
    await marcoCard.click();

    // Wait for the detail page to load
    await page.waitForURL('**/it/talenti/**', { timeout: 10000 });

    // Verify h1 contains "Marco Rossi"
    await expect(page.locator('h1')).toContainText('Marco Rossi', { timeout: 15000 });

    // Verify "Frontend Developer" is visible
    await expect(page.getByText('Frontend Developer').first()).toBeVisible();

    // Verify "Milano" is visible
    await expect(page.getByText('Milano').first()).toBeVisible();

    // Verify "Esperienza Lavorativa" section is visible
    await expect(page.getByText('Esperienza Lavorativa')).toBeVisible();

    // Verify "TechFlow Italia" (experience) is visible
    await expect(page.getByText('TechFlow Italia').first()).toBeVisible();

    // Verify "Formazione" section is visible
    await expect(page.getByText('Formazione').first()).toBeVisible();
  });

  // -----------------------------------------------------------------------
  // Test 7: Privacy — email not shown
  // -----------------------------------------------------------------------
  test('email and phone are not shown on detail page', async ({ page }) => {
    await page.goto('/it/talenti');
    await expect(page.locator('h1')).toContainText('Scopri i Talenti', { timeout: 15000 });

    // Navigate to Marco Rossi's detail page
    const marcoCard = page.locator('[role="button"]', { hasText: 'Marco Rossi' });
    await expect(marcoCard).toBeVisible({ timeout: 10000 });
    await marcoCard.click();

    await page.waitForURL('**/it/talenti/**', { timeout: 10000 });
    await expect(page.locator('h1')).toContainText('Marco Rossi', { timeout: 15000 });

    // Verify email is NOT visible anywhere
    await expect(page.getByText('marco.rossi@email.it')).not.toBeVisible();

    // Verify phone is NOT visible anywhere
    await expect(page.getByText('+39 333 1234567')).not.toBeVisible();
  });

  // -----------------------------------------------------------------------
  // Test 8: 404 for non-existent talent
  // -----------------------------------------------------------------------
  test('shows 404 for non-existent talent', async ({ page }) => {
    await page.goto('/it/talenti/nonexistent-id-12345');

    // Verify "Talento non trovato" is visible
    await expect(page.getByText('Talento non trovato')).toBeVisible({ timeout: 15000 });
  });

  // -----------------------------------------------------------------------
  // Test 9: Social links visible
  // -----------------------------------------------------------------------
  test('social links are visible on detail page', async ({ page }) => {
    await page.goto('/it/talenti');
    await expect(page.locator('h1')).toContainText('Scopri i Talenti', { timeout: 15000 });

    // Navigate to Marco Rossi's detail page
    const marcoCard = page.locator('[role="button"]', { hasText: 'Marco Rossi' });
    await expect(marcoCard).toBeVisible({ timeout: 10000 });
    await marcoCard.click();

    await page.waitForURL('**/it/talenti/**', { timeout: 10000 });
    await expect(page.locator('h1')).toContainText('Marco Rossi', { timeout: 15000 });

    // Verify LinkedIn link is visible (scoped to main content, not footer)
    await expect(page.getByRole('main').locator('a[aria-label="LinkedIn"]')).toBeVisible();

    // Verify GitHub link is visible (scoped to main content, not footer)
    await expect(page.getByRole('main').locator('a[aria-label="GitHub"]')).toBeVisible();
  });

  // -----------------------------------------------------------------------
  // Test 10: CTA links to Craft Your Developer
  // -----------------------------------------------------------------------
  test('CTA links to Craft Your Developer', async ({ page }) => {
    await page.goto('/it/talenti');
    await expect(page.locator('h1')).toContainText('Scopri i Talenti', { timeout: 15000 });

    // Navigate to Marco Rossi's detail page
    const marcoCard = page.locator('[role="button"]', { hasText: 'Marco Rossi' });
    await expect(marcoCard).toBeVisible({ timeout: 10000 });
    await marcoCard.click();

    await page.waitForURL('**/it/talenti/**', { timeout: 10000 });
    await expect(page.locator('h1')).toContainText('Marco Rossi', { timeout: 15000 });

    // Verify "Interessato a questo talento?" text is visible
    await expect(page.getByText('Interessato a questo talento?')).toBeVisible();

    // Verify link to Craft Your Developer is present
    const cydLink = page.locator('a[href="/it/craft-your-developer"]');
    await expect(cydLink.last()).toBeVisible();
  });
});

// =========================================================================
// Test Group 3: Profile Privacy Toggle (requires auth)
// =========================================================================
test.describe('Profile Privacy Toggle', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
  });

  // -----------------------------------------------------------------------
  // Test 11: Privacy toggle visible on profile page
  // -----------------------------------------------------------------------
  test('privacy toggle is visible on profile page', async ({ page }) => {
    await page.goto('/it/profilo');
    await page.waitForSelector('h1', { timeout: 15000 });

    // Verify "Visibilita' Profilo" heading is visible (note: apostrophe in Italian)
    await expect(page.getByText('Visibilit')).toBeVisible();

    // Verify the toggle switch (role="switch") exists
    const toggle = page.locator('[role="switch"]');
    await expect(toggle).toBeVisible();
  });

  // -----------------------------------------------------------------------
  // Test 12: Toggle privacy and verify
  // -----------------------------------------------------------------------
  test('toggle privacy and verify state change', async ({ page }) => {
    await page.goto('/it/profilo');
    await page.waitForSelector('h1', { timeout: 15000 });

    // Find the toggle
    const toggle = page.locator('[role="switch"]');
    await expect(toggle).toBeVisible();

    // Note initial state
    const initialState = await toggle.getAttribute('aria-checked');

    // Click to toggle
    await toggle.click();

    // Wait for API response
    await page.waitForTimeout(1000);

    // Verify toggle state changed
    const newState = await toggle.getAttribute('aria-checked');
    expect(newState).not.toBe(initialState);

    // Toggle back to restore original state
    await toggle.click();

    // Wait for API response
    await page.waitForTimeout(1000);

    // Verify restored
    const restoredState = await toggle.getAttribute('aria-checked');
    expect(restoredState).toBe(initialState);
  });
});

// =========================================================================
// Test Group 4: Navigation
// =========================================================================
test.describe('Navigation', () => {
  // -----------------------------------------------------------------------
  // Test 13: CYD page links to talents
  // -----------------------------------------------------------------------
  test('Craft Your Developer page links to talents', async ({ page }) => {
    await page.goto('/it/craft-your-developer');

    // Verify "Scopri i Talenti" button/link exists (scoped to main content, not footer)
    const talentsLink = page.getByRole('main').locator('a[href="/it/talenti"]', { hasText: 'Scopri i Talenti' });
    await expect(talentsLink).toBeVisible({ timeout: 15000 });

    // Click it
    await talentsLink.click();

    // Verify navigated to /it/talenti
    await page.waitForURL('**/it/talenti', { timeout: 10000 });
    await expect(page.locator('h1')).toContainText('Scopri i Talenti', { timeout: 15000 });
  });
});
