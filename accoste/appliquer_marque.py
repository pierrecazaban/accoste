#!/usr/bin/env python3
"""Transforme une arborescence RustDesk en Accoste.

À lancer depuis la racine du dépôt, après avoir récupéré une nouvelle version de RustDesk :
    python3 accoste/appliquer_marque.py
    bash accoste/icones/generer.sh      (sur un Mac)

Le script est idempotent : le relancer sur un arbre déjà transformé ne change rien.
Il s'arrête avec une erreur si un texte attendu a disparu (le code de RustDesk a changé) :
il faut alors adapter la règle concernée.
"""
import glob
import os
import re
import sys

# --- Identité du produit -------------------------------------------------------------
NOM = "Accoste"
ID_APPLI = "fr.accoste.app"
SERVEUR = "158.69.232.131"  # serveur de mise en relation (hbbs) ; le relais est annoncé par hbbs
CLE_SERVEUR = "ywCWzOEDRDFWH4+7Mou24Ob2v7wisur1js4rUJFNzjk="
DEPOT = "https://github.com/pierrecazaban/accoste"
SITE = "https://pierrecazaban.github.io/accoste/"
CONFIDENTIALITE = SITE + "confidentialite.html"
COPYRIGHT = f"© 2026 {NOM}. Basé sur RustDesk © Purslane Tech Pte. Ltd. (AGPL-3.0)"
# --------------------------------------------------------------------------------------

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(RACINE)
erreurs = []


def lire(chemin):
    with open(chemin, encoding="utf-8") as f:
        return f.read()


def ecrire(chemin, texte):
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(texte)


def remplacer(chemin, ancien, nouveau, tous=True):
    """Remplace `ancien` par `nouveau`. Sans effet si c'est déjà fait."""
    texte = lire(chemin)
    if ancien in texte:
        texte = texte.replace(ancien, nouveau) if tous else texte.replace(ancien, nouveau, 1)
        ecrire(chemin, texte)
    elif nouveau not in texte:
        erreurs.append(f"{chemin} : texte introuvable : {ancien!r}")


def remplacer_re(chemin, motif, nouveau, attendu):
    """Remplacement par expression régulière ; `attendu` sert à reconnaître l'état final."""
    texte = lire(chemin)
    nouveau_texte, n = re.subn(motif, nouveau, texte, flags=re.M)
    if n:
        ecrire(chemin, nouveau_texte)
    elif attendu not in texte:
        erreurs.append(f"{chemin} : motif introuvable : {motif!r}")


# 1. Nom, serveur et clé intégrés au cœur (hbb_common)
CONFIG = "libs/hbb_common/src/config.rs"
remplacer_re(CONFIG, r'^pub const RENDEZVOUS_SERVERS: &\[&str\] = &\[[^\]]*\];',
             f'pub const RENDEZVOUS_SERVERS: &[&str] = &["{SERVEUR}"];', f'"{SERVEUR}"')
remplacer_re(CONFIG, r'^pub const RS_PUB_KEY: &str = "[^"]*";',
             f'pub const RS_PUB_KEY: &str = "{CLE_SERVEUR}";', CLE_SERVEUR)
remplacer(CONFIG, 'pub static ref APP_NAME: RwLock<String> = RwLock::new("RustDesk".to_owned());',
          f'pub static ref APP_NAME: RwLock<String> = RwLock::new("{NOM}".to_owned());')

# 2. Cargo (métadonnées)
remplacer("Cargo.toml", 'description = "RustDesk Remote Desktop"', f'description = "{NOM} Remote Desktop"')
remplacer("Cargo.toml", 'name = "RustDesk"\nidentifier = "com.carriez.rustdesk"',
          f'name = "{NOM}"\nidentifier = "{ID_APPLI}"')

# 3. macOS
remplacer("flutter/macos/Runner/Configs/AppInfo.xcconfig", "PRODUCT_NAME = RustDesk", f"PRODUCT_NAME = {NOM}")
remplacer("flutter/macos/Runner/Configs/AppInfo.xcconfig", "PRODUCT_BUNDLE_IDENTIFIER = com.carriez.flutterHbb",
          f"PRODUCT_BUNDLE_IDENTIFIER = {ID_APPLI}")
remplacer_re("flutter/macos/Runner/Configs/AppInfo.xcconfig", r"^PRODUCT_COPYRIGHT = (?!©).*$",
             f"PRODUCT_COPYRIGHT = {COPYRIGHT}", f"PRODUCT_COPYRIGHT = {COPYRIGHT}")
