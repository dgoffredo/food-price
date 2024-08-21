import puppeteer from 'puppeteer';
import process from 'node:process';

const storeLocatorURL = ({zipCode}) => `https://www.keyfood.com/store/keyFood/en/store-locator?query=${zipCode}&radius=40`;

if (process.argv.length !== 3) {
  console.error(`usage: node ${process.argv[1]} ZIP_CODE`);
  process.exit(1);
}
const zipCode = Number(process.argv[2]);

(async () => {
  const sleepMilliseconds = ms => new Promise(r => setTimeout(() => r(), ms));
  const browser = await puppeteer.launch({
    headless: true
  });

  const page = await browser.newPage();
  await page.setViewport({width: 1920, height: 1080});

  const locator = storeLocatorURL({zipCode});
  console.error(`Navigating to store locator: ${locator}...`);
  await page.goto(locator);
  console.error('Sleeping a little (I found that this was necessary)...');
  await sleepMilliseconds(5000);
  console.error('Writing page HTML to standard output...')
  process.stdout.write(await page.$eval('html', el => el.outerHTML));

  await browser.close();
})();
