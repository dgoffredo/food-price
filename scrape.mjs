import puppeteer from 'puppeteer';
import fs from 'node:fs/promises';

// const storeLocatorURL = 'https://www.keyfood.com/store/keyFood/en/store-locator';
const storeLocatorURL = ({zipCode}) => `https://www.keyfood.com/store/keyFood/en/store-locator?query=${zipCode}&radius=40`;
// https://keyfoodstores.keyfood.com/store/keyFood/en/store-locator?query=10009&radius=40

// Page number is zero-based.
// const catalogURL = page =>
//   `https://urbanmarketplace.keyfood.com/store/urbanMarketplace/en/Departments/c/Departments?sort=name-asc&q=%3AdptSortIndex&page=${page}`;

const catalogURL = ({domain, storeName, page}) =>
  `https://${domain}/store/${storeName}/en/Departments/c/Departments?sort=name-asc&q=%3AdptSortIndex&page=${page}`;

// https://fooduniverse.keyfood.com/store/foodUniverse/en/Departments/c/Departments?q=%3Aname-asc&sort=department&page=${page}
// https://www.keyfood.com/store/keyFood/en/c/Departments?sort=name-asc&q=%3AdptSortIndex%3Anew%3Atrue#
// https://www.keyfood.com/store/keyFood/en/c/Departments?sort=name-asc&q=%3AdptSortIndex%3Anew%3Atrue#
// https://www.keyfood.com/store/keyFood/en/c/Departments?sort=name-asc&q=%3AdptSortIndex%3Anew%3Atrue#

const zipCode = 10009;
// const storeCode = 566;
// const storeCode = 2308;
// const storeCode = 1750;
const storeCode = 1826;

(async () => {
  const sleepMilliseconds = ms => new Promise(r => setTimeout(() => r(), ms));
  // Launch the browser and open a new blank page
  const browser = await puppeteer.launch({
    headless: false
  });

  const page = await browser.newPage();
  await page.setViewport({width: 1920, height: 1080});

  const locator = storeLocatorURL({zipCode});
  console.error(`Navigating to store locator: ${locator}...`);
  await page.goto(locator);
  console.error('Sleeping a little (I found that this was necessary)...');
  await sleepMilliseconds(5000);
  console.error('Waiting for the store to appear in the search results...');
  const catalog = await page.waitForSelector(`button.js-entry__view-catalog[data-store="${storeCode}"]`);
  console.error(await catalog.evaluate(el => el.outerHTML));
  console.error('Clicking on the "view catalog" button for the store and waiting for page load...');
  await Promise.all([
    catalog.click(),
    page.waitForNavigation()
  ]);

  await (async function() {
    // `i` is the page number. We `return` below when it looks like the final
    // page.
    for (let i = 0;; ++i) {
      // Allow for some retries
      const max_attempts = 3;
      let attempt = 0;
      for (; attempt < max_attempts; ++attempt) {
        try {
          const url = catalogURL({
            page: i,
            domain: 'fooduniverse.keyfood.com',
            storeName: 'fooduniverse'
          });
          console.error(`Fetching catalog page ${url}... attempt ${attempt + 1}/${max_attempts}`);
          await page.goto(url);
          const html = await page.$eval('html', el => el.outerHTML);
          const html_file_path = `${i}.html`;
          await fs.writeFile(html_file_path, html);
          console.log(html_file_path);
          const next = await page.waitForSelector('li.pagination-next');
          const className = await next.evaluate(el => el.className);
          if (className.split(' ').includes('disabled')) {
            console.error("That was the last page.");
            return;
          }
          break;
        } catch (error) {
          console.error(error);
        }
      }
      if (attempt === max_attempts) {
        console.error('Too many failures.');
        process.exit(1);
      }
    }
  }());

  await browser.close();
})();
