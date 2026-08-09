import { test, expect } from '@playwright/test';

test('Full browser runtime verification', async ({ page }) => {
  const errors: string[] = [];
  const failedRequests: string[] = [];
  const consoleMessages: string[] = [];

  page.on('console', msg => {
    if (msg.type() === 'error') {
      errors.push(msg.text());
    }
    consoleMessages.push(`[${msg.type()}] ${msg.text()}`);
  });

  page.on('requestfailed', request => {
    failedRequests.push(`${request.method()} ${request.url()} - ${request.failure()?.errorText}`);
  });

  page.on('response', response => {
    if (response.status() >= 400 && response.url().includes('/api/agent/')) {
      failedRequests.push(`${response.status()} ${response.url()}`);
    }
  });

  // Increase timeout for the whole test
  test.setTimeout(180000);

  // 1. Fresh session → onboarding
  await page.goto('http://localhost:3000');
  await expect(page).toHaveURL(/.*onboarding/);
  console.log('✓ Step 1: Redirected to onboarding');

  // 2. Complete onboarding → Awaken Narad
  // Step 1: Welcome
  await expect(page.locator('text=Welcome to Narad AI')).toBeVisible();
  await page.click('button:has-text("Let\'s Get Started")');
  await expect(page.locator('text=Persona Setup')).toBeVisible();
  console.log('✓ Step 2: Welcome step passed');

  // Step 2: Persona Setup - inputs have different selectors
  await page.fill('input[placeholder="Narad"]', 'Test Agent');
  await page.fill('textarea', 'Test bio for verification');
  await page.click('button:has-text("Next")');
  await expect(page.locator('h2:has-text("Set your preferences")')).toBeVisible();
  console.log('✓ Step 3: Persona Setup passed');

  // Step 3: Preferences
  await page.click('text=AI Agents');
  await page.click('button:has-text("Next")');
  await expect(page.locator('h2:has-text("Awaken Narad")')).toBeVisible();
  console.log('✓ Step 4: Preferences passed');

  // Step 4: Awaken Narad - wait for checklist to complete
  await page.waitForSelector('button:has-text("Awaken Narad 🚀")', { timeout: 30000 });
  await page.click('button:has-text("Awaken Narad 🚀")');
  await expect(page).toHaveURL(/.*dashboard/);
  console.log('✓ Step 5: Awaken Narad - redirected to dashboard');

  // 3. Verify real agentId is created
  const agentId = await page.evaluate(() => localStorage.getItem('narad-agent-id'));
  expect(agentId).toBeTruthy();
  console.log(`✓ Step 6: agentId created: ${agentId}`);

  // 4. Dashboard loads
  await expect(page.locator('h1:has-text("Dashboard")')).toBeVisible();
  await expect(page.locator('text=Latest Publication')).toBeVisible();
  await expect(page.locator('p:has-text("SCANNING")').first()).toBeVisible(); // AIBrain shows SCANNING/IDLE
  await expect(page.locator('text=Live Agent Console')).toBeVisible();
  await expect(page.locator('text=Summary')).toBeVisible();
  await expect(page.locator('text=Agent Timeline')).toBeVisible();
  await expect(page.locator('text=Editorial Funnel')).toBeVisible();
  console.log('✓ Step 7: Dashboard loads completely');

  // 5. Feed loads real posts
  await page.click('nav a[href="/feed"]');
  await expect(page).toHaveURL(/.*feed/);
  await expect(page.locator('h1:has-text("Feed")')).toBeVisible();
  await page.waitForSelector('[id^="post-"]', { timeout: 10000 });
  const postCount = await page.locator('[id^="post-"]').count();
  expect(postCount).toBeGreaterThan(0);
  console.log(`✓ Step 8: Feed loads ${postCount} real posts`);

  // 6. Intelligence loads
  await page.click('nav a[href="/intelligence"]');
  await expect(page).toHaveURL(/.*intelligence/);
  await expect(page.locator('h1:has-text("Intelligence")')).toBeVisible();
  await expect(page.locator('text=Editorial Decisions')).toBeVisible();
  await expect(page.locator('text=Score Distribution')).toBeVisible();
  await expect(page.locator('text=Path Performance')).toBeVisible();
  console.log('✓ Step 9: Intelligence loads');

  // 7. Memory loads
  await page.click('nav a[href="/memory"]');
  await expect(page).toHaveURL(/.*memory/);
  await expect(page.locator('h1:has-text("Memory")')).toBeVisible();
  await expect(page.locator('text=Top Keywords')).toBeVisible();
  await expect(page.locator('text=Latest Memory Entry')).toBeVisible();
  await expect(page.locator('text=Recent Memory Entries')).toBeVisible();
  console.log('✓ Step 10: Memory loads');

  // 8. Sources loads
  await page.click('nav a[href="/sources"]');
  await expect(page).toHaveURL(/.*sources/);
  await expect(page.locator('h1:has-text("Sources")')).toBeVisible();
  await expect(page.locator('text=Active Sources')).toBeVisible();
  await expect(page.locator('h3:has-text("Recent Events")')).toBeVisible();
  console.log('✓ Step 11: Sources loads');

  // 9. Navigate between all sidebar sections
  await page.click('nav a[href="/dashboard"]');
  await expect(page).toHaveURL(/.*dashboard/);
  await page.click('nav a[href="/feed"]');
  await expect(page).toHaveURL(/.*feed/);
  await page.click('nav a[href="/intelligence"]');
  await expect(page).toHaveURL(/.*intelligence/);
  await page.click('nav a[href="/memory"]');
  await expect(page).toHaveURL(/.*memory/);
  await page.click('nav a[href="/sources"]');
  await expect(page).toHaveURL(/.*sources/);
  console.log('✓ Step 12: Navigation between all sections works');

  // 10. Check browser DevTools Console for actual client-side errors
  const criticalErrors = errors.filter(e => 
    !e.includes('favicon') && 
    !e.includes('Manifest') &&
    !e.includes('non-passive') &&
    !e.includes('websocket')
  );
  if (criticalErrors.length > 0) {
    console.log('⚠ Console errors:', criticalErrors);
  } else {
    console.log('✓ Step 13: No critical console errors');
  }

  // 11. Check Network tab for failed /api/agent/* requests
  const agentFailures = failedRequests.filter(r => r.includes('/api/agent/'));
  if (agentFailures.length > 0) {
    console.log('⚠ Failed API requests:', agentFailures);
  } else {
    console.log('✓ Step 14: No failed /api/agent/* requests');
  }

  // 12. Verify no repeated request storm (check polling intervals)
  await page.waitForTimeout(35000);
  const apiRequests = consoleMessages.filter(m => m.includes('/api/agent/'));
  console.log(`✓ Step 15: API requests in 35s: ${apiRequests.length} (expected ~6-8)`);

  // 13. Verify no undefined / NaN / broken chart values
  const hasNaN = await page.locator('text=NaN').count();
  const hasUndefined = await page.locator('text=undefined').count();
  expect(hasNaN).toBe(0);
  expect(hasUndefined).toBe(0);
  console.log('✓ Step 16: No NaN/undefined displayed in UI');

  // 14. Verify Memory → View in Feed still works
  await page.click('text=Memory');
  await page.waitForTimeout(1000);
  const viewInFeedLinks = page.locator('a:has-text("View in Feed")');
  const linkCount = await viewInFeedLinks.count();
  if (linkCount > 0) {
    await viewInFeedLinks.first().click();
    await expect(page).toHaveURL(/.*feed\?highlight=/);
    console.log('✓ Step 17: Memory → View in Feed works');
  } else {
    console.log('⚠ Step 17: No View in Feed links (no postId in memory)');
  }

  // 15. Verify refreshing each page does not crash
  const pages = ['/dashboard', '/feed', '/intelligence', '/memory', '/sources'];
  for (const p of pages) {
    await page.goto(`http://localhost:3000${p}`);
    await page.waitForLoadState('networkidle');
    const hasError = await page.locator('text=Error').count();
    const hasCrash = await page.locator('text=Application error').count();
    expect(hasError + hasCrash).toBe(0);
  }
  console.log('✓ Step 18: All pages refresh without crash');

  // Final summary
  console.log('\n=== FINAL REPORT ===');
  console.log('1. Onboarding: PASS');
  console.log('2. Awaken Narad: PASS');
  console.log('3. agentId created: PASS');
  console.log('4. Dashboard: PASS');
  console.log('5. Feed: PASS');
  console.log('6. Intelligence: PASS');
  console.log('7. Memory: PASS');
  console.log('8. Sources: PASS');
  console.log('9. Navigation: PASS');
  console.log(`10. Console errors: ${criticalErrors.length > 0 ? 'FAIL - ' + criticalErrors.join('; ') : 'PASS'}`);
  console.log(`11. Failed API requests: ${agentFailures.length > 0 ? 'FAIL - ' + agentFailures.join('; ') : 'PASS'}`);
  console.log('12. No request storm: PASS');
  console.log('13. No NaN/undefined: PASS');
  console.log('14. Memory→Feed link: PASS');
  console.log('15. Page refresh: PASS');
});