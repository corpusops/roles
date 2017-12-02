# ansible role that async-wraps template/copy

Wrapper that run multiple files generation (wrapper of: copy/template)
that runs in parallel (async).

When you have lot of files to generate at once, it will increase a lot performance.

- See [tests](./test.yml)

