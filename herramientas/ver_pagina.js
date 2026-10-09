const { chromium } = require('/home/j/teolingo-v2/node_modules/playwright');
const path = require('path');

/* Revisa la invitación en varios tamaños de celular y de tablet.
 *
 * Tres cosas que se rompen fácil y no se ven en una sola captura:
 *   1. desborde horizontal (el scroll lateral en el celular)
 *   2. deformación de las pinturas: si la proporción mostrada no es la real,
 *      la imagen está estirada — que era el defecto anterior
 *   3. ampliación: una pintura mostrada a más píxeles de los que tiene se ve
 *      borrosa. Se mide en píxeles de DISPOSITIVO, que es como se ve de verdad
 *
 * Uso:  node herramientas/ver_pagina.js
 * Sale con código 1 si algo falla.
 */

const RAIZ = path.dirname(__dirname);
const PAGINA = 'file://' + path.join(RAIZ, 'index.html');

const TAMANOS = [
  { w: 320, h: 568, dpr: 2, nombre: 'iPhone SE (chico)' },
  { w: 360, h: 640, dpr: 3, nombre: 'Android de gama baja' },
  { w: 390, h: 844, dpr: 3, nombre: 'iPhone 12/13/14' },
  { w: 430, h: 932, dpr: 3, nombre: 'iPhone Pro Max' },
  { w: 768, h: 1024, dpr: 2, nombre: 'tablet' },
];

const TOLERANCIA = 0.02;   // 2% de diferencia de proporción

async function esperarImagenes(page) {
  await page.evaluate(async () => {
    // baja hasta el final para disparar loading="lazy"
    const alto = document.body.scrollHeight;
    for (let y = 0; y < alto; y += 300) {
      window.scrollTo(0, y);
      await new Promise(r => setTimeout(r, 40));
    }
    window.scrollTo(0, 0);
  });
  await page.waitForFunction(() =>
    [...document.images].every(i => i.complete && i.naturalWidth > 0),
    null, { timeout: 10000 }
  ).catch(() => {});
  // las animaciones de entrada se disparan al bajar
  await page.evaluate(async () => {
    const alto = document.body.scrollHeight;
    for (let y = 0; y < alto; y += 400) {
      window.scrollTo(0, y);
      await new Promise(r => setTimeout(r, 60));
    }
  });
  await page.waitForTimeout(700);
}

(async () => {
  const browser = await chromium.launch({
    executablePath: '/home/j/.cache/ms-playwright/chromium-1247/chrome-linux64/chrome',
    args: ['--no-sandbox', '--disable-gpu'],
  });

  let fallos = 0;

  for (const t of TAMANOS) {
    const page = await browser.newPage({
      viewport: { width: t.w, height: t.h },
      deviceScaleFactor: t.dpr,
      isMobile: true,
      hasTouch: true,
    });
    const errores = [];
    page.on('pageerror', e => errores.push(e.message));

    await page.goto(PAGINA, { waitUntil: 'networkidle' });
    await esperarImagenes(page);

    const r = await page.evaluate((dpr) => {
      const doc = document.documentElement;
      const laminas = [...document.querySelectorAll('figure.lamina img')].map(img => {
        const b = img.getBoundingClientRect();
        const real = img.naturalWidth / img.naturalHeight;
        const vista = b.width / b.height;
        return {
          nombre: (img.alt || '').slice(0, 28) || '(sin alt)',
          natural: `${img.naturalWidth}×${img.naturalHeight}`,
          deforma: Math.abs(real - vista) / real > 0.02,
          // píxeles de dispositivo que ocupa en pantalla
          pixelesPantalla: Math.round(b.width * dpr),
          // > 1 significa que se está ampliando
          ampliacion: +(b.width * dpr / img.naturalWidth).toFixed(2),
        };
      });

      // el texto del momento tiene que caber dentro de su lámina
      const txt = document.querySelector('.momento-texto');
      const lam = document.querySelector('.momento .lamina');
      let momento = null;
      if (txt && lam) {
        const tr = txt.getBoundingClientRect();
        const lr = lam.getBoundingClientRect();
        momento = tr.bottom <= lr.bottom + 1 &&
                  tr.left >= -0.5 && tr.right <= window.innerWidth + 0.5;
      }

      return {
        desborde: doc.scrollWidth > window.innerWidth + 1,
        anchoDoc: doc.scrollWidth,
        anchoVentana: window.innerWidth,
        laminas,
        momento,
        // scrollHeight a veces es undefined en documentos sin layout de flujo;
        // el alto real se mide sobre el último hijo
        alto: Math.round(Math.max(
          document.body.scrollHeight || 0,
          document.body.offsetHeight || 0,
          (document.body.lastElementChild &&
            document.body.lastElementChild.getBoundingClientRect().bottom + window.scrollY) || 0
        )),
      };
    }, t.dpr);

    const problemas = [];
    if (r.desborde) problemas.push(`desborda ${r.anchoDoc}>${r.anchoVentana}px`);
    for (const l of r.laminas) {
      if (l.deforma) problemas.push(`"${l.nombre}" deformada (${l.natural})`);
      if (l.ampliacion > 1) {
        problemas.push(`"${l.nombre}" ampliada ${l.ampliacion}x (${l.natural})`);
      }
    }
    if (r.momento === false) problemas.push('el texto del momento se sale');

    if (problemas.length) {
      fallos += problemas.length;
      console.log(`✗ ${t.nombre.padEnd(24)} ${t.w}×${t.h}@${t.dpr}x`);
      for (const p of problemas) console.log(`    ${p}`);
    } else {
      const maxAmp = Math.max(...r.laminas.map(l => l.ampliacion));
      console.log(`✓ ${t.nombre.padEnd(24)} ${String(t.w).padStart(3)}×${t.h}@${t.dpr}x  ` +
                  `láminas a ${maxAmp}x de su resolución · alto ${r.alto}px`);
    }

    if (errores.length) {
      fallos += errores.length;
      console.log(`    errores JS: ${errores.join(' | ')}`);
    }

    await page.close();
  }

  await browser.close();
  console.log(fallos ? `\n${fallos} problema(s).` : '\nTodo en orden.');
  process.exit(fallos ? 1 : 0);
})();