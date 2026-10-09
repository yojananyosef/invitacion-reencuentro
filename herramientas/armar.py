#!/usr/bin/env python3
"""Arma el HTML final: un solo archivo con las imágenes embebidas.

Ventaja: la invitación se puede mandar por WhatsApp, correo o Drive como UN
archivo y se ve igual en cualquier celular, sin carpeta ni internet.
"""
import base64
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(BASE, ".assets")
SALIDA = BASE


def data_uri(nombre):
    with open(os.path.join(ASSETS, nombre), "rb") as f:
        return "data:image/jpeg;base64," + base64.b64encode(f.read()).decode("ascii")


html = open(os.path.join(BASE, "index.base.html"), encoding="utf-8").read()

IMAGENES = {
    "IMAGEN_SEGUNDA": "segunda-venida.jpg",   # portada
    "IMAGEN_PASTOR": "buen-pastor.jpg",       # buen pastor
    "IMAGEN_CORDERO": "jesus-cordero.jpg",    # cierre
}

faltantes = [k for k in IMAGENES if k not in html]
if faltantes:
    sys.exit("✗ la plantilla no tiene estos marcadores: " + ", ".join(faltantes))

for marca, archivo in IMAGENES.items():
    html = html.replace(marca, data_uri(archivo))
    kb = os.path.getsize(os.path.join(ASSETS, archivo)) / 1024
    print(f"  embebida {archivo:20s} {kb:6.0f} KB")

ruta = os.path.join(SALIDA, "index.html")
with open(ruta, "w", encoding="utf-8") as f:
    f.write(html)

kb = os.path.getsize(ruta) / 1024
print(f"\n✓ {ruta}")
print(f"  {kb:.0f} KB · un solo archivo · sin dependencias externas")

pendientes = [m for m in list(IMAGENES) + ["REEMPLAZA_CON_TU_DOMINIO"] if m in html]
if pendientes:
    print(f"\n  nota: quedan marcadores sin reemplazar -> {', '.join(pendientes)}")