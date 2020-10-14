# -*- mode: python -*-

DOCUMENTATION = '''
---

This will define facts if not set something like:

    ansible_lsb:
      "codename": "xenial"
      "description": "Ubuntu 16.04.1 LTS"
      "id": "Ubuntu"
      "major_release": "16"
      "release": "16.04"
'''

EXAMPLES = """
In a Playbook "muche":

    - In playbook/foo.yml:

        - cops_lsb_release
"""
