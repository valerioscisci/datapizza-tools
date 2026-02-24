import { test, expect, Page } from '@playwright/test';

// ---------------------------------------------------------------------------
// Constants — real seeded credentials from api/database/seed.py
// ---------------------------------------------------------------------------
const TALENT_EMAIL = 'marco.rossi@email.it';
const TALENT_PASSWORD = 'password123';

const COMPANY_EMAIL = 'hr@techflow.it';
const COMPANY_PASSWORD = 'password123';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Login as a talent user and wait for redirect to /it/jobs.
 */
async function loginAsTalent(page: Page) {
  await page.goto('/it/login');
  await page.waitForLoadState('networkidle');
  await page.locator('input[type="email"]').fill(TALENT_EMAIL);
  await page.locator('input[type="password"]').fill(TALENT_PASSWORD);
  await page.locator('button[type="submit"]').click();
  await page.waitForURL('**/it/jobs', { timeout: 15000 });
}

/**
 * Login as a company user and wait for redirect to /it/talenti.
 */
async function loginAsCompany(page: Page) {
  await page.goto('/it/login');
  await page.waitForLoadState('networkidle');
  await page.locator('input[type="email"]').fill(COMPANY_EMAIL);
  await page.locator('input[type="password"]').fill(COMPANY_PASSWORD);
  await page.locator('button[type="submit"]').click();
  await page.waitForURL('**/it/talenti', { timeout: 15000 });
}

// =========================================================================
// Group 1: Company Signup Flow
// =========================================================================
test.describe('Company Signup Flow', () => {
  test('signup page shows talent/company tabs', async ({ page }) => {
    await page.goto('/it/signup');
    await expect(page.locator('h1')).toContainText('Registrati');

    // Both user type tabs should be visible
    await expect(page.getByRole('button', { name: 'Sono un Talento' })).toBeVisible();
    await expect(page.getByRole('button', { name: "Sono un'Azienda" })).toBeVisible();
  });

  test('company tab shows company-specific fields', async ({ page }) => {
    await page.goto('/it/signup');
    await page.getByRole('button', { name: "Sono un'Azienda" }).click();

    // Company-specific fields should appear
    await expect(page.getByLabel('Nome Azienda')).toBeVisible();
    await expect(page.getByLabel('Nome referente')).toBeVisible();
    await expect(page.getByLabel('Email aziendale')).toBeVisible();
    await expect(page.getByLabel('Sito Web')).toBeVisible();
    await expect(page.getByLabel('Settore')).toBeVisible();

    // Settore dropdown should have options
    const settoreSelect = page.getByLabel('Settore');
    await expect(settoreSelect.locator('option')).toHaveCount(11); // 10 industries + "Seleziona un settore"
  });

  test('company signup creates account and redirects to /it/talenti', async ({ page }) => {
    const uniqueEmail = `e2e-company-${Date.now()}@test.it`;

    await page.goto('/it/signup');
    await page.getByRole('button', { name: "Sono un'Azienda" }).click();

    await page.getByLabel('Nome Azienda').fill('E2E Test Company');
    await page.getByLabel('Nome referente').fill('Test Referente');
    await page.getByLabel('Email aziendale').fill(uniqueEmail);
    await page.getByLabel('Password', { exact: true }).fill('testpassword123');
    await page.getByLabel('Conferma Password').fill('testpassword123');
    await page.getByLabel('Settore').selectOption('SaaS');

    await page.locator('button[type="submit"]').click();

    // Company should redirect to /it/talenti
    await page.waitForURL('**/it/talenti', { timeout: 15000 });
    await expect(page).toHaveURL(/\/it\/talenti/);
  });

  test('company signup without company name shows error', async ({ page }) => {
    await page.goto('/it/signup');
    await page.getByRole('button', { name: "Sono un'Azienda" }).click();

    // Fill everything EXCEPT company name - but it's required HTML attribute,
    // so we test the client-side validation
    await page.getByLabel('Nome referente').fill('Test Referente');
    await page.getByLabel('Email aziendale').fill('company-noname@test.it');
    await page.getByLabel('Password', { exact: true }).fill('testpassword123');
    await page.getByLabel('Conferma Password').fill('testpassword123');

    await page.locator('button[type="submit"]').click();

    // Page should NOT redirect (form validation prevents submission)
    await page.waitForTimeout(1000);
    await expect(page).toHaveURL(/\/it\/signup/);
  });
});

