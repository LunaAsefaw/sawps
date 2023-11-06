import { test , expect } from '@playwright/test';

let url = '/';


test.describe('Explore page', () => {
    
    test.use({ storageState: "tests/.auth/sawps-auth.json" });

    test('user interaction', async ({page}) => {

        await page.goto(url);

        const initialURL = page.url();

        await page.locator('#navbarNav').isVisible();

        const buttonSelector = 'div.landing-page-banner-text-btns button:text("EXPLORE")';

        await page.waitForSelector(buttonSelector, {timeout: 2000});

        await page.click(buttonSelector);

        await page.waitForURL('**/map/');

        await page.getByLabel('Map').isVisible();

        await page.getByRole('tab', {name: 'LAYERS'}).click(); //layers tab
        
        await page.locator('li').filter({ hasText: 'Critical Biodiversity areas' }).getByRole('button').click();

        await page.locator('li').filter({ hasText: 'Critical Biodiversity areas' }).getByRole('button').click();

        await page.getByRole('tab', {name: 'FILTERS'}).click(); //filters

        await page.getByText('Search placeOrganisationSelectSelect AllAdminPropertySelectSelect AllSpeciesActi').click();

        await page.getByText('Search placeOrganisationSelectSelect AllAdminPropertySelectSelect AllSpeciesActi').click();

        await page.locator('div').filter({ hasText: /^SelectSelect All$/ }).getByRole('button').click();

        await page.locator('div').filter({ hasText: /^SelectSelect All$/ }).getByRole('button').click();

        await page.locator('nav').filter({ hasText: 'SelectSelect AllAdmin' }).getByRole('button').click();

        await page.locator('nav').filter({ hasText: 'SelectSelect AllAdmin' }).getByRole('button').click();

        await page.getByPlaceholder('Select').nth(1).click();

        await page.getByPlaceholder('Select').nth(1).click();

        await page.locator('.MuiSlider-track').isVisible();

        await page.getByRole('tab', { name: 'REPORTS' }).click(); //reports

        await page.waitForURL('**/reports');

        await page.getByRole('tab', { name: 'CHARTS' }).click(); //charts

        await page.waitForURL('**/charts');

        await page.getByLabel('CHARTS').locator('div').first().isVisible();

        const finalURL = page.url();

        expect(finalURL).not.toBe(initialURL);
    });
});
