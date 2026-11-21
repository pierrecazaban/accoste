// Dessine l'icône d'Accoste (écran + curseur) en PNG.
// Usage : swift icone.swift <mode> <taille> <sortie.png>
// Modes : app (carré arrondi plein), mac (carré arrondi avec marge macOS),
//         rond (disque), avant-plan (pictogramme seul, zone sûre Android),
//         gabarit (pictogramme noir, barre de menus macOS),
//         notif (pictogramme blanc, notification Android),
//         etiquette (texte « Accoste » blanc, 96x32)
import AppKit
import CoreGraphics
import Foundation
import ImageIO
import UniformTypeIdentifiers

let args = CommandLine.arguments
guard args.count == 4, let size = Int(args[2]) else {
    FileHandle.standardError.write("usage: icone.swift <mode> <taille> <sortie.png>\n".data(using: .utf8)!)
    exit(2)
}
let mode = args[1]
let out = args[3]

let width = mode == "etiquette" ? 96 : size
let height = mode == "etiquette" ? 32 : size
let space = CGColorSpace(name: CGColorSpace.sRGB)!
guard let ctx = CGContext(data: nil, width: width, height: height, bitsPerComponent: 8, bytesPerRow: 0,
                          space: space, bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue) else { exit(1) }

// Repère 1024 x 1024, origine en haut à gauche (comme le SVG).
func toTopLeft(_ scale: CGFloat) {
    ctx.translateBy(x: 0, y: CGFloat(height))
    ctx.scaleBy(x: scale, y: -scale)
}

let tealDark = CGColor(srgbRed: 0x0B / 255, green: 0x5F / 255, blue: 0x57 / 255, alpha: 1)
let tealLight = CGColor(srgbRed: 0x14 / 255, green: 0xB8 / 255, blue: 0xA6 / 255, alpha: 1)
let white = CGColor(srgbRed: 1, green: 1, blue: 1, alpha: 1)
let black = CGColor(srgbRed: 0, green: 0, blue: 0, alpha: 1)

func fillBackground(_ path: CGPath) {
    ctx.saveGState()
    ctx.addPath(path)
    ctx.clip()
    let gradient = CGGradient(colorsSpace: space, colors: [tealLight, tealDark] as CFArray, locations: [0, 1])!
    ctx.drawLinearGradient(gradient, start: CGPoint(x: 0, y: 0), end: CGPoint(x: 1024, y: 1024), options: [])
    ctx.restoreGState()
}

// Pictogramme : écran, pied, curseur. `t` = transformation dans le repère 1024.
func drawGlyph(color: CGColor, transform t: CGAffineTransform) {
    ctx.saveGState()
    ctx.concatenate(t)
    ctx.setStrokeColor(color)
    ctx.setFillColor(color)
    // Écran
    let screen = CGPath(roundedRect: CGRect(x: 232, y: 262, width: 560, height: 390), cornerWidth: 56, cornerHeight: 56, transform: nil)
    ctx.addPath(screen)
    ctx.setLineWidth(64)
    ctx.strokePath()
    // Pied
    ctx.fill(CGRect(x: 472, y: 680, width: 80, height: 70))
    ctx.addPath(CGPath(roundedRect: CGRect(x: 352, y: 742, width: 320, height: 60), cornerWidth: 30, cornerHeight: 30, transform: nil))
    ctx.fillPath()
    // Curseur
    let cursor: [CGPoint] = [
        CGPoint(x: 452, y: 370), CGPoint(x: 452, y: 566), CGPoint(x: 501, y: 521),
        CGPoint(x: 537, y: 598), CGPoint(x: 571, y: 583), CGPoint(x: 535, y: 506), CGPoint(x: 601, y: 506),
    ]
    ctx.beginPath()
    ctx.addLines(between: cursor)
    ctx.closePath()
    ctx.fillPath()
    ctx.restoreGState()
}

// Centre le pictogramme (boîte 200..824 x 230..802) et le met à l'échelle `factor`.
func centered(_ factor: CGFloat) -> CGAffineTransform {
    let cx: CGFloat = 512, cy: CGFloat = 532 // centre de la boîte du pictogramme
    return CGAffineTransform(translationX: 512, y: 512).scaledBy(x: factor, y: factor).translatedBy(x: -cx, y: -cy)
}

switch mode {
case "app":
    toTopLeft(CGFloat(size) / 1024)
    fillBackground(CGPath(roundedRect: CGRect(x: 0, y: 0, width: 1024, height: 1024), cornerWidth: 230, cornerHeight: 230, transform: nil))
    drawGlyph(color: white, transform: centered(1.0))
case "mac":
    toTopLeft(CGFloat(size) / 1024)
    fillBackground(CGPath(roundedRect: CGRect(x: 100, y: 100, width: 824, height: 824), cornerWidth: 185, cornerHeight: 185, transform: nil))
    drawGlyph(color: white, transform: centered(0.8))
case "rond":
    toTopLeft(CGFloat(size) / 1024)
    fillBackground(CGPath(ellipseIn: CGRect(x: 0, y: 0, width: 1024, height: 1024), transform: nil))
    drawGlyph(color: white, transform: centered(0.82))
case "avant-plan":
    // Icône adaptative Android : seuls les 66 % centraux sont garantis visibles.
    toTopLeft(CGFloat(size) / 1024)
    drawGlyph(color: white, transform: centered(0.62))
case "gabarit":
    toTopLeft(CGFloat(size) / 1024)
    drawGlyph(color: black, transform: centered(1.4))
case "notif":
    toTopLeft(CGFloat(size) / 1024)
    drawGlyph(color: white, transform: centered(1.4))
case "etiquette":
    let attrs: [NSAttributedString.Key: Any] = [
        .font: NSFont.systemFont(ofSize: 20, weight: .semibold),
        .foregroundColor: NSColor.white,
    ]
    let text = NSAttributedString(string: "Accoste", attributes: attrs)
    NSGraphicsContext.current = NSGraphicsContext(cgContext: ctx, flipped: false)
    let bounds = text.size()
    text.draw(at: NSPoint(x: (96 - bounds.width) / 2, y: (32 - bounds.height) / 2))
default:
    FileHandle.standardError.write("mode inconnu : \(mode)\n".data(using: .utf8)!)
    exit(2)
}

guard let image = ctx.makeImage(),
      let dest = CGImageDestinationCreateWithURL(URL(fileURLWithPath: out) as CFURL, UTType.png.identifier as CFString, 1, nil)
else { exit(1) }
CGImageDestinationAddImage(dest, image, nil)
if !CGImageDestinationFinalize(dest) { exit(1) }
