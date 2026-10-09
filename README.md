# Invitación virtual · Reencuentro

Iglesia Adventista del Séptimo Día Empedrado
**Sábado 31 de octubre de 2026**

---

## Archivos

| Archivo | Qué es | Peso |
|---|---|---|
| **`index.html`** | **La invitación.** Un solo archivo, sin dependencias. | 749 KB |
| `respaldo-1080x1920.jpg` | Foto vertical para estado/historia de WhatsApp | 304 KB |
| `respaldo-1080x1350.jpg` | Foto para grupos y publicaciones | 237 KB |
| `og-imagen.jpg` | Miniatura del enlace (WhatsApp, Facebook) | 86 KB |
| `GUIA.md` | Instrucciones para la iglesia, sin nada técnico | — |
| `PROPUESTA.md` | La propuesta original | — |
| `index.base.html` | La plantilla. **Se edita esto, no `index.html`.** | — |
| `herramientas/` | Scripts para regenerar todo | — |

---

## Ver la invitación ahora

```bash
xdg-open /home/j/invitacion-reencuentro/index.html
```

También funciona abriéndola desde el explorador de archivos del celular.

---

## Pendiente antes de publicar

### 1 · Confirmar la hora ⚠️ **bloqueante**

Benedicta escribió en el chat *"desde las 9:30 horas oh 11:00 horas"*, pero su
póster dice **11:00 a. m.** Ahora está en **9:30 – 11:00**. Si se invita a la
hora equivocada, se arruina el evento.

Está en el bloque `CONFIG` de `index.base.html`:

```js
INICIO: '2026-10-31T09:30:00-03:00',
FIN:    '2026-10-31T11:00:00-03:00',
HORA:   '9:30 a. m. a 11:00 a. m.',
```

### 2 · Los demás datos

```js
DIR_CORTA: '',                    // dirección o barrio (opcional)
ENLACE_MAPS: 'https://maps.app.goo.gl/HHZeLZEiyYPyNw5G6?g_st=ac',
WHATSAPP_CONTACTO: '56968585169', // +56 9 6858 5169 — solo dígitos
ENLACE_TRANSMISION: '',           // si hay Facebook/Zoom en vivo
CREDITOS: 'Nos vemos el 31 de octubre',
```

### 3 · Dominio, para que el enlace se vea al compartirlo

En `index.base.html`, línea 14:

```html
<meta property="og:image" content="REEMPLAZA_CON_TU_DOMINIO/og-imagen.jpg">
```

Sin esto el enlace se comparte bien, pero **WhatsApp lo muestra pelado**: sin
imagen y sin título. Es lo que decide si alguien lo abre.

---

## Publicar el enlace (gratis)

| Opción | Cómo |
|---|---|
| **GitHub Pages** | Subir `index.html` y `og-imagen.jpg` a un repo, activar Pages. Dominio propio opcional. El enlace no caduca. |
| **Netlify Drop** | Arrastrar la carpeta a netlify.com/drop. 2 minutos. |
| **Cloudflare Pages** | Dashboard → nuevo proyecto → subir carpeta. |

Mientras no esté publicada, el `.html` se puede mandar por WhatsApp como
documento: abre bien, pero sin vista previa.

---

## Lo que hace la página

- **Compartir por WhatsApp** con el mensaje ya escrito (usa el menú nativo del
  celular si existe; si no, abre `wa.me`)
- **Confirmar asistencia** — abre WhatsApp al **+56 9 6858 5169** con el
  mensaje precargado. Sin base de datos ni formularios
- **Agregar al calendario** — Google Calendar y archivo `.ics` para iOS
- **Cómo llegar** — abre Google Maps con la ruta de la iglesia
- **Cuenta regresiva** en vivo hasta el 31 de octubre
- **Transmisión en vivo** — el botón aparece solo si se configura el enlace
- Barra de progreso de lectura, partículas de latón en la portada (los
  «ríos de luz» de la referencia) y revelado progresivo al bajar. Todo se
  apaga con `prefers-reduced-motion`.

Sin JavaScript, toda la información sigue visible: la cuenta regresiva queda
fija y la invitación se lee completa.

---

## Sobre las tres pinturas

Se usan las tres imágenes de `/home/j/Descargas`, **sin deformar**:

| Lámina | Origen | Recorte | Tamaño final |
|---|---|---|---|
| La Segunda Venida | 700×469 | 0–62% (fuera la multitud del pie) | 1120×464 |
| El Buen Pastor | 500×619 | 0–90% (fuera la firma) | 950×1058 |
| Jesús y el cordero | 500×670 | 0–90,5% (fuera la firma) | 950×1151 |

**Lo importante:** los originales son pequeños (500–700px de ancho) y un
celular de 3x necesita ~915 píxeles reales para una lámina de 305px. Por eso
se re-muestrean con Lanczos + realce suave, y **el ancho de cada lámina está
limitado en CSS** para no ampliar más de lo que el original da. Estirar era lo
que las volvía borrosas.

Para que se vean realmente nítidas harían falta los originales en alta
resolución.

Las firmas del autor se quitaron: la pintura es de otra persona.

---

## Regenerar

```bash
cd /home/j/invitacion-reencuentro

# 1. procesar las pinturas originales → .assets/
python3 herramientas/preparar_fondos.py

# 2. rasterizar el logo oficial a PNG (una vez; se cachea)
node herramientas/logo_png.js

# 3. generar las 3 fotos
python3 herramientas/ver_espacio.py      # ¿cabe todo en el lienzo?
python3 herramientas/generar_imagenes.py

# 4. armar index.html con las imágenes embebidas
python3 herramientas/armar.py

# 5. revisar la página en 5 tamaños de pantalla
node herramientas/ver_pagina.js

# ver cómo queda, en pantallas
node herramientas/capturar.js            # deja las capturas en .capturas/
```

`preparar_fondos.py` y `generar_imagenes.py` tienen los textos al principio:
si cambian la fecha o la hora, se editan ahí y se vuelve a correr.

---

## Los dos verificadores

Ambos usan las mismas funciones que generan, así que avisan de lo mismo que
se dibuja:

- **`ver_espacio.py`** — que el texto de las fotos no se salga del lienzo
- **`ver_pagina.js`** — que la página no desborde, que las pinturas no estén
  deformadas ni ampliadas, y que el texto no se salga de su lámina. Corre en
  320/360/390/430px a 2x y 3x, y en tablet.

---

## Dirección visual

Tinta cálida `#100e0c`, latón `#c9a227`, papel `#e9e1d1`. Spectral para el
texto largo, Inter para las etiquetas. Filetes de 1px en vez de tarjetas, y
un bloque central en papel claro para que la carta respire. Sin sombras
blandas, sin degradados de neón, sin emoji en la página.

El logo oficial va en SVG embebido, dentro de un anillo fino con cuatro
puntos.

---

## Nota sobre las imágenes de los versículos

Las 5 imágenes que mandó Benedicta (Mateo 11:28, Marcos 2:17, Juan 6:37...) se
quedaron fuera: tienen el texto pegado adentro, que se ve borroso y pesa
mucho. Los versículos de la invitación están escritos en la página, con
letra propia. Las tres pinturas nuevas sí van, a tamaño grande y con su
proporción intacta.

> Si en el futuro quieren usar esas imágenes originales en redes públicas,
> conviene confirmar de dónde salieron: varias parecen descargadas o
> generadas con IA y no son de la iglesia.
