---
Source-AI: Claude
Category: Technical
Time-Context: Coding Session
Topics: [UIKit, iOS Development, Xcode Previews, SwiftUI, UIViewRepresentable, IBDesignable]
tags:
  - ai-distilled
---

# UIKit View Preview（AI Insight）

### Summary
Three approaches exist for previewing UIKit views in Xcode without running the simulator: the modern `#Preview` macro (Xcode 15+), the `UIViewRepresentable` SwiftUI wrapper (Xcode 13–14), and `@IBDesignable` for Storyboard-based projects. The `#Preview` macro is now the cleanest and recommended path.

### Key Takeaway
For any UIKit project targeting Xcode 15+, the `#Preview` macro is the definitive approach — it works for both `UIView` and `UIViewController`, supports multiple named variants in one file, and requires no SwiftUI boilerplate.

### Key Insights
- The `#Preview` macro unified UIKit and SwiftUI preview syntax; there is no longer a need for `UIViewRepresentable` wrappers just to get live previews.
- Wrapping preview code in `#if DEBUG ... #endif` is a simple production hygiene practice worth making habitual.
- `@IBDesignable` is the only approach that works inside Interface Builder / Storyboards, but its hot-reload is partial and notoriously slow — avoid for new code.

### Technical Details

#### `#Preview` Macro — Xcode 15+ (Recommended)

```swift
import UIKit

class MyView: UIView {
    override init(frame: CGRect) {
        super.init(frame: frame)
        backgroundColor = .systemBlue
    }
    required init?(coder: NSCoder) { fatalError() }
}

#Preview {
    MyView()
}

// UIViewController variant
#Preview {
    let vc = MyViewController()
    return vc
}

// Multiple named previews in one file
#Preview("Dark Mode") {
    let v = MyView()
    v.overrideUserInterfaceStyle = .dark
    return v
}

#Preview("Light Mode") {
    MyView()
}
```

#### `UIViewRepresentable` Wrapper — Xcode 13–14

```swift
import SwiftUI

struct MyViewPreview: UIViewRepresentable {
    func makeUIView(context: Context) -> MyView { MyView() }
    func updateUIView(_ uiView: MyView, context: Context) {}
}

#if DEBUG
struct MyView_Previews: PreviewProvider {
    static var previews: some View {
        MyViewPreview()
            .frame(width: 300, height: 200)
            .previewLayout(.sizeThatFits)
    }
}
#endif

// UIViewController variant
struct MyVC_Previews: UIViewControllerRepresentable {
    func makeUIViewController(context: Context) -> MyViewController { MyViewController() }
    func updateUIViewController(_ vc: MyViewController, context: Context) {}
}
```

#### `@IBDesignable` — Interface Builder / Storyboards

```swift
@IBDesignable
class MyCustomView: UIView {

    @IBInspectable var cornerRadius: CGFloat = 8 {
        didSet { layer.cornerRadius = cornerRadius }
    }

    override func prepareForInterfaceBuilder() {
        super.prepareForInterfaceBuilder()
        backgroundColor = .systemOrange
    }
}
```

#### Comparison

| Method | Min Xcode | Storyboard | Hot Reload | Notes |
| --- | --- | --- | --- | --- |
| `#Preview` macro | 15 | ✗ | ✅ | Cleanest, recommended |
| `UIViewRepresentable` | 13 | ✗ | ✅ | Verbose but flexible |
| `@IBDesignable` | Any | ✅ | Partial | IB only, slow to render |
| Simulator | Any | ✅ | ✗ | Always works, slowest |

**Canvas shortcut:** `Editor → Canvas` or `⌥⌘↩`

### Related Topics
#Preview Macro
UIViewRepresentable
IBDesignable and IBInspectable
UIKit vs SwiftUI Interoperability
Xcode Canvas and Live Previews
