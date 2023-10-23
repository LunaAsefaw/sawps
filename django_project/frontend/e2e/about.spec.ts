import { test , expect } from '@playwright/test';

let url = '/';


test.describe('about page', () => {
    
    //test.use({ storageState: ".auth/adminAuth.json" });

    test('page elements', async ({page}) => {

        await page.goto(url);

        const buttonSelector = 'div.landing-page-banner-text-btns button:text("ABOUT")';

        await page.waitForSelector(buttonSelector, {timeout: 2000});

        const initialURL = page.url();

        await page.click(buttonSelector);

        await page.waitForURL('**/about/');

        await page.locator('#navbarNav').isVisible();

        await page.locator('.col-12').first().isVisible();

        await page.locator('div').filter({ hasText: 'A centralised wildlife population and trade monitoring system for assessing popu' }).nth(3).click();

        await page.frameLocator('[data-testid="about-page-video-frame"]').getByLabel('Play', { exact: true}).isVisible();
        
        await page.frameLocator('[data-testid="about-page-video-frame"]').locator('video').click();

        await page.getByRole('heading', { name: 'Secure species data storage' }).isVisible();

        await page.getByRole('heading', { name: 'automated state report' }).isVisible();

        await page.getByRole('heading', { name: 'Data analysis and visualisation' }).isVisible();

        await page.getByRole('heading', { name: 'Support National Decision making' }).isVisible();

        await page.getByText('The Wildlife Population system').click();

        const finalURL = page.url();

        expect(finalURL).not.toBe(initialURL);
    });
});
