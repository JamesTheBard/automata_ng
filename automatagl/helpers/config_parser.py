from pathlib import Path
import logging
import re
import sys
import yaml

from automatagl.helpers.provider_operations import AutomataGroupConfig, ProviderConfig, AutomataConfig

# Dictionary to translate logging levels in the config file
log_level_dict = {
    "info": logging.INFO,
    "warning": logging.WARN,
    "debug": logging.DEBUG,
}


class ConfigOps:
    """
    Responsible for parsing the configuration file for information relating to automata.
    """

    filename: str
    raw_config: dict
    provider_config: dict
    logging_config: dict
    api_token_env: str

    def __init__(self, filename: str, api_token_env: str = 'GL_API_TOKEN') -> None:
        """
        :param filename: Configuration file name
        :param api_token_env: Gitlab API token environment variable.
        """
        self.filename = filename
        self.raw_config = self.__import_config(filename)
        self.provider_config = self.raw_config['config']
        self.server_config = self.raw_config['server']
        self.logging_config = self.raw_config['logging']
        self.api_token_env = api_token_env

    def get_logging_config(self) -> dict:
        """
        Returns the logging configuration contained in the `raw_config` variable after some massaging.
        :return: LoggingConfig object
        :raises COInvalidLogLevel: Thrown if log level isn't defined in the log level dictionary.
        """
        if self.logging_config["log_level"] not in log_level_dict.keys():
            raise COInvalidLogLevel
        return {
            "level": log_level_dict[self.logging_config['log_level']],
            "filename": self.logging_config['log_path'],
            "format": self.logging_config['log_format'],
        }

    def get_server_config(self) -> AutomataConfig:
        """
        Return the Automata base configuration from the config file
        :return: AutomataConfig object
        """
        group_data = list()
        group_info = self.server_config['groups']
        for k, v in group_info.items():
            try:
                other_groups = v['other_groups']
            except KeyError:
                other_groups = list()

            temp = AutomataGroupConfig(
                provider_group=k,
                linux_group=v['linux_group'],
                sudoers_line=sanitize_sudoers_line(v['sudoers_line']),
                other_groups=other_groups,
            )
            group_data.append(temp)

        protected_uid_start = 1000
        protected_gid_start = 1000
        if 'protected_uid_start' in self.server_config.keys():
            protected_uid_start = self.server_config['protected_uid_start']
        if 'protected_gid_start' in self.server_config.keys():
            protected_gid_start = self.server_config['protected_gid_start']

        return AutomataConfig(
            groups=group_data,
            sudoers_file=self.server_config['sudoers_file'],
            home_dir_path=self.server_config['home_dir_path'],
            protected_uid_start=protected_uid_start,
            protected_gid_start=protected_gid_start,
        )

    def get_provider_config(self) -> ProviderConfig:
        """
        Returns the provider configuration object for the Provider
        :return: ProviderConfig object
        """
        # Get provider information
        provider = self.provider_config['provider']
        provider_config = self.provider_config['provider_config']
        return ProviderConfig(
            provider=provider,
            provider_config=provider_config,
        )

    @staticmethod
    def __import_config(filename: str) -> dict:
        """
        Parses the configuration file
        :param filename: The file to parse the configuration from
        :return: The contents of the configuration file after being parsed.
        """
        path = Path(filename)
        perms = path.stat().st_mode
        if bool(perms % 0o100):
            print("WARNING: The permissions on '{}' must be set to restrict access from all users. Consider changing "
                  "the permissions to 400 or more secure.".format(filename))
            sys.exit(15)
        with open(filename, 'r') as stream:
            try:
                return yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)


def sanitize_username(username: str) -> str:
    """
    Remove non-word characters from a username
    :param username: The username to sanitize
    :return: The sanitized username
    """
    illegal_chars = r'[^\w]'
    return re.sub(illegal_chars, '_', username)


def sanitize_sudoers_line(sudoers_line: str) -> str:
    """
    Sanitize the sudoers file line
    :param sudoers_line: The line of the sudoers file
    :return: The sanitized sudoers file line
    """
    illegal_chars = r'\s+'
    return re.sub(illegal_chars, ' ', sudoers_line)


class COError(Exception):
    pass


class COInvalidLogLevel(COError):
    pass
