# Difference Between `bash` and `sh` --- And Why Lightweight Images Include Only `sh`

## 1. What Is `sh`?

`sh` is the original Unix **Bourne shell**, designed to be small and
simple.

### Features:

-   Very small binary size
-   Minimal built‑in functions
-   No arrays
-   No advanced string operations
-   No `[[ ]]` syntax
-   Basic scripting only

### In Containers:

-   BusyBox `/bin/sh` is extremely small (sometimes \<200 KB)
-   Alpine's `/bin/sh` is actually `ash`, also lightweight

------------------------------------------------------------------------

## 2. What Is `bash`?

`bash` (Bourne Again Shell) is a **modern, feature‑rich shell** used by
most Linux distros.

### Supports:

-   Arrays
-   Associative arrays
-   `[[ … ]]` conditional tests
-   Brace expansions (`{1..5}`)
-   Command history
-   Tab completion
-   Rich scripting syntax

### Larger size:

-   Usually \~1--1.5 MB binary
-   More dependencies

------------------------------------------------------------------------

## 3. Key Differences (Quick Table)

  Feature                      `sh`             `bash`
  ---------------------------- ---------------- ----------
  Binary size                  **Very small**   Larger
  Included in minimal images   ✔ Yes            ❌ No
  Arrays                       ❌ No            ✔ Yes
  `[[ … ]]` test               ❌ No            ✔ Yes
  Brace expansion `{1..5}`     ❌ No            ✔ Yes
  Associative arrays           ❌ No            ✔ Yes
  Interactive features         Minimal          Rich
  Scripting complexity         Basic            Advanced

------------------------------------------------------------------------

## 4. Why Lightweight Images Do NOT Include Bash

Minimal container images (BusyBox, Alpine, Distroless) are built for:

-   **Small size**
-   **Fast startup**
-   **Low attack surface**
-   **Minimal dependencies**

Including bash would: - Increase image size - Add unnecessary features -
Increase potential vulnerabilities

Typical sizes:

  Image     Shell      Size
  --------- ---------- -----------
  BusyBox   sh         \~1--2 MB
  Alpine    ash (sh)   \~5 MB
  Ubuntu    bash       \~70 MB
  Debian    bash       \~120 MB

This is why cloud‑native best practices recommend using minimal base
images.

------------------------------------------------------------------------

## 5. Why Full Linux Images Include Bash

Full distributions (Ubuntu, CentOS, Debian) are designed for:

-   Human users
-   System management
-   Compatibility with existing scripts

So they include bash by default.

These images prioritize completeness, not size.

------------------------------------------------------------------------

## 6. Why Kubernetes Usually Uses `sh -c`

Since minimal images do not provide bash, commands must be run through
`sh`:

``` yaml
command: ["sh", "-c", "echo hello && sleep 1d"]
```

Using bash in Alpine/BusyBox will fail:

    bash: not found

------------------------------------------------------------------------

## Summary

-   `sh` = minimal, lightweight, always available\
-   `bash` = powerful, large, only in full distros\
-   Lightweight images avoid bash to stay small and secure\
-   Kubernetes commands often use `sh -c` for portability
