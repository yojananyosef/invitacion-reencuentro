#!/usr/bin/env python3
"""Genera las imágenes estáticas de la invitación.

Plan B: se envían por WhatsApp como foto y funcionan aunque la persona no
abra ningún enlace.

  respaldo-1080x1920.jpg  historia / estado de WhatsApp (9:16)
  respaldo-1080x1350.jpg  feed / publicación (4:5)
  og-imagen.jpg           miniatura del enlace (1200x630)

REGLA: NADA se amplía. Las pinturas originales son pequeñas (700px de ancho
la más grande). `lamina()` calcula el mayor tamaño que NO supera la
resolución original y devuelve la pieza con ese tamaño. Si el hueco disponible
es más grande que la pintura, se agranda el hueco, no la imagen: se prefiere
aire en blanco a una imagen borrosa.

La composición se declara una sola vez como lista de bloques, así el que
dibuja y el que verifica usan exactamente la misma estructura.
"""
from PIL import (Image, ImageDraw, ImageFont, ImageFilter, ImageOps,
                 ImageChops, ImageEnhance)
import os
import random

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(RAIZ, ".assets")
FUENTES = os.path.join(RAIZ, ".fuentes")
SALIDA = RAIZ

PLAYFAIR = os.path.join(FUENTES, "PlayfairDisplay-var.ttf")
PLAYFAIR_I = os.path.join(FUENTES, "PlayfairDisplay-Italic-var.ttf")
MONTSERRAT = os.path.join(FUENTES, "Montserrat-var.ttf")
LOGO = os.path.join(ASSETS, "logo-ia.png")

# paleta tomada de la referencia: tinta cálida + latón
NOCHE = (16, 14, 12)
NOCHE_2 = (23, 20, 18)
ORO = (201, 162, 39)
ORO_CLARO = (232, 205, 126)
PAPEL = (233, 225, 209)
PAPEL_2 = (207, 196, 174)
PAPEL_3 = (154, 143, 124)
REGLA = (51, 44, 37)

TITULO = "Reencuentro"
LEMA = ["¿Vale la pena regresar?", "Alguien ora por ti."]
IGLESIA = ["IGLESIA ADVENTISTA DEL SÉPTIMO DÍA", "EMPEDRADO"]
FECHA = "SÁBADO 31 DE OCTUBRE DE 2026"
HORA = "9:30 a. m. — 12:00 m."
LUGAR = "Iglesia Adventista Empedrado"
SALMO = "“Al que a mí viene, no le echaré fuera.”  Juan 6:37"
CIERRE = "¡Ya te esperamos!"
PIE = "Nos vemos el 31 de octubre"


def f(path, size, weight="Regular"):
    ft = ImageFont.truetype(path, size)
    try:
        ft.set_variation_by_name(weight)
    except Exception:
        pass
    return ft


# ══════════════════════════════════════════════════════════ texto
def ancho(ft, txt, tracking=0):
    return (ft.getlength(txt) if txt else 0) + tracking * max(0, len(txt) - 1)


def alto(ft, txt):
    b = ft.getbbox(txt)
    return b[3] - b[1]


def dibujar_tracking(d, x, y, txt, ft, fill, tracking=0, centro=None):
    total = ancho(ft, txt, tracking)
    if centro is not None:
        x = centro - total / 2
    for ch in txt:
        d.text((x, y), ch, font=ft, fill=fill)
        x += ft.getlength(ch) + tracking
    return total


def envolver(ft, txt, max_w, tracking=0):
    lineas, actual = [], ""
    for p in txt.split():
        prueba = f"{actual} {p}".strip()
        if ancho(ft, prueba, tracking) <= max_w or not actual:
            actual = prueba
        else:
            lineas.append(actual)
            actual = p
    if actual:
        lineas.append(actual)
    return lineas


def ajustar(ruta, txt, max_w, size_inicial, weight="Regular", tracking=0):
    """Baja el cuerpo hasta que el texto quepa en max_w."""
    s = size_inicial
    while s > 8 and ancho(f(ruta, s, weight), txt, tracking) > max_w:
        s -= 2
    return f(ruta, s, weight)


# ══════════════════════════════════════════════════════════ piezas
def texto(txt, ft, fill, tracking=0):
    off = int(ft.getbbox(txt)[1])

    def dib(im, cx, y):
        dibujar_tracking(ImageDraw.Draw(im), cx, y - off, txt, ft, fill,
                         tracking, centro=cx)
    return {"alto": alto(ft, txt), "dibuja": dib, "txt": txt, "ft": ft}


