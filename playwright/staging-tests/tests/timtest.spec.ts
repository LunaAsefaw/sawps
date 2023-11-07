import { test, expect } from '@playwright/test';

test.use({
  storageState: 'auth.json'
});

test('test', async ({ page }) => {
  await page.goto('https://sawps.sta.do.kartoza.com/');
  await page.locator('#navbarNav').getByRole('link', { name: 'EXPLORE' }).click();
  await page.getByPlaceholder('Select').click();
  await page.getByRole('option', { name: 'Panthera leo' }).click();
  await page.getByRole('tab', { name: 'REPORTS' }).click();
  await page.getByText('Venetia Limpopo NR', { exact: true }).click();
});