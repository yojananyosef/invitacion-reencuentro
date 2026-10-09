const { chromium } = require('/home/j/teolingo-v2/node_modules/playwright');
const path = require('path');
const fs = require('fs');

/* Rasteriza el logo oficial de la Iglesia Adventista a PNG con fondo
   transparente, para poder pegarlo en las imágenes estáticas.
   El logo viene como SVG: PIL no lo dibuja, el navegador sí. */

const SVG = fs.readFileSync(path.join(__dirname, 'logo-ia.svg'), 'utf8');
const SALIDA = path.join(__dirname, '..', '.assets', 'logo-ia.png');
const PX = 512;

(async () => {
  const browser = await chromium.launch({
    executablePath: '/home/j/.cache/ms-playwright/chromium-1247/chrome-linux64/chrome',
    args: ['--no-sandbox', '--disable-gpu'],
  });
  const page = await browser.newPage({
    viewport: { width: PX, height: PX },
    deviceScaleFactor: 1,
  });

  await page.setContent(`<!doctype html><meta charset="utf-8">
    <style>
      html,body{margin:0;background:transparent}
      body{width:${PX}px;height:${PX}px;display:grid;place-items:center}
      svg{width:${PX * 0.86}px;height:auto;color:#C6A15B}
    </style>${SVG}`);

  await page.waitForTimeout(400);
  await page.screenshot({ path: SALIDA, omitBackground: true });

  const kb = fs.statSync(SALIDA).size / 1024;
  console.log(`✓ logo-ia.png  ${PX}x${PX}  ${kb.toFixed(0)} KB`);

  await browser.close();
})();