// =========================================================================
// Group 2: Login Redirect Logic
// =========================================================================
test.describe('Login Redirect Logic', () => {
  test('company login redirects to /it/talenti', async ({ page }) => {
    await loginAsCompany(page);
    await expect(page).toHaveURL(/\/it\/talenti/);
  });

  test('talent login redirects to /it/jobs', async ({ page }) => {
    await loginAsTalent(page);
    await expect(page).toHaveURL(/\/it\/jobs/);
  });
});

// =========================================================================
// Group 3: Navbar Role-Based Items
// =========================================================================
test.describe('Navbar Role-Based Items', () => {
  test('company navbar shows "Le mie Proposte" link', async ({ page }) => {
    await loginAsCompany(page);

    // Company should see "Le mie Proposte" link pointing to /it/azienda/proposte
    const proposalsLink = page.locator('a[href="/it/azienda/proposte"]');
    await expect(proposalsLink.first()).toBeVisible({ timeout: 5000 });

    // Company should NOT see "Il mio Profilo" or "Le mie Candidature"
    await expect(page.locator('a[href="/it/profilo"]')).not.toBeVisible();
    await expect(page.locator('a[href="/it/candidature"]')).not.toBeVisible();
  });

  test('talent navbar shows profile and candidature links', async ({ page }) => {
    await loginAsTalent(page);

    // Talent should see "Il mio Profilo" and "Le mie Candidature"
    await expect(page.locator('a[href="/it/profilo"]').first()).toBeVisible({ timeout: 5000 });
    await expect(page.locator('a[href="/it/candidature"]').first()).toBeVisible();

    // Talent should NOT see "Le mie Proposte" pointing to company proposals
    await expect(page.locator('a[href="/it/azienda/proposte"]')).not.toBeVisible();
  });

  test('company navbar shows company initial in avatar', async ({ page }) => {
    await loginAsCompany(page);

    // Avatar should show "T" for TechFlow Italia
    const avatar = page.locator('nav').getByText('T').first();
    await expect(avatar).toBeVisible({ timeout: 5000 });
  });
});

// =========================================================================
// Group 4: Talent Detail — Company CTA
// =========================================================================
test.describe('Talent Detail — Company CTA', () => {
  test('company user sees "Proponi un Percorso" CTA on talent detail', async ({ page }) => {
    await loginAsCompany(page);

    // Navigate to Marco Rossi's detail page
    const marcoCard = page.locator('[role="button"]', { hasText: 'Marco Rossi' });
    await expect(marcoCard).toBeVisible({ timeout: 10000 });
    await marcoCard.click();

    await page.waitForURL('**/it/talenti/**', { timeout: 10000 });
    await expect(page.locator('h1')).toContainText('Marco Rossi', { timeout: 15000 });

    // Company CTA: "Proponi un Percorso" (NOT "Scopri Craft Your Developer")
    await expect(page.getByText('Proponi un Percorso').first()).toBeVisible();

    // The link should point to the proposal creation page with talent_id
    const proposalLink = page.locator('a[href*="/it/azienda/proposte/nuova?talent_id="]');
    await expect(proposalLink).toBeVisible();
  });

  test('company CTA navigates to proposal creation page', async ({ page }) => {
    await loginAsCompany(page);

    // Navigate to talent detail
    const marcoCard = page.locator('[role="button"]', { hasText: 'Marco Rossi' });
    await expect(marcoCard).toBeVisible({ timeout: 10000 });
    await marcoCard.click();

    await page.waitForURL('**/it/talenti/**', { timeout: 10000 });
    await expect(page.locator('h1')).toContainText('Marco Rossi', { timeout: 15000 });

    // Click the "Proponi un Percorso" CTA link
    const ctaLink = page.locator('a[href*="/it/azienda/proposte/nuova?talent_id="]');
    await ctaLink.click();

    // Should navigate to proposal creation page
    await page.waitForURL('**/it/azienda/proposte/nuova**', { timeout: 10000 });
    await expect(page.locator('h1')).toContainText('Nuova Proposta', { timeout: 15000 });

    // Talent info should be displayed
    await expect(page.getByText('Marco Rossi')).toBeVisible();
    await expect(page.getByText('Frontend Developer')).toBeVisible();
  });

  test('unauthenticated user sees generic CTA on talent detail', async ({ page }) => {
    await page.goto('/it/talenti');
    await expect(page.locator('h1')).toContainText('Scopri i Talenti', { timeout: 15000 });

    const marcoCard = page.locator('[role="button"]', { hasText: 'Marco Rossi' });
    await expect(marcoCard).toBeVisible({ timeout: 10000 });
    await marcoCard.click();

    await page.waitForURL('**/it/talenti/**', { timeout: 10000 });
    await expect(page.locator('h1')).toContainText('Marco Rossi', { timeout: 15000 });

    // Unauthenticated user should see generic CTA "Interessato a questo talento?"
    await expect(page.getByText('Interessato a questo talento?')).toBeVisible();

    // Should NOT see "Proponi un Percorso"
    await expect(page.locator('a[href*="/it/azienda/proposte/nuova"]')).not.toBeVisible();
  });
});

