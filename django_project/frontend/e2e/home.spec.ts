import { test , expect } from '@playwright/test';

let url = '/';


test.describe('landing page', () => {
    
    //test.use({ storageState: ".auth/adminAuth.json" });

    test('page elements', async ({page}) => {

        await page.goto(url);

        await page.locator('#navbarNav').isVisible();

        await page.locator('#navbarNav').getByRole('link', { name: 'ABOUT' }).isVisible();

        await page.locator('#navbarNav').getByRole('link', { name: 'HELP' }).isVisible();

        await page.locator('#navbarNav').getByRole('link', { name: 'CONTACT' }).isVisible();

        await page.locator('#navbarNav').getByRole('link', { name: 'LOGIN' }).isVisible();

        await page.locator('#navbarNav').getByRole('link', { name: 'REGISTER' }).isVisible();

        await page.getByTestId('landing-page-banner-image').isVisible();

        await page.getByTestId('landing-page-population-overview-container').isVisible();
        
        await page.getByTestId('footer').isVisible();

    });
});
