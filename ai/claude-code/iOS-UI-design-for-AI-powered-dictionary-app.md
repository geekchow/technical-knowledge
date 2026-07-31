---
title: "iOS UI design for AI-powered dictionary app"
author:
published:
created: 2026-04-16
description: "Claude conversation with 29 messages"
tags:
  - "clippings"
---

# iOS UI design for AI-powered dictionary app

**You**

is there any ios ui design claude skill, that I can make use professional my ios app ai-power-dict ui

---

**Claude**

There's **no dedicated iOS UI design skill** currently available — the skills library covers docx, pptx, xlsx, pdf, frontend-design, and a few examples. Nothing iOS-specific.

Here's what you *can* work with for your `ai-power-dict` app:

**What's available that helps:**

The `frontend-design` skill is the closest fit. It's strong for producing high-quality, polished HTML/CSS UI mockups that you can use as:

- **iOS UI prototypes** (simulated iPhone frames in HTML)
- **Design reference screens** to hand off to SwiftUI developers
- **Interactive demos** of your dictionary app's UX flow

**Practical options for your iOS app:**

1. **Use `frontend-design` skill here** — I can generate pixel-perfect iOS-style HTML mockups of your `ai-power-dict` screens (look up card, word detail, settings, onboarding, etc.) using iOS design tokens (SF Pro fonts, iOS color palette, safe areas, nav bars, tab bars)
2. **Figma / Sketch** — industry standard for real iOS design; no Claude skill for those
3. **SwiftUI preview code** — I can directly write SwiftUI view code for your screens if you prefer working code over mockups

**My suggestion:** Since you prefer plain HTML output, I can create high-fidelity iOS-style HTML mockups of your app screens using the frontend-design skill — simulated in an iPhone 15 shell with proper iOS HIG styling.

Would you like me to do that? If so, tell me:

---

**You**

Q: Which screens should I mock up first for ai-power-dict? (Select all that apply) A: Word lookup / search

Q: What visual style fits your app? A: Colorful / playful

---

**Claude**

Now let me build this — committing to a **candy-bright, bouncy** aesthetic: think Duolingo energy meets a smart dictionary. Rounded everything, vivid color blocks, playful micro-animations.

---

**You**

do it for all the other pages

---

**Claude**

Building all 3 screens in parallel now — Word Detail, AI Chat, and History & Favorites. Keeping the same design language consistent throughout.

---

**You**

the app include these functionality

please adjust your design

---

**Claude**

Got it! Your real nav is: **Word Book · Scan · Review · Settings** + a **Search FAB**. Let me update all 4 screens now.

---

**You**

these are real function page, please update your previously design according to the functionality

---

**Claude**

Now I have the full picture of your real app. Let me rebuild all screens faithfully — same colorful/playful style, but matching your actual features: bilingual definitions, OCR word chips, flashcard review, category word book, and the correct tab bar.

---

**You**

I use claude code to adjust the existing wordbbook ui from image 1 to the expected design you give me as image 2, but it's never achieve it, so how to do with it

---

**Claude**

Looking at the two images, the gap is clear. Let me give you the **exact SwiftUI code** to achieve Image 2, which you can paste directly or give to Claude Code as a concrete reference.

---

**You**

do the same for ai power dict detail page

---

**Claude**

Let me study the detail page design I created and the real app screenshots carefully before writing the SwiftUI.

---

**You**

do the same for Ai power dict scan page

---

**Claude**

Let me read the scan design file first.

---

**You**

do the same for Ai power dict review

---

**Claude**

Got every spec. Building now.

---

**You**

do the same thing for Ai power dict search page

---

**Claude**

Every spec extracted. Building now.

---

**You**

here the other pages from the real app, please redesign them align design style with previous 5 pages such as detail, review, scan pages

---

**Claude**

Let me study all 3 screenshots carefully before writing a single line of code.

---

**You**

please generate the pages in html format, then i can preview them

---

**Claude**

All 3 pages ready to preview. Here's what's in each:

---

**📷 Scan Camera** — teal/green gradient bg

- 3-layer animated hero: outer pulsing ring → mid opacity ring → `#6C63FF→#4ECDC4` gradient circle with SVG scan-frame icon
- Primary "Choose from Library" button: `#007AFF→#0056CC` gradient with blue shadow
- Secondary "Take Photo": blue-tinted border button
- Yellow `#FFF5CC` tip strip at bottom — stagger-animates in last

---

**✅ Empty Review** — matching purple bg from ReviewView

- 4-layer animated check circle: glow pulse → gradient stroke ring (`#6C63FF→#4ECDC4`) → tinted fill → spring-in SVG checkmark
- "Refresh" button: `#6C63FF→#FF6EB4` gradient Capsule with indigo shadow
- "Go to Word Book" indigo-tinted secondary
- Streak strip at bottom — **pixel-identical** to ReviewView so the empty/filled states feel like one screen

---

**⚙️ Settings** — pink/coral gradient bg

- Membership card: blue-tinted circle avatar icon + "Upgrade to Premium" blue CTA
- Language checkmark: **indigo `#6C63FF`** ← signals vocabulary
- Appearance checkmark: **orange `#FF9F43`** ← intentionally different colour
- About rows: each has its own coloured rounded-square icon badge (indigo/teal/orange/coral) — same pattern as the Word Book word list rows, keeping the whole design system coherent

---

**You**

all ui are good now, except the bottom bar isn't right

---

**Claude**

Looking at your screenshot carefully: the real tab bar has **one white pill** containing all 4 tabs, with the search as a **separate circle** to the right. My mockups have it split wrong. Let me fix all 8 files at once.

---

**You**

misunderstand me, I like your design of the bottom bar, but the actually one is unchanged, please give prompt and sample swift code to make it adhere to you design

---

**Claude**

Got it — you want your real app's tab bar to look like my HTML design (the floating pill + search circle). Here's the SwiftUI code + Claude Code prompt.

---

**Claude**

mobile application development
