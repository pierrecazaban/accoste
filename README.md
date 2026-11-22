# Accoste

Prise en main à distance : Windows, macOS et Android, sans limite de durée de session.

Accoste est une version modifiée de [RustDesk](https://github.com/rustdesk/rustdesk) (licence AGPL-3.0),
configurée pour utiliser son propre serveur. Le code d'origine reste la propriété de ses auteurs
(Purslane Tech Pte. Ltd. et contributeurs) ; les modifications d'Accoste sont publiées ici sous la même licence.

- Site et téléchargements : https://pierrecazaban.github.io/accoste/
- Code source (obligation AGPL) : ce dépôt

## Ce qui change par rapport à RustDesk

| Élément | Où |
|---|---|
| Nom, serveur et clé intégrés | `libs/hbb_common/src/config.rs` (`APP_NAME`, `RENDEZVOUS_SERVERS`, `RS_PUB_KEY`) |
| Icônes et logos | `accoste/icones/` (programme de dessin + script de génération) |
| Identifiants d'appli (`fr.accoste.app`), libellés, liens, mentions légales | `accoste/appliquer_marque.py` |
| Compilation | `.github/workflows/accoste.yml` → `flutter-build.yml` réduit à Windows, macOS et Android |
| Glisser-déposer d'images sur l'écran distant (collées à l'endroit du dépôt) | `flutter/lib/desktop/pages/remote_page.dart` (`_onImagesDropped`), `src/clipboard.rs` (`image_drop_msg`), `src/server/connection.rs` |

`libs/hbb_common` est intégré directement au dépôt (ce n'est plus un sous-module) pour que la
configuration du serveur fasse partie du code publié.

## Publier une version

```bash
git tag v1.5.3 && git push origin v1.5.3
```

GitHub Actions compile alors (environ 1 h 30) et publie dans la « release » du même nom :

- `accoste-<version>-x86_64.exe` et `-aarch64.exe` : Windows (portable, avec bouton d'installation)
- `accoste-<version>-x86_64.dmg` et `-aarch64.dmg` : macOS Intel et Apple Silicon
- `accoste-<version>-<arch>-signed.apk` : Android

Secrets du dépôt utilisés s'ils existent : `ANDROID_SIGNING_KEY`, `ANDROID_ALIAS`,
`ANDROID_KEY_STORE_PASSWORD`, `ANDROID_KEY_PASSWORD` (APK signé) ; `MACOS_P12_BASE64`,
`MACOS_P12_PASSWORD`, `MACOS_CODESIGN_IDENTITY`, `MACOS_NOTARIZE_JSON` (macOS signé et notarisé).
Sans certificat, les applis sont publiées non signées (avertissement SmartScreen sous Windows,
« Ouvrir quand même » sous macOS).

## Mettre à jour depuis RustDesk

```bash
# récupérer la nouvelle version de RustDesk par-dessus ce dépôt, puis :
python3 accoste/appliquer_marque.py     # s'arrête en signalant toute règle devenue obsolète
bash accoste/icones/generer.sh          # sur un Mac
```

## Serveur

`hbbs` (mise en relation) et `hbbr` (relais) de [rustdesk-server](https://github.com/rustdesk/rustdesk-server)
tournent en conteneurs Docker sur le VPS (`~/accoste-serveur`, ports 21115-21117 TCP et 21116 UDP).
La clé privée du serveur est sauvegardée hors du dépôt : si elle est perdue, toutes les applis
distribuées doivent être recompilées.

## Licence

AGPL-3.0, voir [LICENCE](LICENCE). Toute version distribuée d'Accoste doit rester accompagnée de son code source.