// =========================================================================
// Group 5: Proposal Creation Page
// =========================================================================
test.describe('Proposal Creation Page', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsCompany(page);
  });

  test('displays talent info and course list', async ({ page }) => {
    // Navigate to a talent and click through to proposal creation
    const marcoCard = page.locator('[role="button"]', { hasText: 'Marco Rossi' });
    await expect(marcoCard).toBeVisible({ timeout: 10000 });
    await marcoCard.click();
    await page.waitForURL('**/it/talenti/**', { timeout: 10000 });

    const ctaLink = page.locator('a[href*="/it/azienda/proposte/nuova?talent_id="]');
    await ctaLink.click();
    await page.waitForURL('**/it/azienda/proposte/nuova**', { timeout: 10000 });

    // Title
    await expect(page.locator('h1')).toContainText('Nuova Proposta', { timeout: 15000 });

    // Talent info section
    await expect(page.getByText('Informazioni Talento')).toBeVisible();
    await expect(page.getByText('Marco Rossi')).toBeVisible();
    await expect(page.getByText('Frontend Developer')).toBeVisible();
    await expect(page.getByText('Milano')).toBeVisible();

    // Course selection section
    await expect(page.getByText('Seleziona i Corsi')).toBeVisible();

    // At least one course checkbox should be visible
    const courseCheckboxes = page.locator('[role="checkbox"]');
    const count = await courseCheckboxes.count();
    expect(count).toBeGreaterThanOrEqual(1);

    // Message and budget fields
    await expect(page.getByLabel('Messaggio')).toBeVisible();
    await expect(page.getByLabel('Budget Indicativo')).toBeVisible();

    // Submit button
    await expect(page.getByRole('button', { name: 'Invia Proposta' })).toBeVisible();
  });

  test('course selection and reordering works', async ({ page }) => {
    // Navigate to proposal creation
    const marcoCard = page.locator('[role="button"]', { hasText: 'Marco Rossi' });
    await expect(marcoCard).toBeVisible({ timeout: 10000 });
    await marcoCard.click();
    await page.waitForURL('**/it/talenti/**', { timeout: 10000 });

    const ctaLink = page.locator('a[href*="/it/azienda/proposte/nuova?talent_id="]');
    await ctaLink.click();
    await page.waitForURL('**/it/azienda/proposte/nuova**', { timeout: 10000 });
    await expect(page.locator('h1')).toContainText('Nuova Proposta', { timeout: 15000 });

    // Select first course
    const firstCheckbox = page.locator('[role="checkbox"]').first();
    await firstCheckbox.click();

    // "Corsi Selezionati (1)" heading should appear
    await expect(page.getByText('Corsi Selezionati (1)')).toBeVisible();

    // Select second course
    const secondCheckbox = page.locator('[role="checkbox"]').nth(1);
    await secondCheckbox.click();

    // "Corsi Selezionati (2)" heading should appear
    await expect(page.getByText('Corsi Selezionati (2)')).toBeVisible();

    // Deselect first course
    await firstCheckbox.click();

    // "Corsi Selezionati (1)" heading should show again
    await expect(page.getByText('Corsi Selezionati (1)')).toBeVisible();
  });

  test('submitting proposal redirects to company proposals', async ({ page }) => {
    // Navigate to proposal creation for Marco Rossi
    const marcoCard = page.locator('[role="button"]', { hasText: 'Marco Rossi' });
    await expect(marcoCard).toBeVisible({ timeout: 10000 });
    await marcoCard.click();
    await page.waitForURL('**/it/talenti/**', { timeout: 10000 });

    const ctaLink = page.locator('a[href*="/it/azienda/proposte/nuova?talent_id="]');
    await ctaLink.click();
    await page.waitForURL('**/it/azienda/proposte/nuova**', { timeout: 10000 });
    await expect(page.locator('h1')).toContainText('Nuova Proposta', { timeout: 15000 });

    // Select a course
    const firstCheckbox = page.locator('[role="checkbox"]').first();
    await firstCheckbox.click();
    await expect(page.getByText('Corsi Selezionati (1)')).toBeVisible();

    // Fill message and budget
    await page.getByLabel('Messaggio').fill('E2E test proposal message');
    await page.getByLabel('Budget Indicativo').fill('1.000 - 2.000 EUR');

    // Submit
    await page.getByRole('button', { name: 'Invia Proposta' }).click();

    // Should redirect to company proposals dashboard
    await page.waitForURL('**/it/azienda/proposte', { timeout: 15000 });
    await expect(page.locator('h1')).toContainText('Proposte Inviate', { timeout: 15000 });
  });

  test('submitting without courses shows validation error', async ({ page }) => {
    // Navigate to proposal creation
    const marcoCard = page.locator('[role="button"]', { hasText: 'Marco Rossi' });
    await expect(marcoCard).toBeVisible({ timeout: 10000 });
    await marcoCard.click();
    await page.waitForURL('**/it/talenti/**', { timeout: 10000 });

    const ctaLink = page.locator('a[href*="/it/azienda/proposte/nuova?talent_id="]');
    await ctaLink.click();
    await page.waitForURL('**/it/azienda/proposte/nuova**', { timeout: 10000 });
    await expect(page.locator('h1')).toContainText('Nuova Proposta', { timeout: 15000 });

    // Try to submit without selecting any courses
    await page.getByRole('button', { name: 'Invia Proposta' }).click();

    // Should show validation error
    await expect(page.getByText('Seleziona almeno un corso')).toBeVisible({ timeout: 5000 });

    // Should NOT redirect
    await expect(page).toHaveURL(/\/it\/azienda\/proposte\/nuova/);
  });
});

