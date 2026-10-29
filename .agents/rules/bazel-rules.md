---
trigger: always_on
---

# Rules for Bazel

## One target per source file

We want a fine-grained Bazel target structure.
This means as much as possible we want a single source file to have its own Bazel target.

There are exceptions such as `cc` where we will have multiple files associated with a single target.

### Python

One target per source file.

### Go

One target per source file.

### Rust

One target per source file.

### CC

Source files will be grouped into `.cc`, `.hh`, and `.inl` files sharing the same stem.
`something.cc`, `something.hh`, `something.inl` will be in the same `something` target.

If any of these extensions are missing they will be elided from the target.

## Target Names the same as the Source File

We want to be able to know the target name for a source file using only a naming convention.
Using Bazel to query for a source file's target is extensive and time-consuming.

If we have a source file `something.py`, it's target should be named `something`.

If we have two files with the same stem like `main.py` and `main.go`, we can use the extension in the target name like `main_py` and `main_go`.