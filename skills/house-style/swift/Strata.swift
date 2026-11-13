// Strata tokens for SwiftUI. Maintained from tokens/tokens.json.
import SwiftUI

public enum StrataTheme { case night, paper }

public struct Strata {
    public let theme: StrataTheme
    public var ground: Color { theme == .night ? Color(red: 0.086, green: 0.086, blue: 0.098) : Color(red: 0.957, green: 0.933, blue: 0.890) }
    public var surface: Color { theme == .night ? Color(red: 0.098, green: 0.098, blue: 0.114) : Color(red: 0.980, green: 0.965, blue: 0.933) }
    public var raised: Color { theme == .night ? Color(red: 0.133, green: 0.133, blue: 0.149) : Color(red: 1.000, green: 0.992, blue: 0.973) }
    public var wash: Color { theme == .night ? Color(red: 0.161, green: 0.180, blue: 0.208) : Color(red: 0.929, green: 0.898, blue: 0.839) }
    public var line: Color { theme == .night ? Color(red: 0.208, green: 0.208, blue: 0.235) : Color(red: 0.867, green: 0.827, blue: 0.761) }
    public var lineStrong: Color { theme == .night ? Color(red: 0.467, green: 0.467, blue: 0.502) : Color(red: 0.549, green: 0.510, blue: 0.435) }
    public var ink: Color { theme == .night ? Color(red: 0.831, green: 0.831, blue: 0.847) : Color(red: 0.078, green: 0.125, blue: 0.227) }
    public var inkMuted: Color { theme == .night ? Color(red: 0.671, green: 0.671, blue: 0.698) : Color(red: 0.302, green: 0.341, blue: 0.424) }
    public var inkFaint: Color { theme == .night ? Color(red: 0.573, green: 0.573, blue: 0.596) : Color(red: 0.392, green: 0.420, blue: 0.486) }
    public var action: Color { theme == .night ? Color(red: 0.541, green: 0.710, blue: 0.839) : Color(red: 0.122, green: 0.365, blue: 0.667) }
    public var actionSoft: Color { theme == .night ? Color(red: 0.161, green: 0.192, blue: 0.224) : Color(red: 0.863, green: 0.906, blue: 0.961) }
    public var onAction: Color { theme == .night ? Color(red: 0.027, green: 0.031, blue: 0.051) : Color(red: 1.000, green: 1.000, blue: 1.000) }
    public var sun: Color { theme == .night ? Color(red: 0.949, green: 0.537, blue: 0.310) : Color(red: 0.659, green: 0.251, blue: 0.071) }
    public var sunSoft: Color { theme == .night ? Color(red: 0.165, green: 0.094, blue: 0.063) : Color(red: 0.980, green: 0.902, blue: 0.847) }
    public var onSun: Color { theme == .night ? Color(red: 0.027, green: 0.031, blue: 0.051) : Color(red: 1.000, green: 1.000, blue: 1.000) }
    public var ok: Color { theme == .night ? Color(red: 0.310, green: 0.757, blue: 0.690) : Color(red: 0.051, green: 0.439, blue: 0.392) }
    public var okSoft: Color { theme == .night ? Color(red: 0.059, green: 0.165, blue: 0.153) : Color(red: 0.835, green: 0.929, blue: 0.910) }
    public var fail: Color { theme == .night ? Color(red: 0.949, green: 0.463, blue: 0.561) : Color(red: 0.659, green: 0.153, blue: 0.290) }
    public var failSoft: Color { theme == .night ? Color(red: 0.169, green: 0.067, blue: 0.098) : Color(red: 0.965, green: 0.863, blue: 0.886) }
    public var series1: Color { theme == .night ? Color(red: 0.310, green: 0.525, blue: 0.839) : Color(red: 0.184, green: 0.435, blue: 0.769) }
    public var series2: Color { theme == .night ? Color(red: 0.859, green: 0.424, blue: 0.200) : Color(red: 0.824, green: 0.376, blue: 0.165) }
    public var series3: Color { theme == .night ? Color(red: 0.133, green: 0.627, blue: 0.561) : Color(red: 0.102, green: 0.576, blue: 0.518) }
    public var series4: Color { theme == .night ? Color(red: 0.604, green: 0.471, blue: 0.816) : Color(red: 0.604, green: 0.420, blue: 0.769) }
    public var series5: Color { theme == .night ? Color(red: 0.929, green: 0.788, blue: 0.482) : Color(red: 0.478, green: 0.259, blue: 0.000) }
    public var series6: Color { theme == .night ? Color(red: 0.831, green: 0.361, blue: 0.494) : Color(red: 0.784, green: 0.275, blue: 0.416) }
    public var seriesContext: Color { theme == .night ? Color(red: 0.392, green: 0.435, blue: 0.549) : Color(red: 0.518, green: 0.486, blue: 0.427) }
    public init(_ theme: StrataTheme = .night) { self.theme = theme }

    // Type: Avenir Next ships with macOS and iOS. Mono: bundle DMMono-*.ttf in the app.
    public static func sans(_ size: CGFloat, _ weight: Font.Weight = .regular) -> Font { .custom("Avenir Next", size: size).weight(weight) }
    public static func mono(_ size: CGFloat, _ weight: Font.Weight = .regular) -> Font { .custom("DM Mono", size: size).weight(weight) }
    public static let space: [CGFloat] = [0, 4, 8, 12, 16, 24, 32, 48, 64, 96, 128]
    public static let radiusSm: CGFloat = 3, radiusMd: CGFloat = 6, radiusLg: CGFloat = 14
}
