import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  retries: 0,
  workers: 1,
  reporter: 'list',
  use: {
    baseURL: 'http://localhost:3003',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  webServer: [
    {
      command: 'cd ../../apps/api && python3 run_api.py',
      port: 8003,
      reuseExistingServer: true,
      timeout: 15000,
    },
    {
      command: 'pnpm dev',
      port: 3003,
      reuseExistingServer: true,
      timeout: 30000,
    },
  ],
  outputDir: '../../.playwright-mcp/test-results',
});
