# Why Kubernetes Commands Use `sh -c`

When specifying a container command in Kubernetes such as:

``` yaml
spec:
  containers:
  - command:
    - sh
    - -c
    - touch /tmp/ready && sleep 1d
    image: busybox:1.31.0
```

You must include:

    - sh
    - -c

before the actual command string. Here's why.

------------------------------------------------------------------------

## 1. Kubernetes Executes Commands in *Exec Form*, Not a Shell

Kubernetes treats the `command:` field as an array that maps directly
to:

    exec(["cmd", "arg1", "arg2", ...])

This means **no shell is involved by default**, and Kubernetes does NOT
interpret:

-   `&&`
-   `|`
-   `>`
-   variable expansion (`$VAR`)
-   multiple commands

Example of what *does not* work:

    command:
      - touch /tmp/ready && sleep 1d

Because `&&` is a shell operator --- but no shell exists to interpret
it.

------------------------------------------------------------------------

## 2. `sh -c` Explicitly Runs the Command Through a Shell

Using:

``` yaml
command:
  - sh
  - -c
  - touch /tmp/ready && sleep 1d
```

kubelet executes:

    exec(["sh", "-c", "touch /tmp/ready && sleep 1d"])

This starts `/bin/sh` and evaluates the full string as a proper shell
command.

------------------------------------------------------------------------

## 3. Why Not `bash`?

Minimal images like BusyBox and Alpine **do not include bash**, only
`sh`.

If using Ubuntu or other full OS images, you *may* use:

``` yaml
command: ["bash", "-c", "echo hello"]
```

But Kubernetes never adds bash automatically.

------------------------------------------------------------------------

## Summary Table

  Feature                            Without `sh -c`    With `sh -c`
  ---------------------------------- ------------------ --------------
  Shell operators (`&&`, `|`, `>`)   ❌ Not supported   ✔ Works
  Variable expansion (`$VAR`)        ❌ Fails           ✔ Works
  Multiple commands                  ❌ Fails           ✔ Works
  Behaves like shell script          ❌ No              ✔ Yes

------------------------------------------------------------------------

## Key Point

> Kubernetes does not interpret complex command strings unless you
> explicitly run them under a shell using `sh -c`.
