#!/bin/bash
# Génère toutes les icônes d'Accoste dans l'arborescence RustDesk (à lancer sur un Mac).
# Usage : bash accoste/icones/generer.sh   (depuis la racine du dépôt)
set -euo pipefail
cd "$(dirname "$0")/../.."
ICI=accoste/icones
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

swiftc -O -o "$TMP/icone" "$ICI/icone.swift"
r() { "$TMP/icone" "$1" "$2" "$3"; }

# Icônes génériques
r app 1024 res/icon.png
r mac 1024 res/mac-icon.png
r app 32 res/32x32.png
r app 64 res/64x64.png
r app 128 res/128x128.png
r app 256 res/128x128@2x.png
r gabarit 60 res/mac-tray-dark-x2.png
r gabarit 48 res/mac-tray-light-x2.png
r etiquette 0 libs/portable/src/res/label.png

# Windows (.ico)
for s in 16 24 32 48 64 128 256; do r app $s "$TMP/ico-$s.png"; done
python3 "$ICI/ico.py" res/icon.ico "$TMP"/ico-{16,24,32,48,64,128,256}.png
python3 "$ICI/ico.py" flutter/windows/runner/resources/app_icon.ico "$TMP"/ico-{16,24,32,48,64,128,256}.png
python3 "$ICI/ico.py" res/tray-icon.ico "$TMP"/ico-{16,24,32,48}.png

# macOS (.icns)
SET="$TMP/AppIcon.iconset"
mkdir -p "$SET"
for s in 16 32 128 256 512; do
  r mac $s "$SET/icon_${s}x${s}.png"
  r mac $((s * 2)) "$SET/icon_${s}x${s}@2x.png"
done
iconutil -c icns -o flutter/macos/Runner/AppIcon.icns "$SET"

# Android
A=flutter/android/app/src/main/res
for d in mdpi:48:108:24 hdpi:72:162:36 xhdpi:96:216:48 xxhdpi:144:324:72 xxxhdpi:192:432:96; do
  IFS=: read -r nom lanceur avant notif <<< "$d"
  r app "$lanceur" "$A/mipmap-$nom/ic_launcher.png"
  r rond "$lanceur" "$A/mipmap-$nom/ic_launcher_round.png"
  r avant-plan "$avant" "$A/mipmap-$nom/ic_launcher_foreground.png"
  r notif "$notif" "$A/mipmap-$nom/ic_stat_logo.png"
done

# Logos vectoriels
for f in flutter/assets/icon.svg res/logo.svg res/scalable.svg res/design.svg; do
  cp "$ICI/accoste.svg" "$f"
done

echo "Icônes générées."
