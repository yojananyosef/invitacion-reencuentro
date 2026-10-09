#!/usr/bin/env python3
"""Comprueba que las imágenes estáticas no se salen del lienzo ni amplían
las pinturas.

Usa las mismas funciones de composición que generar_imagenes.py, así que
mide exactamente lo que se dibuja: si cambia un tamaño o un texto, el aviso
sale del mismo sitio.

Uso:  python3 herramientas/ver_espacio.py
Sale con código 1 si algo no cabe o si alguna lámina se amplía.
"""
import importlib.util
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# generar_imagenes.py genera las imágenes al importarse; aquí solo se
# necesitan sus funciones, así que se carga el código sin el final.
_spec = importlib.util.spec_from_file_location(
    "generar_imagenes", os.path.join(RAIZ, "herramientas", "generar_imagenes.py"))
g = importlib.util.module_from_spec(_spec)
_fuente = _spec.loader.get_source(_spec.name)
exec(compile(_fuente.split('print("Imágenes')[0], _spec.origin, "exec"), g.__dict__)

FORMATOS = [
    ("respaldo-1080x1920.jpg", 1080, 1920, True, 0.11),
    ("respaldo-1080x1350.jpg", 1080, 1350, False, 0.10),
]
AIRE_MIN = 64


def revisar_laminas(bloques, nombre, fallos):
    """Ninguna lámina puede ocupar más píxeles de los que tiene de origen."""
    for _, piezas, _ in bloques:
        for p in piezas:
            if "ancho" not in p:
                continue
            src = Image.open(os.path.join(g.ASSETS, "segunda-venida.jpg"))
            if p["ancho"] - 16 > src.size[0] + 1:
                fallos.append(f"{nombre}: una lámina mide {p['ancho']}px pero la "
                              f"pintura solo tiene {src.size[0]}px")


from PIL import Image  # noqa: E402  (después, lo usa revisar_laminas)


def main():
    fallos = []
    for nombre, w, h, con_versiculo, margen in FORMATOS:
        bloques = g._encajar(w, margen, h, con_versiculo)
        y0 = g.y_inicial(h, bloques)
        final = y0 + g.alto_total(bloques)
        libre = h - final

        if libre < AIRE_MIN:
            fallos.append(f"{nombre}: termina en {final}px de {h}px "
                          f"({libre}px de aire, se necesitan {AIRE_MIN})")
        else:
            print(f"✓ {nombre}: {final}px de {h}px ({libre}px de aire)")

        revisar_laminas(bloques, nombre, fallos)

    for msg in fallos:
        print("✗ " + msg)
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())