def texto_centro(txt, ft, c1, c2, tracking=0):
    """Relleno degradado. Se dibuja desplazado para que la tinta ocupe
    exactamente el alto declarado."""
    h_texto = alto(ft, txt)
    caja_h = int(h_texto * 1.4)
    off = int(ft.getbbox(txt)[1])

    def dib(im, cx, y):
        w, h = im.size
        m = Image.new("L", (int(ancho(ft, txt, tracking)) + 60, caja_h), 0)
        dibujar_tracking(ImageDraw.Draw(m), m.size[0] / 2, -off, txt, ft, 255,
                         tracking, centro=m.size[0] / 2)
        destino = Image.new("L", (w, h), 0)
        destino.paste(m, (int(cx - m.size[0] / 2), int(y)))
        tira = Image.new("RGB", (m.size[0], h_texto + 1))
        px = tira.load()
        for i in range(h_texto + 1):
            t = (i / max(1, h_texto)) ** 0.7
            color = tuple(int(c1[k] + (c2[k] - c1[k]) * t) for k in range(3))
            for x in range(tira.size[0]):
                px[x, i] = color
        im.paste(tira.resize((w, h), Image.NEAREST), (0, 0), destino)

    return {"alto": h_texto, "dibuja": dib, "txt": txt, "ft": ft}


def parrafo(txt, ft, fill, max_w, inter=1.6, tracking=0):
    lineas = envolver(ft, txt, max_w, tracking)
    h_linea = ft.size * inter
    offs = [int(ft.getbbox(ln)[1]) for ln in lineas]

    def dib(im, cx, y):
        d = ImageDraw.Draw(im)
        for i, ln in enumerate(lineas):
            dibujar_tracking(d, cx, y + i * h_linea - offs[i], ln, ft, fill,
                             tracking, centro=cx)

    return {"alto": int(h_linea * (len(lineas) - 1) + alto(ft, lineas[-1])),
            "dibuja": dib}


def filete(largo=150, color=ORO, grosor=2):
    def dib(im, cx, y):
        d = ImageDraw.Draw(im)
        d.line([(cx - largo, y), (cx - 18, y)], fill=color, width=grosor)
        d.line([(cx + 18, y), (cx + largo, y)], fill=color, width=grosor)
        d.polygon([(cx, y - 5), (cx + 5, y), (cx, y + 5), (cx - 5, y)], fill=color)
    return {"alto": 12, "dibuja": dib}


def capsula(txt, ft, tracking=5, relleno=NOCHE_2, color=ORO_CLARO):
    w_texto = ancho(ft, txt, tracking)
    pad_x, pad_y = 44, 26
    h = alto(ft, txt) + pad_y * 2 + int(ft.getbbox(txt)[1])

    def dib(im, cx, y):
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((cx - w_texto / 2 - pad_x, y, cx + w_texto / 2 + pad_x,
                             y + h), radius=h / 2, fill=relleno, outline=ORO, width=3)
        dibujar_tracking(d, cx, y + pad_y, txt, ft, color, tracking, centro=cx)
    return {"alto": h, "dibuja": dib}


