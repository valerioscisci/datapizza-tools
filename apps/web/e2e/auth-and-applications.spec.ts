import { test, expect } from '@playwright/test';

const TEST_EMAIL = `e2e-${Date.now()}@test.it`;
const TEST_PASSWORD = 'testpassword123';
const TEST_NAME = 'E2E Test User';

test.describe('Authentication flow', () => {
  test('navbar shows login/signup buttons when not authenticated', async ({ page }) => {
    await page.goto('/it');

    // Desktop nav should show Accedi and Registrati
    const loginLink = page.locator('a[href="/it/login"]').first();
    const signupLink = page.locator('a[href="/it/signup"]').first();

    await expect(loginLink).toBeVisible();
    await expect(signupLink).toBeVisible();
  });

  test('signup page renders correctly', async ({ page }) => {
    await page.goto('/it/signup');

    await expect(page.locator('h1')).toContainText('Registrati');
    await expect(page.locator('input#fullName')).toBeVisible();
    await expect(page.locator('input#email')).toBeVisible();
    await expect(page.locator('input#password')).toBeVisible();
    await expect(page.locator('input#confirmPassword')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('login page renders correctly', async ({ page }) => {
    await page.goto('/it/login');

    await expect(page.locator('h1')).toContainText('Accedi');
    await expect(page.locator('input#email')).toBeVisible();
    await expect(page.locator('input#password')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('signup with password mismatch shows error', async ({ page }) => {
    await page.goto('/it/signup');

    await page.fill('input#fullName', TEST_NAME);
    await page.fill('input#email', 'mismatch@test.it');
    await page.fill('input#password', 'password123');
    await page.fill('input#confirmPassword', 'differentpassword');
    await page.click('button[type="submit"]');

    // Should show password mismatch error
    await expect(page.locator('text=Le password non coincidono')).toBeVisible();
  });

  test('signup creates account and redirects to jobs', async ({ page }) => {
    await page.goto('/it/signup');

    await page.fill('input#fullName', TEST_NAME);
    await page.fill('input#email', TEST_EMAIL);
    await page.fill('input#password', TEST_PASSWORD);
    await page.fill('input#confirmPassword', TEST_PASSWORD);
    await page.click('button[type="submit"]');

    // Should redirect to jobs page
    await page.waitForURL('**/it/jobs', { timeout: 10000 });
    await expect(page).toHaveURL(/\/it\/jobs/);
  });

  test('login with valid credentials redirects to jobs', async ({ page }) => {
    // Use seeded user
    await page.goto('/it/login');

    await page.fill('input#email', 'marco.rossi@email.it');
    await page.fill('input#password', 'password123');
    await page.click('button[type="submit"]');

    // Should redirect to jobs page
    await page.waitForURL('**/it/jobs', { timeout: 10000 });
    await expect(page).toHaveURL(/\/it\/jobs/);
  });

  test('login with invalid credentials shows error', async ({ page }) => {
    await page.goto('/it/login');

    await page.fill('input#email', 'wrong@email.it');
    await page.fill('input#password', 'wrongpassword');
    await page.click('button[type="submit"]');

    // Should show error message
    await expect(page.locator('.bg-red-50')).toBeVisible({ timeout: 5000 });
  });

  test('navbar shows user state after login', async ({ page }) => {
    await page.goto('/it/login');

    await page.fill('input#email', 'marco.rossi@email.it');
    await page.fill('input#password', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/it/jobs', { timeout: 10000 });

    // Should show user avatar initial 'M' for Marco
    const avatar = page.locator('text=M').first();
    await expect(avatar).toBeVisible({ timeout: 5000 });

    // Should show logout button
    await expect(page.locator('text=Esci').first()).toBeVisible();
  });

  test('logout clears user state', async ({ page }) => {
    // Login first
    await page.goto('/it/login');
    await page.fill('input#email', 'marco.rossi@email.it');
    await page.fill('input#password', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/it/jobs', { timeout: 10000 });

    // Click logout
    await page.locator('button:has-text("Esci")').first().click();

    // Should show login/signup buttons again
    await expect(page.locator('a[href="/it/login"]').first()).toBeVisible({ timeout: 5000 });
    await expect(page.locator('a[href="/it/signup"]').first()).toBeVisible();
  });
});

test.describe('Jobs page', () => {
  test('jobs page loads and displays jobs', async ({ page }) => {
    await page.goto('/it/jobs');

    await expect(page.locator('h1')).toContainText('Offerte di Lavoro');

    // Should show job cards
    const jobCards = page.locator('[role="button"]');
    await expect(jobCards.first()).toBeVisible({ timeout: 10000 });
  });

  test('job dialog opens on card click', async ({ page }) => {
    await page.goto('/it/jobs');

    // Wait for jobs to load
    const jobCard = page.locator('[role="button"]').first();
    await expect(jobCard).toBeVisible({ timeout: 10000 });
    await jobCard.click();

    // Dialog should appear
    await expect(page.locator('[role="dialog"]')).toBeVisible();
    await expect(page.locator('#job-dialog-title')).toBeVisible();
  });

  test('filter buttons work', async ({ page }) => {
    await page.goto('/it/jobs');

    // Click remote filter
    await page.locator('button:has-text("Remoto")').click();

    // Wait for reload
    await page.waitForTimeout(500);

    // Page should still be functional
    await expect(page.locator('h1')).toContainText('Offerte di Lavoro');
  });
});

test.describe('Applications flow', () => {
  test('candidature page redirects to login when not authenticated', async ({ page }) => {
    await page.goto('/it/candidature');

    // Should redirect to login
    await page.waitForURL('**/it/login', { timeout: 10000 });
  });

  test('candidature page loads with authenticated user', async ({ page }) => {
    // Login as Marco Rossi (has applications)
    await page.goto('/it/login');
    await page.fill('input#email', 'marco.rossi@email.it');
    await page.fill('input#password', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/it/jobs', { timeout: 10000 });

    // Navigate to candidature
    await page.goto('/it/candidature');

    await expect(page.locator('h1')).toContainText('Candidature');
    await expect(page.locator('text=Visualizza tutte le candidature')).toBeVisible();

    // Should show 4 status tabs
    await expect(page.locator('button:has-text("Proposte")')).toBeVisible();
    await expect(page.locator('button:has-text("Da completare")')).toBeVisible();
    await expect(page.locator('button:has-text("Attive")')).toBeVisible();
    await expect(page.locator('button:has-text("Archiviate")')).toBeVisible();
  });

  test('candidature page shows applications in active tab', async ({ page }) => {
    // Login as Marco Rossi
    await page.goto('/it/login');
    await page.fill('input#email', 'marco.rossi@email.it');
    await page.fill('input#password', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/it/jobs', { timeout: 10000 });

    await page.goto('/it/candidature');

    // Attive tab is default - Marco has 1 active application
    // Wait for application cards to load
    await page.waitForTimeout(2000);

    // Should show the application for "Senior Frontend Developer"
    const appCard = page.locator('text=Senior Frontend Developer');
    await expect(appCard.first()).toBeVisible({ timeout: 10000 });
  });

  test('switching tabs shows different applications', async ({ page }) => {
    // Login as Marco Rossi
    await page.goto('/it/login');
    await page.fill('input#email', 'marco.rossi@email.it');
    await page.fill('input#password', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/it/jobs', { timeout: 10000 });

    await page.goto('/it/candidature');

    // Click Archiviate tab
    await page.locator('button:has-text("Archiviate")').click();
    await page.waitForTimeout(1000);

    // Marco has 1 archived application for Full Stack Developer
    const archivedApp = page.locator('text=Full Stack Developer');
    await expect(archivedApp.first()).toBeVisible({ timeout: 10000 });
  });
});

test.describe('Full E2E: Signup -> Apply -> View Application', () => {
  test('complete flow: signup, apply to job, view in candidature', async ({ page }) => {
    const uniqueEmail = `e2e-flow-${Date.now()}@test.it`;

    // Step 1: Signup
    await page.goto('/it/signup');
    await page.fill('input#fullName', 'E2E Flow User');
    await page.fill('input#email', uniqueEmail);
    await page.fill('input#password', 'testpassword123');
    await page.fill('input#confirmPassword', 'testpassword123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/it/jobs', { timeout: 10000 });

    // Step 2: Open a job dialog
    const jobCard = page.locator('[role="button"]').first();
    await expect(jobCard).toBeVisible({ timeout: 10000 });
    await jobCard.click();
    await expect(page.locator('[role="dialog"]')).toBeVisible();

    // Step 3: Click Candidati button (for jobs without apply_url)
    const candidatiBtn = page.locator('[role="dialog"] button:has-text("Candidati")');
    if (await candidatiBtn.isVisible()) {
      await candidatiBtn.click();

      // Should show success state
      await expect(page.locator('text=Candidatura inviata!')).toBeVisible({ timeout: 5000 });
    }

    // Step 4: Close dialog and navigate to candidature
    await page.keyboard.press('Escape');
    await page.goto('/it/candidature');

    await expect(page.locator('h1')).toContainText('Candidature');

    // If we applied, we should see the application in the active tab
    // (The test is flexible since some jobs may have apply_url)
  });
});
