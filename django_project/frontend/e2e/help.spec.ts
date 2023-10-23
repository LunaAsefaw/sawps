import { test , expect } from '@playwright/test';

let url = '/';


test.describe('help page', () => {
    
    //test.use({ storageState: ".auth/adminAuth.json" });

    test('page elements', async ({page}) => {

        await page.goto(url);

        const initialURL = page.url();

        await page.locator('#navbarNav').isVisible();

        await page.locator('#navbarNav').getByRole('link', { name: 'HELP' }).click();

        await page.waitForURL('**/help/');

        const helpURL = page.url();

        await page.locator('section').getByText('HELP').isVisible();
        
        await page.getByRole('img', { name: 'Help Banner' }).isVisible();

        await page.getByText(
            'The SAWPS platform offers a broad range of features which are documented in a fu'
            ).isVisible();

        await page.getByRole('button', {name: 'Go to user guide'}).isVisible();

        await page.goto(helpURL);

        await page.getByRole('button', {name: 'Contact us'}).click();

        await page.waitForURL('**/contact/');

        const finalURL = page.url();

        expect(finalURL).not.toBe(initialURL);
    });
});
