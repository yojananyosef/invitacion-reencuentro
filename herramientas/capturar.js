const { chromium } = require('/home/j/teolingo-v2/node_modules/playwright');
const path = require('path');

/* Captura la invitación como la ve un celular de 390x844.
   Uso:  node herramientas/capturar.js
   Deja las capturas en .capturas/ (se ignoran al publicar). */

(async () => {
  const raiz = path.dirname(__dirname);
  const salida = path.join(raiz, '.capturas');

  const browser = await chromium.launch({
    executablePath: '/home/j/.cache/ms-playwright/chromium-1247/chrome-linux64/chrome',
    args: ['--no-sandbox', '--disable-gpu'],
  });
  const page = await browser.newPage({
    viewport: { width: 390, height: 844 },
    deviceScaleFactor: 2,
    isMobile: true,
    hasTouch: true,
  });

  const errores = [];
  page.on('console', m => { if (m.type() === 'error') errores.push(m.text()); });
  page.on('pageerror', e => errores.push('PAGEERROR: ' + e.message));

  await page.goto('file://' + path.join(raiz, 'index.html'), { waitUntil: 'networkidle' });
  await page.waitForTimeout(1200);

  // baja y sube para disparar las animaciones de entrada
  await page.evaluate(async () => {
    const h = document.body.scrollHeight;
    for (let y = 0; y < h; y += 400) {
      window.scrollTo(0, y);
      await new Promise(r => setTimeout(r, 60));
    }
    window.scrollTo(0, 0);
    await new Promise(r => setTimeout(r, 500));
  });
  await page.waitForTimeout(600);

  const alto = await page.evaluate(() => document.body.scrollHeight);
  const n = Math.ceil(alto / 844);
  for (let i = 0; i < n; i++) {
    await page.evaluate(y => window.scrollTo(0, y), i * 844);
    await page.waitForTimeout(350);
    const num = String(i).padStart(2, '0');
    await page.screenshot({ path: path.join(salida, `pantalla-${num}.png`) });
  }
  await page.screenshot({ path: path.join(salida, 'completa.png'), fullPage: true });

  const cuenta = await page.evaluate(() => ({
    dias: document.getElementById('c-d').textContent,
    horas: document.getElementById('c-h').textContent,
    min: document.getElementById('c-m').textContent,
    seg: document.getElementById('c-s').textContent,
  }));

  console.log(`altura: ${alto}px · ${n} capturas en .capturas/`);
  console.log('cuenta regresiva:', JSON.stringify(cuenta));
  console.log('errores de consola:', errores.length ? errores : 'ninguno');

  await browser.close();
})();