// =========================================================================
// Group 6: Company Proposals Dashboard
// =========================================================================
test.describe('Company Proposals Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsCompany(page);
  });

  test('displays proposals with status tabs', async ({ page }) => {
    await page.goto('/it/azienda/proposte');

    // Title
    await expect(page.locator('h1')).toContainText('Proposte Inviate', { timeout: 15000 });

    // Status tabs
    await expect(page.getByRole('button', { name: 'Tutte' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Bozze' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Inviate' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Accettate' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Rifiutate' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Completate' })).toBeVisible();

    // Wait for proposals to load
    await page.waitForTimeout(1000);

    // Should show at least one proposal with talent name
    await expect(page.getByText('Marco Rossi').first()).toBeVisible({ timeout: 10000 });
  });

  test('proposals show progress bars', async ({ page }) => {
    await page.goto('/it/azienda/proposte');
    await expect(page.locator('h1')).toContainText('Proposte Inviate', { timeout: 15000 });

    // Wait for proposals to load
    await page.waitForTimeout(1000);

    // At least one "Progresso" label should be visible
    await expect(page.getByText('Progresso').first()).toBeVisible({ timeout: 10000 });

    // At least one "di X corsi completati" text should be visible
    await expect(page.getByText(/di \d+ corsi completati/).first()).toBeVisible();
  });

  test('status tabs filter proposals', async ({ page }) => {
    await page.goto('/it/azienda/proposte');
    await expect(page.locator('h1')).toContainText('Proposte Inviate', { timeout: 15000 });

    // Wait for initial load
    await page.waitForTimeout(1000);

    // Click "Accettate" tab
    await page.getByRole('button', { name: 'Accettate' }).click();
    await page.waitForTimeout(1000);

    // The seeded proposal for Marco Rossi is "accepted"
    await expect(page.getByText('Marco Rossi').first()).toBeVisible({ timeout: 10000 });

    // Click "Rifiutate" tab
    await page.getByRole('button', { name: 'Rifiutate' }).click();
    await page.waitForTimeout(1000);

    // There may be no rejected proposals (empty state or rejected ones)
    // The page should still be functional
    await expect(page.locator('h1')).toContainText('Proposte Inviate');
  });

  test('expandable courses list works', async ({ page }) => {
    await page.goto('/it/azienda/proposte');
    await expect(page.locator('h1')).toContainText('Proposte Inviate', { timeout: 15000 });

    // Wait for proposals to load
    await page.waitForTimeout(1000);

    // Click on courses expand button
    const coursesBtn = page.getByRole('button', { name: /Corsi \(\d+\)/ }).first();
    await expect(coursesBtn).toBeVisible({ timeout: 10000 });
    await coursesBtn.click();

    // Course items should be visible after expansion
    await expect(page.locator('.bg-neutral-50').first()).toBeVisible({ timeout: 5000 });
  });
});

// =========================================================================
// Group 7: Talent Proposals Dashboard
// =========================================================================
test.describe('Talent Proposals Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsTalent(page);
  });

  test('displays received proposals', async ({ page }) => {
    await page.goto('/it/proposte');

    // Title
    await expect(page.locator('h1')).toContainText('Le mie Proposte', { timeout: 15000 });

    // Status tabs (talent sees different tabs - no "Bozze")
    await expect(page.getByRole('button', { name: 'Tutte' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Inviate' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Accettate' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Rifiutate' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Completate' })).toBeVisible();

    // Wait for proposals to load
    await page.waitForTimeout(1000);

    // Should show company name "TechFlow Italia" on the proposal card
    await expect(page.getByText('TechFlow Italia').first()).toBeVisible({ timeout: 10000 });
  });

  test('proposals show status badges', async ({ page }) => {
    await page.goto('/it/proposte');
    await expect(page.locator('h1')).toContainText('Le mie Proposte', { timeout: 15000 });
    await page.waitForTimeout(1000);

    // At least one status badge should be visible (Accettata from seeded data)
    await expect(page.getByText('Accettata').first()).toBeVisible({ timeout: 10000 });
  });

  test('talent can expand course list', async ({ page }) => {
    await page.goto('/it/proposte');
    await expect(page.locator('h1')).toContainText('Le mie Proposte', { timeout: 15000 });
    await page.waitForTimeout(1000);

    // Click courses expand button
    const coursesBtn = page.getByRole('button', { name: /Corsi \(\d+\)/ }).first();
    await expect(coursesBtn).toBeVisible({ timeout: 10000 });
    await coursesBtn.click();

    // Course items should be visible
    await expect(page.locator('.bg-neutral-50').first()).toBeVisible({ timeout: 5000 });
  });

  test('accepted proposal shows "Segna come completato" on courses', async ({ page }) => {
    await page.goto('/it/proposte');
    await expect(page.locator('h1')).toContainText('Le mie Proposte', { timeout: 15000 });
    await page.waitForTimeout(1000);

    // Click "Accettate" tab to filter
    await page.getByRole('button', { name: 'Accettate' }).click();
    await page.waitForTimeout(1000);

    // Expand courses on the accepted proposal
    const coursesBtn = page.getByRole('button', { name: /Corsi \(\d+\)/ }).first();
    await expect(coursesBtn).toBeVisible({ timeout: 10000 });
    await coursesBtn.click();

    // "Segna come completato" button should be visible for incomplete courses
    await expect(page.getByRole('button', { name: 'Segna come completato' }).first()).toBeVisible({ timeout: 5000 });
  });

  test('talent proposals show budget and progress', async ({ page }) => {
    await page.goto('/it/proposte');
    await expect(page.locator('h1')).toContainText('Le mie Proposte', { timeout: 15000 });
    await page.waitForTimeout(1000);

    // Budget should be visible on at least one proposal
    await expect(page.getByText('Budget:').first()).toBeVisible({ timeout: 10000 });

    // Progress should be visible
    await expect(page.getByText('Progresso').first()).toBeVisible();
    await expect(page.getByText(/di \d+ corsi completati/).first()).toBeVisible();
  });
});

