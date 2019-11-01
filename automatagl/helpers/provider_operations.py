from collections import namedtuple


# Provider data structures
ProviderUser = namedtuple('ProviderUser', ['username', 'keys'])
ProviderConfig = namedtuple(
    'ProviderConfig', [
        'provider',
        'config',
    ]
)

# Automata data structures
AutomataGroupConfig = namedtuple(
    'AutomataGroupConfig', ['provider_group', 'linux_group', 'sudoers_line', 'other_groups']
)
AutomataConfig = namedtuple(
    'AutomataConfig', [
        'groups',
        'sudoers_file',
        'home_dir_path',
        'protected_uid_start',
        'protected_gid_start',
    ]
)