def sello(anillo=140, logo_px=None, color=ORO):
    """Logo oficial en un anillo fino con cuatro puntos."""
    logo_px = logo_px if logo_px is not None else int(anillo * 0.56)

    def dib(im, cx, y):
        capa = Image.new("RGBA", im.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(capa)
        r = anillo / 2
        d.ellipse((cx - r, y, cx + r, y + anillo), outline=color + (140,), width=2)
        r2 = r - 9
        d.ellipse((cx - r2, y + 9, cx + r2, y + anillo - 9),
                  outline=color + (60,), width=1)
        for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            d.ellipse((cx + dx * r - 2, y + anillo / 2 + dy * r - 2,
                       cx + dx * r + 2, y + anillo / 2 + dy * r + 2),
                      fill=color + (200,))
        lg = Image.open(LOGO).convert("RGBA").resize(
            (logo_px, logo_px), Image.LANCZOS)
        capa.alpha_composite(lg, (int(cx - logo_px / 2),
                                  int(y + anillo / 2 - logo_px / 2)))
        im.paste(capa, (0, 0), capa)
    return {"alto": anillo, "dibuja": dib}


def lamina(ruta_img, ancho_max, alto_max=None):
    """La pintura tal cual, con su proporción, enmarcada con una línea fina.

    NO amplía: si el hueco pedido es mayor que la pintura, se devuelve la
    pintura a su tamaño real y el sobrante queda como aire. Deformarla para
    llenar el hueco es lo que la dejaba borrosa y chueca.
    """
    src = Image.open(ruta_img).convert("RGB")
    w0, h0 = src.size
    esc = min(ancho_max / w0, 1.0)
    if alto_max:
        esc = min(esc, alto_max / h0)
    w = max(1, int(w0 * esc))
    h = max(1, int(h0 * esc))
    cuadro = src.resize((w, h), Image.LANCZOS)
    marco = 8

    def dib(im, cx, y):
        x = int(cx - w / 2)
        yy = int(y - marco)
        im.paste(cuadro, (x + marco, yy + marco))
        d = ImageDraw.Draw(im)
        d.rectangle((x, yy, x + w + marco * 2 - 1, yy + h + marco * 2 - 1),
                    outline=ORO, width=marco)
        # esquinas: dan el aire de lámina de museo
        for ex, ey, sx, sy in ((x, yy, 1, 1),
                               (x + w + marco * 2, yy, -1, 1),
                               (x, yy + h + marco * 2, 1, -1),
                               (x + w + marco * 2, yy + h + marco * 2, -1, -1)):
            d.line([(ex, ey), (ex + sx * 22, ey)], fill=ORO_CLARO, width=3)
            d.line([(ex, ey), (ex, ey + sy * 22)], fill=ORO_CLARO, width=3)

    return {"alto": h + marco * 2, "ancho": w + marco * 2, "dibuja": dib}


# ══════════════════════════════════════════════════════════ composición
def flujo(im, y, piezas, separaciones, x_centro=None):
    cx = im.size[0] / 2 if x_centro is None else x_centro
    for i, p in enumerate(piezas):
        p["dibuja"](im, cx, y)
        y += p["alto"]
        if i < len(separaciones):
            y += separaciones[i]
    return y


def medir(piezas, separaciones):
    return sum(p["alto"] for p in piezas) + sum(separaciones)


def alto_total(bloques):
    return sum(sep + medir(piezas, seps) for sep, piezas, seps in bloques)


def dibujar_bloques(im, bloques, y_inicial, x_centro=None):
    y = y_inicial
    for sep, piezas, seps in bloques:
        y = flujo(im, y + sep, piezas, seps, x_centro=x_centro)
    return y


def _bloques(w, margen, con_versiculo=True, escala=1.0):
    """Composición de un formato. `escala` multiplica los cuerpos y los
    espacios; los formatos de WhatsApp no son proporcionales entre sí, así que
    cada uno busca la suya.

    La lámina NO se escala: va siempre a su resolución real. Si sobra sitio,
    el aire se queda de aire.
    """
    util = w - 2 * margen
    base = (w / 1080) * escala
    k = lambda n: max(8, int(n * base))            # noqa: E731

    ft_t = ajustar(PLAYFAIR, TITULO, util, k(158), "Medium")
    ft_l = ajustar(PLAYFAIR_I, LEMA[0], util, k(52), "Regular")
    ft_h = ajustar(PLAYFAIR, HORA, util, k(54), "Medium")
    ft_g = ajustar(PLAYFAIR, LUGAR, util, k(54), "Medium")
    ft_c = ajustar(PLAYFAIR, CIERRE, util, k(80), "Medium")

    lam = lamina(os.path.join(ASSETS, "segunda-venida.jpg"), int(util))

    bloques = [
        (0, [sello(k(142), k(78)),
             texto(IGLESIA[0], f(MONTSERRAT, k(24), "Medium"), PAPEL_2, 4),
             texto(IGLESIA[1], f(MONTSERRAT, k(24), "Medium"), PAPEL_2, 4)],
         [k(24), k(14), k(5)]),

        (k(72), [texto_centro(TITULO, ft_t, (233, 225, 209), ORO),
                 filete(k(165)),
                 texto(LEMA[0], ft_l, ORO_CLARO),
                 texto(LEMA[1], ft_l, ORO_CLARO)],
         [k(40), k(40), k(7)]),

        (k(76), [lam], []),

        (k(76), [capsula(FECHA, f(MONTSERRAT, k(36), "Medium"), 5),
                 texto(HORA, ft_h, PAPEL),
                 texto(LUGAR, ft_g, PAPEL)],
         [k(54), k(28), k(9)]),
    ]

    if con_versiculo:
        bloques.append(
            (k(78), [filete(k(120), (108, 90, 54)),
                     parrafo(SALMO, f(PLAYFAIR_I, k(38), "Regular"), PAPEL_2,
                             int(util)),
                     texto_centro(CIERRE, ft_c, (233, 225, 209), ORO)],
             [k(36), k(56), k(26)]))
        bloques.append(
            (k(60), [sello(k(80), k(44)),
                     texto(PIE, f(MONTSERRAT, k(22), "Medium"), PAPEL_3, 3)],
             [k(17), k(12)]))
    else:
        bloques.append(
            (k(74), [filete(k(110), (108, 90, 54)),
                     texto_centro(CIERRE, ft_c, (233, 225, 209), ORO),
                     texto(PIE, f(MONTSERRAT, k(21), "Medium"), PAPEL_3, 3)],
             [k(34), k(40), k(0)]))

    return bloques


def _encajar(w, margen, alto_lienzo, con_versiculo, aire_min=64):
    """Busca la mayor escala con la que la composición entra con aire.

    Baja primero el cuerpo de letra; solo si con el cuerpo mínimo todavía no
    entra, cierra el margen lateral. Al revés se taparía el texto antes de
    que la pintura empiece a verse pequeña.
    """
    # y_inicial nunca deja menos de `minimo` arriba, así que el aire que hay
    # que garantizar es el de abajo: (alto_lienzo - minimo - alto_total)
    minimo = 70 if alto_lienzo > 1500 else 48
    def entra(bloques):
        return alto_lienzo - minimo - alto_total(bloques) >= aire_min

    escala = 1.0
    while escala >= 0.40:
        bloques = _bloques(w, int(w * margen), con_versiculo, escala)
        if entra(bloques):
            return bloques
        escala -= 0.04

    m = margen
    while m >= 0.04:
        bloques = _bloques(w, int(w * m), con_versiculo, 0.40)
        if entra(bloques):
            return bloques
        m -= 0.01

    return _bloques(w, int(w * 0.04), con_versiculo, 0.40)


def y_inicial(h, bloques, aire_min=64):
    """Arranque de la composición. El aire sobrante se reparte con un poco
    más de peso arriba que abajo (0.42), que es como se centra un cartel.

    Nunca deja el contenido pegado al borde inferior: si el aire no alcanza
    para el reparto, se queda arriba y el sobrante queda como aire limpio.
    """
    libre = h - alto_total(bloques)
    minimo = 70 if h > 1500 else 48
    if libre < minimo + aire_min:
        return minimo
    return max(minimo, int(libre * 0.42))


# ══════════════════════════════════════════════════════════ fondos
def fondo(w, h, luz=(0.5, 0.3)):
    """Tinta casi negra con una luz cálida muy contenida.

    El halo va al 12% y muy difuso: si sube, el papel se vuelve marrón y deja
    de leerse como tinta. La referencia (ellen-white-cronologia) usa #100e0c
    con la luz apenas insinuada.
    """
    base = Image.new("RGB", (w, h), NOCHE)
    halo = Image.new("L", (w, h), 0)
    cx, cy = int(w * luz[0]), int(h * luz[1])
    r = int(max(w, h) * 0.62)
    ImageDraw.Draw(halo).ellipse((cx - r, cy - r, cx + r, cy + r), fill=30)
    halo = halo.filter(ImageFilter.GaussianBlur(int(max(w, h) * 0.2)))
    gris = Image.merge("RGB", (halo, halo, halo))
    base = ImageChops.screen(base, ImageChops.multiply(
        Image.new("RGB", (w, h), (52, 40, 20)), gris))
    vin = Image.new("L", (w, h), 0)
    ImageDraw.Draw(vin).ellipse((-w * 0.3, -h * 0.2, w * 1.3, h * 1.2), fill=255)
    vin = vin.filter(ImageFilter.GaussianBlur(int(max(w, h) * 0.15)))
    vin = vin.point(lambda v: 58 + int(v * 0.72))
    return ImageChops.multiply(base, Image.merge("RGB", (vin, vin, vin)))


def grano(im):
    random.seed(11)
    px = im.load()
    w, h = im.size
    for _ in range(int(w * h / 11)):
        x, y = random.randrange(w), random.randrange(h)
        r, g, b = px[x, y]
        n = random.randint(-5, 5)
        px[x, y] = (max(0, min(255, r + n)), max(0, min(255, g + n)),
                    max(0, min(255, b + n)))


def guardar(im, nombre):
    ruta = os.path.join(SALIDA, nombre)
    im.save(ruta, "JPEG", quality=88, optimize=True, progressive=True,
            subsampling=0)
    print(f"  {nombre:26s} {im.size[0]}x{im.size[1]}  "
          f"{os.path.getsize(ruta)/1024:6.0f} KB")


# ══════════════════════════════════════════════════════════ formatos
def historia():
    w, h = 1080, 1920
    im = fondo(w, h, luz=(0.5, 0.28))
    bloques = _encajar(w, 0.11, h, con_versiculo=True)
    dibujar_bloques(im, bloques, y_inicial(h, bloques))
    grano(im)
    guardar(im, "respaldo-1080x1920.jpg")


def feed():
    w, h = 1080, 1350
    im = fondo(w, h, luz=(0.5, 0.26))
    bloques = _encajar(w, 0.10, h, con_versiculo=False)
    dibujar_bloques(im, bloques, y_inicial(h, bloques))
    grano(im)
    guardar(im, "respaldo-1080x1350.jpg")


def miniatura():
    """1200x1200 — la vista previa del enlace.

    POR QUÉ CUADRADA Y NO 1200x630
    ------------------------------
    WhatsApp no muestra la imagen completa: la recorta a un cuadrado chiquito
    al lado del título. Con una imagen de 1200x630 el recorte se lleva el
    título "Reencuentro" y la mitad del logo — que es justo lo que se veía en
    el chat. Cuadrada entra entera en cualquier recorte.

    La información importante va en el CENTRO, dentro de un cuadrado de 900px,
    que es lo que sobrevive al recorte más agresivo.
    """
    w = h = 1200
    im = fondo(w, h, luz=(0.5, 0.34))

    # lo que importa vive dentro de este cuadrado central
    cx, cy = w / 2, h / 2 - 20
    util = 700          # el título entra completo en un recorte de 700px

    sello(150, 80)["dibuja"](im, cx, cy - 372)
    d = ImageDraw.Draw(im)
    d.text((cx, cy - 176), IGLESIA[0], font=f(MONTSERRAT, 21, "Medium"),
           fill=PAPEL_2, anchor="ma")
    d.text((cx, cy - 146), IGLESIA[1], font=f(MONTSERRAT, 21, "Medium"),
           fill=PAPEL_2, anchor="ma")

    texto_centro(TITULO, ajustar(PLAYFAIR, TITULO, util, 122, "Medium"),
                 (233, 225, 209), ORO)["dibuja"](im, cx, cy - 62)
    filete(150)["dibuja"](im, cx, cy + 84)

    d.text((cx, cy + 128), LEMA[0], font=f(PLAYFAIR_I, 34, "Regular"),
           fill=ORO_CLARO, anchor="ma")
    d.text((cx, cy + 178), LEMA[1], font=f(PLAYFAIR_I, 34, "Regular"),
           fill=ORO_CLARO, anchor="ma")

    capsula("SÁBADO 31 DE OCTUBRE", f(MONTSERRAT, 25, "Medium"),
            5)["dibuja"](im, cx, cy + 252)

    d.text((cx, cy + 372), HORA,
           font=ajustar(PLAYFAIR, HORA, util, 36, "Medium"),
           fill=PAPEL, anchor="ma")
    d.text((cx, cy + 426), LUGAR,
           font=ajustar(PLAYFAIR, LUGAR, util, 36, "Medium"),
           fill=PAPEL, anchor="ma")

    d.line([(cx - 120, cy + 502), (cx + 120, cy + 502)], fill=ORO, width=2)
    d.text((cx, cy + 528), PIE, font=f(MONTSERRAT, 20, "Medium"),
           fill=PAPEL_3, anchor="ma")

    grano(im)
    # El nombre lleva versión a propósito: vercel.json manda las fotos con
    # caché de un año inmutable, y WhatsApp además guarda la vista previa por
    # su cuenta. Con el mismo nombre seguirían viendo la imagen anterior
    # aunque la subamos nueva. Al cambiar el diseño, se cambia el v2 → v3.
    guardar(im, "og-imagen-v2.jpg")


print("Imágenes de la invitación:")
os.makedirs(SALIDA, exist_ok=True)
historia()
feed()
miniatura()
print("\nListo.")