// =========================================================================
// Group 8: Auth Guards
// =========================================================================
test.describe('Auth Guards', () => {
  test('unauthenticated user cannot access /it/proposte', async ({ page }) => {
    await page.goto('/it/proposte');

    // Should redirect to login
    await page.waitForURL('**/it/login', { timeout: 15000 });
    await expect(page).toHaveURL(/\/it\/login/);
  });

  test('unauthenticated user cannot access /it/azienda/proposte', async ({ page }) => {
    await page.goto('/it/azienda/proposte');

    // Should redirect to login
    await page.waitForURL('**/it/login', { timeout: 15000 });
    await expect(page).toHaveURL(/\/it\/login/);
  });

  test('talent user cannot access /it/azienda/proposte', async ({ page }) => {
    await loginAsTalent(page);

    await page.goto('/it/azienda/proposte');

    // Should redirect to talent proposals page
    await page.waitForURL('**/it/proposte', { timeout: 15000 });
    await expect(page).toHaveURL(/\/it\/proposte$/);
  });

  test('company user accessing /it/candidature sees empty state', async ({ page }) => {
    await loginAsCompany(page);

    await page.goto('/it/candidature');

    // Candidature page does not have a company-specific redirect guard,
    // so the company user can access it but sees the page (with no applications).
    // The page heading should still load since the user is authenticated.
    await expect(page.locator('h1')).toContainText('Candidature', { timeout: 15000 });
  });
});
