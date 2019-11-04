# Automata

Automata is a user management script that uses different providers as a source for
user information.  Automata can grab the users associated with a specific
group and create user accounts on a Linux/UNIX server based on those
users.

Automata generates a custom `/etc/sudoers.d` access file to give permissions
to each users as well as populate the user's `authorized_keys` file with the
keys associated with that user's account.

Latest commit status: ![](https://travis-ci.com/JamesTheBard/automata_ng.svg?branch=master) [More Info](https://travis-ci.com/JamesTheBard/automata_ng)

# Supported Providers

- **Gitlab** via Gitlab API token
- **SCA** via username/password

## Configuration

All configuration options are contained within the `/etc/automata/automata.yaml` file.


```yaml
# vim:ts=2:sts=2:sw=2:et
---
config:
  provider: gitlab
  config:
    api_address: "https://gitlab.myserver.com/api/v4"
    api_token: "abcdefg1234567"
server:
  sudoers_file: "/etc/sudoers.d/automata"
  home_dir_path: '/home'
  protected_uid_start: 500
  protected_gid_start: 500
  groups:
    open-source:
      linux_group: open_source
      sudoers_line: 'ALL=(ALL) NOPASSWD: ALL'
      other_groups:
        - docker
    another-group:
      linux_group: another_group
      sudoers_line: 'ALL=(ALL) NOPASSWD: ALL'
logging:
  log_level: debug
  log_path: /var/log/automata.log
  log_format: '%(asctime)s [%(levelname)s] %(message)s'
```

- `config`: This is where the provider configuration lives.
    - `provider`: The provider to use to get authentication information.  Currently supported providers are Gitlab and SCA.
    - `provider_config`: The neccessary configuration options to pass to the provider.  This will be specific to the provider.
- `server`: These are settings specific to the server _Automata_ is installed on.
    - `sudoers_file`: The location of the sudoers file to create.
    - `home_dir_path`: The base path for all user home directories created by `automata`
    - `protected_uid_start`: The user ID where standard users live.  Any user with an ID less than `protected_uid_start` will not be deleted (thus protected)
    - `protected_gid_start`: The group ID where standard groups live.  Any group with an ID less than `protected_gid_start` will not be deleted.
    - `groups`: All user/group mapping and sudoers configuration information goes under this key.  Each key under this should be the provider
    group name to use for authentication.  In the example above, the group being used is the `open-source` group using the Gitlab provider.  You
    can specify more than one group, users in the top-most groups will take precedence over the groups defined below them.
        - `linux_group`: The group on the target server to use.  This group will be created if it doesn't exist, and any user in the
        Gitlab `open-source` group will be created as part of that group.
        - `sudoers_line`: The settings for the users created by `automata`.  The line will be prepended with the proper group information.
        - `groups`: Additional groups to associate with the users being created by automata.
- `logging`: Logging options for Automata
  - `log_level`: The logging levels available are `debug`, `info`, and `warn`.
  - `log_path`: The location of the Automata log file.  This file will be
  created on Automata's first run.
  - `log_format`: The format to use when logging.  This script uses Python's
  `logging` module, and this format should mirror what that module would use.

## Provider-specific Configurations

All of these settings will live in the `automata.yaml` configuration file under `config`.

### Gitlab

```yaml
provider: gitlab
config:
  api_address: "https://gitlab.myserver.com/api/v4"
  api_token: "abcdefg1234567"
  only_active: true
```

- `api_address`: The API endpoint for the Gitlab server
- `api_token`: The token used for authentication for Gitlab
- `only_active`: Only create accounts for users who's state is `active`

### SCA

```yaml
provider: sca
config:
  api_address: "https://scaserver.com"
  username: "username"
  password: "password"
```

- `api_address`: The address of the SCA server
- `username`: The username to authenticate as.
- `password`: The password of the aforementioned username.

**NOTE**: Do _not_ place the user that _Automata_ uses to query SCA into the primary group (or group ID `1`).  This would
give that user the ability to change users/groups.

## Installation

You will need to install Python 3 for this to work.  It will not work under Python 2 without some major changes.

The easiest way to install this would be to use the package hosted at `https://pypi.fury.io/jweatherly/automatagl`.
The basic command to get this going is `pip3 install --index-url https://pypi.fury.io/jweatherly/ 
--extra-index-url https://pypi.org/simple/
automatagl`

You can also clone the repository and point `pip` at the repository which will be the freshest stuff you can
install.
