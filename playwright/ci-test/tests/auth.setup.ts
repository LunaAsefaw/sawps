import { test as setup, expect } from '@playwright/test';

let url = '/';

let user_email = 'admin@example.com';
let password = 'admin';
const authFile = 'tests/.auth/sawps-auth.json';


setup.describe('login and 2fa-authentication ', () => {

  setup('login and 2fa', async ({page}) => {

    await page.goto(url);

    const buttonSelector = 'div.landing-page-banner-text-btns button:text("LOGIN")';

    await page.waitForSelector(buttonSelector, {timeout: 2000});

    const initialURL = page.url();

    await page.click(buttonSelector);

    await page.waitForURL('**/accounts/login/');

    await expect(page.getByRole('heading', { name: 'Login' })).toBeVisible();

    await page.getByPlaceholder('E-mail address').fill(user_email);
    
    await page.getByPlaceholder('Password').fill(password);
    
    await page.getByRole('button', { name: 'LOGIN' }).click();

    //await page.waitForURL('**/accounts/two-factor/authenticate/');

    //await expect(page.getByRole('heading', { name: 'Two-Factor Authentication' })).toBeVisible();

    //await page.locator('input[id="id_otp_token"]').fill(token);

    //await page.getByRole('button', { name: 'Authenticate' }).click();

    const finalURL = page.url();

    expect(finalURL).not.toBe(initialURL);

    await page.context().storageState({ path: authFile });
    
  });

});
