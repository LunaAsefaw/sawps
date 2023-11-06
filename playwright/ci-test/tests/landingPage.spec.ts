import { test, expect } from '@playwright/test';

let url = '/';


test.describe('navigation', () => {
  test.beforeEach(async ({ page }) => {
    // Go to the starting url before each test.
    await page.goto(url);
  });

  test('has title', async ({ page }) => {
    await page.waitForSelector('.landing-page-banner-text-header', { timeout: 2000 });
    await expect(page.locator('div.landing-page-banner-text-header')).toHaveText(
        'SOUTH AFRICAN WILDLIFE POPULATION SYSTEM MONITORING TRADED WILDLIFE IN SOUTH AFRICA'
    );
  })
  test('ABOUT button navigates', async ({page}) => {
    const buttonSelector = 'div.landing-page-banner-text-btns button:text("ABOUT")';

    await page.waitForSelector(buttonSelector, {timeout: 2000});

    const initialURL = page.url();

    await page.click(buttonSelector);

    await page.waitForURL('**/about/');

    const finalURL = page.url();

    expect(finalURL).not.toBe(initialURL);
  });
  test('HELP link navigates', async ({page}) => {
    const buttonSelector = 'div#navbarNav a:text("HELP")';

    await page.waitForSelector(buttonSelector, {timeout: 2000});

    const initialURL = page.url();

    await page.click(buttonSelector);

    await page.waitForURL('**/help/');

    const finalURL = page.url();

    expect(finalURL).not.toBe(initialURL);
  });
});
