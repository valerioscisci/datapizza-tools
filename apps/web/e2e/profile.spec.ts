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

  // Fill in credentials
  await page.locator('input[type="email"]').fill(TEST_EMAIL);
  await page.locator('input[type="password"]').fill(TEST_PASSWORD);

  // Submit
  await page.locator('button[type="submit"]').click();

  // Wait for redirect to /it/jobs (login success redirect)
  await page.waitForURL('**/it/jobs', { timeout: 15000 });
}

// =========================================================================
// Test 1: Profile page requires authentication
// =========================================================================
test.describe('Profile page authentication', () => {
  test('redirects to login when not authenticated', async ({ page }) => {
    await page.goto('/it/profilo');

    // The profile page should redirect unauthenticated users to /it/login
    await page.waitForURL('**/it/login', { timeout: 15000 });
    expect(page.url()).toContain('/it/login');
  });
});

// =========================================================================
// Tests 2-6: Authenticated profile tests (share login state)
// =========================================================================
test.describe('Profile page (authenticated)', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
  });

  // -----------------------------------------------------------------------
  // Test 2: Login and view profile
  // -----------------------------------------------------------------------
  test('displays user profile data correctly', async ({ page }) => {
    await page.goto('/it/profilo');

    // Wait for profile to load (client-side rendered)
    await page.waitForSelector('h1', { timeout: 15000 });

    // Name
    await expect(page.locator('h1')).toContainText('Marco Rossi');

    // Role (Frontend Developer) - in the profile header section
    await expect(page.getByText('Frontend Developer', { exact: true })).toBeVisible();

    // Location (Milano)
    await expect(page.getByText('Milano').first()).toBeVisible();

    // Bio text
    await expect(
      page.getByText('Frontend developer appassionato di React e performance web')
    ).toBeVisible();

    // Skills are shown
    await expect(page.getByText('React', { exact: true }).first()).toBeVisible();
    await expect(page.getByText('Next.js', { exact: true }).first()).toBeVisible();
    await expect(page.getByText('TypeScript', { exact: true }).first()).toBeVisible();
    await expect(page.getByText('Tailwind CSS', { exact: true }).first()).toBeVisible();
    await expect(page.getByText('GraphQL', { exact: true }).first()).toBeVisible();

    // Experience section is visible with heading "Esperienza Lavorativa"
    await expect(page.getByText('Esperienza Lavorativa')).toBeVisible();
    // At least one experience should be present (TechFlow Italia)
    await expect(page.getByText('TechFlow Italia').first()).toBeVisible();

    // Education section is visible with heading "Formazione"
    await expect(page.getByText('Formazione').first()).toBeVisible();
    // At least one education should be present (Politecnico di Milano)
    await expect(page.getByText('Politecnico di Milano').first()).toBeVisible();
  });

  // -----------------------------------------------------------------------
  // Test 3: Edit profile modal
  // -----------------------------------------------------------------------
  test('can edit profile via modal', async ({ page }) => {
    await page.goto('/it/profilo');
    await page.waitForSelector('h1', { timeout: 15000 });

    // Click the "Modifica Profilo" button
    await page.getByRole('button', { name: 'Modifica Profilo' }).click();

    // Verify modal opens (dialog role)
    const modal = page.locator('[role="dialog"]');
    await expect(modal).toBeVisible();

    // The modal title should be "Modifica Profilo"
    await expect(modal.locator('#edit-profile-title')).toContainText('Modifica Profilo');

    // Change the bio field
    const bioTextarea = modal.locator('textarea');
    const newBio = 'Bio aggiornata durante il test E2E Playwright.';
    await bioTextarea.fill(newBio);

    // Click "Salva" button (submit)
    await modal.getByRole('button', { name: 'Salva' }).click();

    // Wait for modal to close
    await expect(modal).not.toBeVisible({ timeout: 10000 });

    // Verify the new bio is visible on the page
    await expect(page.getByText(newBio)).toBeVisible({ timeout: 10000 });

    // Restore original bio to keep tests idempotent
    await page.getByRole('button', { name: 'Modifica Profilo' }).click();
    const restoredModal = page.locator('[role="dialog"]');
    await expect(restoredModal).toBeVisible();
    const restoredBioTextarea = restoredModal.locator('textarea');
    await restoredBioTextarea.fill(
      'Frontend developer appassionato di React e performance web. Contributore open source.'
    );
    await restoredModal.getByRole('button', { name: 'Salva' }).click();
    await expect(restoredModal).not.toBeVisible({ timeout: 10000 });
  });

  // -----------------------------------------------------------------------
  // Test 4: Skills management
  // -----------------------------------------------------------------------
  test('can add and remove skills', async ({ page }) => {
    await page.goto('/it/profilo');
    await page.waitForSelector('h1', { timeout: 15000 });

    // Find the skills section - it has the heading "Competenze"
    const skillsHeadingRow = page.getByText('Competenze', { exact: true }).locator('..');
    const editPencilBtn = skillsHeadingRow.locator('..').locator('button').first();
    await editPencilBtn.click();

    // Now the input field for adding skills should appear
    const skillInput = page.getByPlaceholder('es. React, Python, AWS...');
    await expect(skillInput).toBeVisible({ timeout: 5000 });

    // Add a new skill "Docker"
    await skillInput.fill('Docker');
    await skillInput.press('Enter');

    // Wait for the skill to appear as a pill/badge
    await expect(page.getByText('Docker', { exact: true }).first()).toBeVisible({
      timeout: 10000,
    });

    // Now remove the "Docker" skill by clicking the X button on its pill
    const removeBtn = page.getByRole('button', { name: 'Elimina Docker' });
    await removeBtn.click();

    // Wait for the skill to be removed
    await expect(removeBtn).not.toBeVisible({ timeout: 10000 });

    // Exit editing mode
    const closeEditBtn = skillsHeadingRow.locator('..').locator('button').first();
    await closeEditBtn.click();
  });

  // -----------------------------------------------------------------------
  // Test 5: Add experience
  // -----------------------------------------------------------------------
  test('can add a new experience', async ({ page }) => {
    await page.goto('/it/profilo');
    await page.waitForSelector('h1', { timeout: 15000 });

    // Click the "+" (Plus) button in the experience section
    await page.getByRole('button', { name: 'Aggiungi Esperienza' }).click();

    // The inline experience form should appear
    const expForm = page.locator('form').filter({ has: page.getByText('Ruolo') });

    // Fill "Ruolo" (Title)
    const titleInput = expForm.locator('input[type="text"]').first();
    await titleInput.fill('QA Engineer');

    // Fill "Azienda" (Company)
    const companyInput = expForm.locator('input[type="text"]').nth(1);
    await companyInput.fill('TestCompany SRL');

    // Select start year (third select after employment_type and start_month)
    const selects = expForm.locator('select');
    const startYearSelect = selects.nth(2);
    await startYearSelect.selectOption('2023');

    // Check "Attuale" (is_current) checkbox
    await expForm.locator('input[type="checkbox"]').check();

    // Submit the form by clicking "Salva"
    await expForm.getByRole('button', { name: 'Salva' }).click();

    // Wait for the form to disappear and the new experience to appear
    await expect(page.getByText('TestCompany SRL').first()).toBeVisible({ timeout: 10000 });
    await expect(page.getByText('QA Engineer').first()).toBeVisible({ timeout: 10000 });

    // Clean up: delete the newly added experience
    page.on('dialog', (dialog) => dialog.accept());
    await page.getByRole('button', { name: 'Elimina QA Engineer' }).click();

    // Wait for deletion
    await expect(page.getByText('TestCompany SRL')).not.toBeVisible({ timeout: 10000 });
  });

  // -----------------------------------------------------------------------
  // Test 6: Add education
  // -----------------------------------------------------------------------
  test('can add a new education', async ({ page }) => {
    await page.goto('/it/profilo');
    await page.waitForSelector('h1', { timeout: 15000 });

    // Click the "+" (Plus) button in the education section
    await page.getByRole('button', { name: 'Aggiungi Formazione' }).click();

    // The inline education form should appear
    const eduForm = page.locator('form').filter({ has: page.getByText('Istituto') });

    // Fill "Istituto" (Institution) - required
    const institutionInput = eduForm.locator('input[type="text"]').first();
    await institutionInput.fill('Universita di Test');

    // Select start year (second select after degree_type)
    const selects = eduForm.locator('select');
    const startYearSelect = selects.nth(1);
    await startYearSelect.selectOption('2020');

    // Submit the form
    await eduForm.getByRole('button', { name: 'Salva' }).click();

    // Wait for the new education to appear
    await expect(page.getByText('Universita di Test').first()).toBeVisible({
      timeout: 10000,
    });

    // Clean up: delete the newly added education
    page.on('dialog', (dialog) => dialog.accept());
    await page.getByRole('button', { name: 'Elimina Universita di Test' }).click();

    // Wait for deletion
    await expect(page.getByText('Universita di Test')).not.toBeVisible({ timeout: 10000 });
  });
});
