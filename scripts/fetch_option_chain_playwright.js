#!/usr/bin/env node
const { chromium } = require('playwright');

async function main() {
  const symbol = process.argv[2] || 'NIFTY';
  const targetUrl = `https://www.nseindia.com/api/option-chain-indices?symbol=${encodeURIComponent(symbol)}`;
  const pageUrl = `https://www.nseindia.com/option-chain?symbol=${encodeURIComponent(symbol)}`;
  const fetchTimeoutMs = 15000;

  const browser = await chromium.launch({
    headless: true,
    args: ['--disable-http2'],
  });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    locale: 'en-US',
    viewport: { width: 1440, height: 900 },
    ignoreHTTPSErrors: true,
    extraHTTPHeaders: {
      'accept-language': 'en-US,en;q=0.9',
      'cache-control': 'no-cache',
      'pragma': 'no-cache',
      'referer': pageUrl,
    },
  });

  const page = await context.newPage();
  let capturedPayload = null;

  page.on('response', async (response) => {
    try {
      const url = response.url();
      if (url.includes('/api/option-chain-indices?symbol=')) {
        const text = await response.text();
        const parsed = JSON.parse(text);
        if (parsed && typeof parsed === 'object' && Object.keys(parsed).length > 0) {
          capturedPayload = parsed;
        }
      }
    } catch (_) {}
  });

  try {
    try {
      await page.goto(pageUrl, {
        waitUntil: 'domcontentloaded',
        timeout: 45000,
      });
    } catch (_) {
      // continue anyway and try fetch from page context if some session state exists
    }

    await page.waitForTimeout(5000);

    if (!capturedPayload) {
      const responseText = await page.evaluate(async ({ url, referer, fetchTimeoutMs }) => {
        try {
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), fetchTimeoutMs);
          try {
            const res = await fetch(url, {
              signal: controller.signal,
              credentials: 'include',
              headers: {
                'accept': 'application/json,text/plain,*/*',
              },
            });
            return await res.text();
          } finally {
            clearTimeout(timeoutId);
          }
        } catch (err) {
          return JSON.stringify({ __fetch_error__: String(err), referer });
        }
      }, { url: targetUrl, referer: pageUrl, fetchTimeoutMs });

      const parsed = JSON.parse(responseText);
      if (parsed && typeof parsed === 'object' && Object.keys(parsed).length > 0 && !parsed.__fetch_error__) {
        capturedPayload = parsed;
      }
    }

    process.stdout.write(JSON.stringify(capturedPayload || {}));
  } finally {
    await context.close();
    await browser.close();
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