remplacer("flutter/macos/Runner/Info.plist", "<string>com.carriez.rustdesk</string>", f"<string>{ID_APPLI}</string>")
remplacer("flutter/macos/Runner/Info.plist", "<string>rustdesk</string>", f"<string>{NOM.lower()}</string>")
remplacer("flutter/macos/Runner.xcodeproj/project.pbxproj", "RustDesk.app", f"{NOM}.app")
remplacer("build.py", "Release/RustDesk.app/Contents/MacOS/", f"Release/{NOM}.app/Contents/MacOS/")

# 4. Windows (propriétés du fichier .exe)
RC = "flutter/windows/runner/Runner.rc"
remplacer(RC, 'VALUE "CompanyName", "Purslane Tech Pte. Ltd." "\\0"', f'VALUE "CompanyName", "{NOM}" "\\0"')
remplacer(RC, 'VALUE "FileDescription", "RustDesk Remote Desktop" "\\0"',
          f'VALUE "FileDescription", "{NOM} Remote Desktop" "\\0"')
remplacer_re(RC, r'VALUE "LegalCopyright", "(?!©)[^"]*" "\\0"',
             f'VALUE "LegalCopyright", "{COPYRIGHT}" "\\\\0"', f'"{COPYRIGHT}"')
remplacer(RC, 'VALUE "ProductName", "RustDesk" "\\0"', f'VALUE "ProductName", "{NOM}" "\\0"')

# 5. Android
remplacer("flutter/android/app/build.gradle", 'applicationId "com.carriez.flutter_hbb"', f'applicationId "{ID_APPLI}"')
remplacer("flutter/android/app/src/main/AndroidManifest.xml", 'android:label="RustDesk Input"',
          f'android:label="{NOM} Input"')
remplacer("flutter/android/app/src/main/AndroidManifest.xml", 'android:label="RustDesk"', f'android:label="{NOM}"')
for chemin in glob.glob("flutter/android/app/src/main/res/values*/strings.xml"):
    texte = lire(chemin)
    if "RustDesk" in texte:
        ecrire(chemin, texte.replace("RustDesk", NOM))
remplacer("flutter/android/app/src/main/res/values/ic_launcher_background.xml",
          '<color name="ic_launcher_background">#ffffff</color>',
          '<color name="ic_launcher_background">#0F8A7E</color>')

# 6. Interface (Flutter) : titre, liens et mentions légales
D = "flutter/lib"
remplacer(f"{D}/desktop/widgets/tabbar_widget.dart", 'const Text(\n                              "RustDesk",',
          f'const Text(\n                              "{NOM}",')
remplacer(f"{D}/common.dart", "launchUrl(Uri.parse('https://rustdesk.com'));", f"launchUrl(Uri.parse('{SITE}'));")
remplacer(f"{D}/mobile/pages/settings_page.dart", "const url = 'https://rustdesk.com/';", f"const url = '{SITE}';")
remplacer(f"{D}/desktop/pages/install_page.dart", "'https://rustdesk.com/privacy.html'", f"'{CONFIDENTIALITE}'")
remplacer(f"{D}/desktop/pages/connection_page.dart", 'const url = "https://rustdesk.com/pricing";',
          f'const url = "{SITE}#tarifs";')
remplacer(f"{D}/desktop/pages/desktop_home_page.dart", "'https://rustdesk.com/download'", f"'{SITE}'")
REGLAGES = f"{D}/desktop/pages/desktop_setting_page.dart"
remplacer(REGLAGES, "launchUrlString('https://rustdesk.com/privacy.html');", f"launchUrlString('{CONFIDENTIALITE}');")
remplacer(REGLAGES, "launchUrlString('https://rustdesk.com');", f"launchUrlString('{SITE}');")
remplacer(REGLAGES,
          "'Copyright © ${DateTime.now().toString().substring(0, 4)} Purslane Tech Pte. Ltd.\\n$license',",
          f"'{COPYRIGHT}\\nCode source : {DEPOT}\\n$license',")

# 7. Chaîne de compilation (GitHub Actions)
W = ".github/workflows"
for inutile in ["ci.yml", "clear-cache.yml", "fdroid.yml", "flutter-ci.yml", "flutter-nightly.yml",
                "flutter-tag.yml", "playground.yml", "update-webpki-roots.yml"]:
    if os.path.exists(f"{W}/{inutile}"):
        os.remove(f"{W}/{inutile}")

