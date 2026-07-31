# Linux Permission System

## 1. Overview

Linux uses a permission model that controls which users can read, write,
or execute files and directories.

Each file has: - **Owner** (user) - **Group** - **Others** -
**Permission bits** (r, w, x)

## 2. Permission Types

-   **r (read)**: View file contents or list directory.
-   **w (write)**: Modify file or add/remove directory contents.
-   **x (execute)**: Run a file as a program or enter a directory.

## 3. Permission Representation

### Symbolic

    rwxr-x---

### Numeric (octal)

-   r = 4\
-   w = 2\
-   x = 1

Example:

    rwxr-x--- = 750

## 4. Changing Permissions

### chmod

    chmod 755 file
    chmod u+x script.sh

### chown (change owner)

    chown user file

### chgrp (change group)

    chgrp dev file

## 5. Special Permissions

### SUID (4xxx)

Run file with owner's privileges.

### SGID (2xxx)

Run with group's privileges or inherit group on directories.

### Sticky Bit (1xxx)

Only owner can delete files in the directory.

Example:

    chmod 1777 /tmp

## 6. Viewing Permissions

    ls -l

## 7. Directory vs File Permissions

-   **Directories need execute (x)** to be entered.
-   **Directories need read (r)** to list contents.
-   **Directories need write (w)** to create/delete files.
