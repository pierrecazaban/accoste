"""Assemble des PNG carrés en un fichier .ico (entrées PNG, Windows Vista et suivants).

Usage : python3 ico.py sortie.ico image16.png image32.png ...
"""
import struct
import sys


def taille_png(donnees):
    largeur, hauteur = struct.unpack(">II", donnees[16:24])
    return largeur, hauteur


def main():
    sortie, entrees = sys.argv[1], sys.argv[2:]
    images = []
    for chemin in entrees:
        with open(chemin, "rb") as f:
            images.append(f.read())
    entete = struct.pack("<HHH", 0, 1, len(images))
    decalage = 6 + 16 * len(images)
    repertoire = b""
    for donnees in images:
        largeur, hauteur = taille_png(donnees)
        repertoire += struct.pack(
            "<BBBBHHII",
            largeur % 256,  # 256 s'écrit 0
            hauteur % 256,
            0, 0, 1, 32, len(donnees), decalage,
        )
        decalage += len(donnees)
    with open(sortie, "wb") as f:
        f.write(entete + repertoire + b"".join(images))


if __name__ == "__main__":
    main()