BUILD = f"{W}/flutter-build.yml"
lignes = lire(BUILD).split("\n")


def retirer_bloc(lignes, debut_motif, fin_re):
    """Retire le bloc qui commence par la ligne `debut_motif` jusqu'à la prochaine ligne
    correspondant à `fin_re` (exclue)."""
    try:
        i = lignes.index(debut_motif)
    except ValueError:
        return lignes
    j = i + 1
    while j < len(lignes) and not re.match(fin_re, lignes[j]):
        j += 1
    return lignes[:i] + lignes[j:]


# Jobs non distribués pour l'instant : Linux (paquet à renommer), iOS, web, ancienne interface
# Sciter, métadonnées de mise à jour signées par RustDesk.
for job in ["generate-sbom", "build-for-windows-sciter", "build-rustdesk-ios", "publish-signed-update-metadata",
            "publish_unsigned", "build-rustdesk-android-universal", "build-rustdesk-linux",
            "build-rustdesk-linux-drm", "build-rustdesk-linux-sciter", "build-appimage", "build-flatpak",
            "build-rustdesk-web"]:
    lignes = retirer_bloc(lignes, f"  {job}:", r"^  [A-Za-z0-9_-]+:$")
# Paquet MSI : son préprocesseur suppose le nom RustDesk ; on distribue l'installeur .exe.
for etape in ["Build msi", "Build pre-built MSI template", "Upload unsigned msi template"]:
    lignes = retirer_bloc(lignes, f"      - name: {etape}", r"^      - |^  [A-Za-z0-9_-]+:$")
texte = "\n".join(lignes)
# Sans certificat Apple, l'appli reçoit une signature ad hoc cohérente (sinon macOS la dit
# « endommagée », car build.py ajoute le binaire `service` après la signature de Xcode).
SIGNATURE_AD_HOC = ("          codesign --force --deep --sign - ./flutter/build/macos/Build/Products/Release/"
                    f"{NOM}.app\n")
CREATE_DMG_NON_SIGNE = ('          create-dmg --icon "RustDesk.app" 200 190 --hide-extension "RustDesk.app" '
                        '--window-size 800 400 --app-drop-link 600 185 rustdesk-${{ env.VERSION }}-')
if SIGNATURE_AD_HOC not in texte:
    if CREATE_DMG_NON_SIGNE not in texte:
        erreurs.append(f"{BUILD} : étape « create unsigned dmg » introuvable")
    texte = texte.replace(CREATE_DMG_NON_SIGNE, SIGNATURE_AD_HOC + CREATE_DMG_NON_SIGNE, 1)
for ancien, nouveau in [
    ("            ./SignOutput/rustdesk-*.msi\n", ""),
    ("rustdesk-${{ env.VERSION }}", "accoste-${{ env.VERSION }}"),
    ("rustdesk-${VERSION}", "accoste-${VERSION}"),
    ("./SignOutput/rustdesk-*", "./SignOutput/accoste-*"),
    ("rustdesk*-${{ matrix.job.arch }}.dmg", "accoste*-${{ matrix.job.arch }}.dmg"),
    ("RustDesk.app", f"{NOM}.app"),
    ("Contents/MacOS/RustDesk ", f"Contents/MacOS/{NOM} "),
]:
    texte = texte.replace(ancien, nouveau)
ecrire(BUILD, texte)
for job in ["build-rustdesk-linux:", "build-rustdesk-ios:", "build-for-windows-sciter:"]:
    if f"\n  {job}\n" in texte:
        erreurs.append(f"{BUILD} : le job {job} n'a pas été retiré")

ecrire(f"{W}/accoste.yml", f"""name: Accoste — compilation et publication

# Pousser une étiquette (ex. v1.5.3) compile Windows, macOS et Android
# et publie les installeurs dans une « release » GitHub portant ce nom.
on:
  push:
    tags:
      - "v*"
  workflow_dispatch:
    inputs:
      etiquette:
        description: "Nom de la release à créer ou compléter"
        required: true
        default: "essai"

permissions:
  contents: write

jobs:
  compiler:
    uses: ./.github/workflows/flutter-build.yml
    secrets: inherit
    with:
      upload-artifact: true
      upload-tag: ${{{{ github.event_name == 'workflow_dispatch' && inputs.etiquette || github.ref_name }}}}
""")

if erreurs:
    print("Changement de marque incomplet :", file=sys.stderr)
    for e in erreurs:
        print("  - " + e, file=sys.stderr)
    sys.exit(1)
print(f"Marque {NOM} appliquée.")
