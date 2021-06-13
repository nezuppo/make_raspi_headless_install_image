#!/usr/bin/env python3

import os

from ansible.module_utils.basic import (
    AnsibleModule,
)

def get_file_path(entries, params):
    length = len(entries)

    if length == 0:
        return False, None

    if length == 1:
        assert entries[0].endswith('.' + params['check_extension']), entries[0]
        return True, os.path.join(params['target_dir'], entries[0])

    raise Exception()

def main():
    module = AnsibleModule(
        argument_spec = dict(
            target_dir = dict(required=True),
            check_extension = dict(required=True),
        )
    )

    entries = os.listdir(module.params['target_dir'])

    gitignore = '.gitignore'
    if gitignore in entries:
        entries.remove(gitignore)

    is_exist, file_path = get_file_path(entries, module.params)

    module.exit_json(
        is_exist = is_exist,
        file_path = file_path,
    )

if __name__ == '__main__':
    main()
