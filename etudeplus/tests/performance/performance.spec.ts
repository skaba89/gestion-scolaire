/**
 * Frontend Performance Testing with Playwright
 * Tests critical user journeys and measures performance metrics
 */

import { test, expect } from '@playwright/test';

// Test configuration
test.use({
  baseURL: process.env.BASE_URL || 'http://localhost:3000',
  trace: 'retain-on-failure',
  screenshot: 'only-on-failure',
  video: 'retain-on-failure',
});

// Performance thresholds (in ms)
const PERFORMANCE_THRESHOLDS = {
  pageLoad: 3000,
  apiResponse: 1000,
  timeToInteractive: 5000,
  firstContentfulPaint: 1500,
};

test.describe('Performance Tests', () => {
  
  test('Homepage loads within performance budget', async ({ page }) => {
    const startTime = Date.now();
    
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const loadTime = Date.now() - startTime;
    console.log(`Homepage load time: ${loadTime}ms`);
    
    expect(loadTime).toBeLessThan(PERFORMANCE_THRESHOLDS.pageLoad);
  });
  
  test('Login page renders quickly', async ({ page }) => {
    const startTime = Date.now();
    
    await page.goto('/auth/login');
    await page.waitForSelector('form');
    
    const renderTime = Date.now() - startTime;
    console.log(`Login page render time: ${renderTime}ms`);
    
    expect(renderTime).toBeLessThan(PERFORMANCE_THRESHOLDS.firstContentfulPaint);
  });
  
  test('Dashboard loads data within budget', async ({ page }) => {
    // Login first
    await page.goto('/auth/login');
    await page.fill('input[name="email"]', process.env.TEST_ADMIN_EMAIL || 'admin@test.local');
    await page.fill('input[name="password"]', process.env.TEST_ADMIN_PASSWORD || 'Test123!');
    await page.click('button[type="submit"]');
    
    // Wait for redirect to dashboard
    await page.waitForURL('**/dashboard', { timeout: 10000 });
    
    const startTime = Date.now();
    
    // Wait for dashboard data to load
    await page.waitForSelector('[data-testid="dashboard-loaded"]', { timeout: 15000 });
    
    const dataLoadTime = Date.now() - startTime;
    console.log(`Dashboard data load time: ${dataLoadTime}ms`);
    
    expect(dataLoadTime).toBeLessThan(PERFORMANCE_THRESHOLDS.timeToInteractive);
  });
});

test.describe('Multi-tenant Isolation Tests', () => {
  
  test('Tenant ID is properly set in all API requests', async ({ page }) => {
    // Login
    await page.goto('/auth/login');
    await page.fill('input[name="email"]', process.env.TEST_ADMIN_EMAIL || 'admin@test.local');
    await page.fill('input[name="password"]', process.env.TEST_ADMIN_PASSWORD || 'Test123!');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard');
    
    // Intercept API requests
    const requests: any[] = [];
    page.on('request', request => {
      if (request.url().includes('/api/v1/')) {
        requests.push({
          url: request.url(),
          headers: request.headers(),
        });
      }
    });
    
    // Navigate to trigger API calls
    await page.goto('/admin/students');
    await page.waitForSelector('[data-testid="students-table"]');
    
    // Verify X-Tenant-ID header in requests
    const apiRequests = requests.filter(r => r.url.includes('/api/v1/'));
    for (const req of apiRequests) {
      expect(req.headers['x-tenant-id']).toBeTruthy();
    }
  });
});
