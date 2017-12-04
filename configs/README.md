# ansible role that wraps filestemplate/copy

Wrapper that run multiple files generation (wrapper of: file/template/copy)

This can run in parallel (async).

NOTE: for now this run sync as ansible does not support yet (in a near future)
See: https://github.com/ansible/ansible/issues/32265


When you have lot of files to generate at once,
it will increase a lot performance.

- See:
    - [tests1](./test_role/tasks/main.yml)
    - [tests caller](./test.yml)

- order: files, templates, filecopys

