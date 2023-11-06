import { test , expect } from '@playwright/test';

let url = process.env.STAGING;



test.describe('Data Upload page', () => {
    
    test.use({ storageState: "tests/.auth/sawps-auth.json" });

    test('user interaction', async ({page}) => {

        await page.goto(url);

        const initialURL = page.url();

        await page.locator('#navbarNav').isVisible();

        const buttonSelector = 'div.landing-page-banner-text-btns button:text("UPLOAD YOUR DATA")';

        await page.waitForSelector(buttonSelector, {timeout: 2000});

        await page.click(buttonSelector);

        await page.waitForURL('**/upload');

        await page.getByLabel('Map').isVisible();

        await page.getByRole('button', { name: 'CREATE A NEW PROPERTY' }).click();

        await page.locator('#input_propertyname').fill('admin2');

        await page.getByRole('row', { name: 'Open/Closed System ​' }).getByLabel('​').click();
  
        await page.getByRole('option', { name: 'Open', exact: true }).click();

        await page.getByRole('row', { name: 'Property Type ​' }).getByLabel('​').click();  

        await page.getByRole('option', { name: 'Private', exact: true }).click();

        //await page.getByLabel('STEP 1').getByLabel('​', { exact: true }).click();

        //await page.getByRole('option', { name: 'Gauteng' }).click();

        await page.getByRole('button', { name: 'SAVE PROPERTY INFORMATION' }).click();

        await page.getByRole('button', { name: 'UPLOAD' }).click();

        const fileChooserPromise = page.waitForEvent('filechooser');

        await page.getByText('Browse').click();

        const fileChooser = await fileChooserPromise;

        await fileChooser.setFiles('tests/fixtures/parcel.geojson');

        await page.getByRole('button', { name: 'UPLOAD FILES' }).click();

        await page.getByRole('button', { name: 'SAVE BOUNDARY' }).click();

        const finalURL = page.url();

        expect(finalURL).not.toBe(initialURL);
    });
});
