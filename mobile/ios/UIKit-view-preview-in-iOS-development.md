---
title: "UIKit view preview in iOS development"
author:
published:
created: 2026-04-16
description: "Claude conversation with 3 messages"
tags:
  - "clippings"
---

# UIKit view preview in iOS development

**You**

iOS development with UIKit, how to preview a view

---

**Claude**

## Previewing UIKit Views in Xcode

There are several approaches, from modern to legacy:

---

### 1\. #Preview Macro (Xcode 15+ / iOS 17+) — Recommended

The simplest modern approach:

```swift
import UIKit

class MyView: UIView {
    override init(frame: CGRect) {
        super.init(frame: frame)
        backgroundColor = .systemBlue
        // setup...
    }
    required init?(coder: NSCoder) { fatalError() }
}

// At the bottom of the file:
#Preview {
    MyView()
}
```

Works for both `UIView` and `UIViewController`:

```swift
#Preview {
    let vc = MyViewController()
    return vc
}
```

---

### 2\. UIViewRepresentable Wrapper (Xcode 13–14, SwiftUI Previews)

Wrap your UIKit view in a SwiftUI-compatible struct:

```swift
import SwiftUI

struct MyViewPreview: UIViewRepresentable {
    func makeUIView(context: Context) -> MyView {
        return MyView()
    }
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
```

For a `UIViewController`:

```swift
struct MyVC_Previews: UIViewControllerRepresentable {
    func makeUIViewController(context: Context) -> MyViewController {
        return MyViewController()
    }
    func updateUIViewController(_ vc: MyViewController, context: Context) {}
}
```

---

### 3\. @IBDesignable — Interface Builder Live Rendering

If you still use Storyboards/XIBs:

```swift
@IBDesignable
class MyCustomView: UIView {

    @IBInspectable var cornerRadius: CGFloat = 8 {
        didSet { layer.cornerRadius = cornerRadius }
    }

    override func prepareForInterfaceBuilder() {
        super.prepareForInterfaceBuilder()
        // Called only in IB, set up mock data here
        backgroundColor = .systemOrange
    }
}
```

IB will render the view live in the canvas — no build/run needed.

---

### Comparison

| Method | Min Xcode | Storyboard | Hot Reload | Notes |
| --- | --- | --- | --- | --- |
| `#Preview` macro | 15 | ✗ | ✅ | Cleanest, recommended |
| `UIViewRepresentable` | 13 | ✗ | ✅ | Verbose but flexible |
| `@IBDesignable` | Any | ✅ | Partial | IB only, slow to render |
| Simulator | Any | ✅ | ✗ | Always works, slowest |

---

### Tips

- Enable the **Canvas** panel: `Editor → Canvas` (or `⌥⌘↩`)
- Wrap preview code in `#if DEBUG ... #endif` to exclude from production builds
- The `#Preview` macro supports **multiple named previews** in one file:

```swift
#Preview("Dark Mode") {
    let v = MyView()
    v.overrideUserInterfaceStyle = .dark
    return v
}

#Preview("Light Mode") {
    MyView()
}
```

---

**Claude**

mobile application development
