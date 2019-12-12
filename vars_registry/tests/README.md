# timing for testing various forms of registry implementation

Test command
```sh
# for each test
time ( for i in $(seq 20);do ../../../bin/ansible-playbook <test>/t.yml ;done )

- pre: ``1m23,432s``
- post: ``0m53,882s``
- **post_with_dict: ``0m53,534s``**


Demonstration that ``post_with_dict`` is for now the fatest and cleanest implementation of our registry use case.
