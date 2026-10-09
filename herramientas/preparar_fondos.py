#!/usr/bin/env python3
"""Prepara las 3 pinturas para la invitación.

EL PROBLEMA REAL
----------------
Las pinturas originales son pequeñas: 700×469, 500×619 y 500×670. Un celular
moderno tiene densidad de 2x o 3x, así que una lámina de 305px de ancho necesita
915 píxeles reales en pantalla. Con la imagen original, el navegador la ampliaría
1.8x y se vería blanda: de ahí la queja de que se veían borrosas.

QUÉ HACE ESTE SCRIPT
--------------------
1. Recorta lo que sobra (la multitud al pie, la firma del autor).
2. Preamplía con Lanczos + un realce suave hasta un tamaño que cubra lo que
   un celular de 3x necesita, sin pasarse.
3. Nunca deforma: la proporción se conserva exactamente.

Se llama "preampliar" y no "mejorar" a propósito: no se inventa detalle que no
existe, solo se re-muestrea con el mejor filtro disponible y se recupera algo
de nitidez. El techo de calidad lo ponen los originales de 500-700px. Para
tener Truly nitida habría que conseguir las pinturas en alta resolución.

TAMÁÑOS DE SALIDA (objetivo: 3x en un celular de 390px, ~915px reales)
  segunda-venida.jpg  700×469 -> 1120×464  (lámina horizontal de la portada)
  buen-pastor.jpg     500×619 ->  840×936  (lámina vertical)
  jesus-cordero.jpg   500×670 ->  840×1018 (lámina vertical del cierre)
"""
from PIL import Image, ImageEnhance, ImageFilter
import os

DESCARGAS = "/home/j/Descargas"
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(RAIZ, ".assets")
os.makedirs(OUT, exist_ok=True)

# (archivo origen, caja de recorte (l,t,r,b), ancho objetivo)
ORIGENES = {
    "segunda-venida.jpg": (
        f"{DESCARGAS}/Blessed_Hope_p_65177fd1-3722-44c1-9374-f2773c37195f_700x469.webp",
        (0.0, 0.0, 1.0, 0.62), 1120),   # fuera la multitud del pie; queda el arco y Cristo
    "buen-pastor.jpg": (
        f"{DESCARGAS}/Lamb_of_God-p_5fb096eb-4a3f-46be-b9ba-b39fc4e52e66_500x619.webp",
        (0.0, 0.0, 1.0, 0.90), 950),    # fuera la firma
    "jesus-cordero.jpg": (
        f"{DESCARGAS}/Rescue_dd87ad0c-a841-4e0b-b390-17fbdd4cf982_500x670.webp",
        (0.0, 0.0, 1.0, 0.905), 950),   # fuera la firma
}

# Cuánto se re-muestrea. 1.0 = no ampliar.
#
# El ancho objetivo sale de lo que ocupa la lámina en pantalla multiplicado por
# la densidad de píxeles: en un celular de 390px a 3x, una lámina de 305px de
# ancho necesita 915 píxeles reales. Con MAX_ESCALA=1.9 se cubre un celular
# típico y una tablet sin pasarse de lo que el original da.
MAX_ESCALA = 1.9


def recortar(origen, caja):
    """Corta por fracciones (l, t, r, b)."""
    im = Image.open(origen).convert("RGB")
    w, h = im.size
    l, t, r, b = caja
    return im.crop((int(l * w), int(t * h), int(r * w), int(b * h)))


def preampliar(im, objetivo, max_escala=MAX_ESCALA):
    """Re-muestrea con Lanczos hasta `objetivo` de ancho, sin deformar.

    Después pasa un realce suave (unsharp) que devuelve el contraste que el
    promediado de Lanczos se lleva. Con percent bajo y umbral alto, para que
    solo actúe sobre los bordes: en una pintura al óleo no se nota el halo,
    pero en el fondo de las nubes sí.
    """
    w, h = im.size
    escala = min(objetivo / w, max_escala)
    if escala <= 1.0:
        return im, escala

    nuevo = (max(1, int(w * escala)), max(1, int(h * escala)))
    grande = im.resize(nuevo, Image.LANCZOS)

    # el radio debe ir con la ampliación: si no, el realce no cubre el
    # desenfoque que acabamos de introducir
    radio = max(0.8, 1.1 * escala)
    percent = int(70 / escala)
    afilado = grande.filter(ImageFilter.UnsharpMask(
        radius=radio, percent=max(25, min(70, percent)), threshold=3))
    return afilado, escala


def guardar(im, nombre, quality=86):
    ruta = os.path.join(OUT, nombre)
    im.save(ruta, "JPEG", quality=quality, optimize=True, progressive=True,
            subsampling=0)   # 4:4:4: en una textura de pintura se nota el croma
    kb = os.path.getsize(ruta) / 1024
    return kb


print("Pinturas:")
print("  (origen → salida, con la proporción intacta)\n")

for nombre, (origen, caja, objetivo) in ORIGENES.items():
    if not os.path.exists(origen):
        raise SystemExit(f"✗ no existe {origen}")

    original = Image.open(origen).size
    im = recortar(origen, caja)
    recortada = im.size

    # color y contraste: un punto cada uno, nada más. La pintura es el material.
    im = ImageEnhance.Color(im).enhance(1.05)
    im = ImageEnhance.Contrast(im).enhance(1.04)

    grande, escala = preampliar(im, objetivo)

    # la proporción debe seguir siendo la misma que la del recorte
    ar0 = recortada[0] / recortada[1]
    ar1 = grande.size[0] / grande.size[1]
    if abs(ar0 - ar1) / ar0 > 0.01:
        raise SystemExit(f"✗ {nombre}: la proporción cambió de {ar0:.4f} a {ar1:.4f}")

    kb = guardar(grande, nombre)
    print(f"  {nombre:20s} {recortada[0]}x{recortada[1]} → "
          f"{grande.size[0]}x{grande.size[1]}  "
          f"({escala:.2f}x, {kb:.0f} KB)")

print("\nListo. Para que se vean nítidas de verdad harían falta las pinturas")
print("en alta resolución: estos originales son de 500-700px de ancho.")