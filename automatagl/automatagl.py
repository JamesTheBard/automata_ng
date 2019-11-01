#!/usr/bin/env python3

import logging
import os
import sys

from automatagl.helpers.config_parser import ConfigOps, sanitize_username
from automatagl.helpers.ssh_key_object import SSHKeyObject
from automatagl.helpers.user_operations import (
    UserOps, UOGroupNotFoundError, UOProtectedUserError, UOUserAlreadyExistsError
)
from automatagl.helpers.providers import automata_providers


def main():

    working_dir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(working_dir)

    # Grab configuration information
    config_ops = ConfigOps(filename='/etc/automata/automata.conf')

    # Logging configuration
    logging_config = config_ops.get_logging_config()
    logging.basicConfig(**logging_config)

    # Provider configuration
    provider_config = config_ops.get_provider_config()
    provider_ops = automata_providers[provider_config.provider](config=provider_config.config)

    # Automata configuration
    automata_config = config_ops.get_server_config()

    # Set host environment and user operations stuff
    default_shell = '/bin/bash'
    host_env = os.environ.copy()
    host_env["PATH"] = "/bin:/sbin:/usr/bin:/usr/sbin" + host_env["PATH"]
    user_ops = UserOps(
        host_env=host_env,
        default_shell=default_shell,
        base_dir=automata_config.home_dir_path,
        protected_uid_start=automata_config.protected_uid_start,
        protected_gid_start=automata_config.protected_gid_start,
    )

    # Get all members of a given group
    logging.debug("Processing {} groups from the config file.".format(len(automata_config.groups)))

    # Create a cache of created users.
    finished_users = list()

    # Start by parsing each group.
    for group in automata_config.groups:
        logging.debug("Querying users in group '{}'.".format(group.provider_group))
        members = provider_ops.get_users_from_group(group.provider_group)

        # Get associated SSH keys for members
        ssh_list = list()
        for member in members:
            ssh_obj = SSHKeyObject(username=member.username)
            logging.debug("Querying user SSH key information for {}.".format(member.username))
            ssh_obj.add_keys(member.keys)
            ssh_list.append(ssh_obj)

        # Get list of user accounts in the group from the '/etc/group' file
        try:
            linux_group_id = user_ops.get_group_gid(group.linux_group)
        except UOGroupNotFoundError:
            logging.info("Group not found, creating the '{}' group.".format(group.linux_group))
            user_ops.create_group(group.linux_group)
            linux_group_id = user_ops.get_group_gid(group.linux_group)

        # Start removing users with extreme prejudice that are no longer in the GitLab group.
        current_users = user_ops.get_all_users_in_group(linux_group_id)
        provider_users = {sanitize_username(i.username) for i in ssh_list}
        removed_users = current_users - provider_users
        if removed_users:
            logging.info("Found {} users to delete in group {}: {}".format(
                len(removed_users),
                group.linux_group,
                ', '.join(removed_users),
            ))
        else:
            logging.info("No users to delete in group {}.".format(group.linux_group))

        # Deleting users that have been removed
        for user in removed_users:
            logging.info("Deleting user {}.".format(user))
            try:
                user_ops.delete_user(user)
            except UOProtectedUserError:
                logging.info("Cannot delete user '{}' as it is a protected system user.".format(user))
                sys.exit(101)

        # Create new users in group
        created_users = provider_users - current_users
        if created_users:
            logging.info("Found {} users to create in group {}: {}".format(
                len(created_users),
                group.linux_group,
                ', '.join(created_users),
            ))
        else:
            logging.info("No users to add to group {}.".format(group.linux_group))

        for user in created_users:
            if user not in set(finished_users):
                logging.info("Creating user {}.".format(user))
                user_data = {
                    "user": user,
                    "group": group.linux_group,
                    "groups": group.other_groups,
                }
                try:
                    user_ops.create_user(**user_data)
                except UOUserAlreadyExistsError:
                    logging.info("User '{}' already exists, deleting user.".format(user))
                    try:
                        user_ops.delete_user(user)
                    except UOProtectedUserError:
                        logging.info("Cannot delete user '{}' as it is a protected system user.".format(user))
                        sys.exit(101)
                    logging.info("Recreating user '{}'.".format(user))
                    user_ops.create_user(**user_data)
            else:
                logging.info("Skipping user {}, handled previously in another group.".format(user))

        # Create the SSH authorized_keys file so the user can actually log in.
        for ssh_keys in ssh_list:
            user_ops.populate_ssh_file(
                ssh_keys=ssh_keys,
                gid=linux_group_id,
            )

        # Add users to the finished_users table
        finished_users = list(set(provider_users).union(finished_users))
        logging.debug("Finished users list now contains {} members.".format(len(finished_users)))

    # Create the sudoers.d file.
    logging.info("Regenerating the '{}' file.".format(automata_config.sudoers_file))
    user_ops.generate_sudoers_file(automata_config.sudoers_file, automata_config.groups)
