import { test , expect } from '@playwright/test';

let url = '/';


test.describe('contact page', () => {
    
    //test.use({ storageState: ".auth/adminAuth.json" });

    test('page elements', async ({page}) => {

        await page.goto(url);

        const initialURL = page.url();

        await page.locator('#navbarNav').isVisible();

        await page.locator('#navbarNav').getByRole('link', { name: 'CONTACT' }).click();

        await page.waitForURL('**/contact/');

        await page.locator('Contact Us' ).isVisible();

        await page.locator('input[id="id_name"]').fill("John");

        await page.locator('input[id="id_email"]').fill("johndoe@user.com");

        await page.locator('input[id="id_subject"]').fill("Test");

        await page.locator('textarea[id="id_message"]').fill('Good');

        await page.getByRole('button', { name: 'Send' }).click();

        const finalURL = page.url();

        expect(finalURL).not.toBe(initialURL);
    });
});
