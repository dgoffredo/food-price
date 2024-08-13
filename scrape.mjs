import puppeteer from 'puppeteer';
import fs from 'node:fs/promises';

const storeLocatorURL = 'https://www.keyfood.com/store/keyFood/en/store-locator';

// Page number is zero-based.
const catalogURL = page =>
  `https://urbanmarketplace.keyfood.com/store/urbanMarketplace/en/Departments/c/Departments?sort=name-asc&q=%3AdptSortIndex&page=${page}`;

(async () => {
  const sleepMilliseconds = ms => new Promise(r => setTimeout(() => r(), ms));
  // Launch the browser and open a new blank page
  const browser = await puppeteer.launch({
    product: 'firefox',
    protocol:'webDriverBiDi',
    headless: true
  });

  const page = await browser.newPage();
  await page.setViewport({width: 1920, height: 1080});

  console.error(`Navigating to store locator: ${storeLocatorURL}...`);
  await page.goto(storeLocatorURL);
  console.error('Waiting for the store locator query entry to load...');
  const entry = await page.waitForSelector('#storelocator-query');
  console.error('Typing zip code into store locator query entry...');
  await entry.type('10009');
  console.error('Clicking on the submit button and waiting for page load...');
  await Promise.all([
    page.click('#js-btn-store-finder-submit'),
    page.waitForNavigation()
  ]);
  console.error('Sleeping a little (I found that this was necessary)...');
  await sleepMilliseconds(5000);
  console.error('Waiting for the store to appear in the search results...');
  const catalog = await page.waitForSelector('button.js-entry__view-catalog[data-store="566"]');
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
          console.error(`Fetching catalog page ${i}... attempt ${attempt + 1}/${max_attempts}`);
          await page.goto(catalogURL(i));
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
