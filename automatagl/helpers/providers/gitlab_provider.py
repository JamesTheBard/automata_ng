from collections import namedtuple
from typing import List
import json
import os
import requests

from automatagl.helpers.provider_operations import ProviderUser
from automatagl.helpers.providers.base_provider import BaseProvider

__all__ = [
    'GitlabProvider',
    'GLConnectionError',
    'GLApiQueryError',
]

GitlabUser = namedtuple('GitlabUser', ['id', 'username'])


class GitlabProvider(BaseProvider):
    """
    This module handles all of the communications for users and groups in Gitlab.
    """

    api_token: str
    api_address: str
    config: dict
    payload_token: dict

    def __init__(self, config: dict) -> None:
        """
        :param config: The Gitlab configuration settings from Automata
        """
        super().__init__(config)
        self.api_token = config['api_token']
        self.api_address = config['api_address']
        self.payload_token = {
            'private_token': self.api_token,
        }

    def get_users_from_group(self, group: str, only_active: bool = True) -> List[ProviderUser]:
        """
        Get all users from a Gitlab Group
        :param group: The group name in Gitlab
        :param only_active: Whether to pull all users or only the active ones in Gitlab
        :return: A GitlabUser object with the user information
        """
        users = list()
        path = os.path.join(self.api_address, 'groups/{}/members'.format(group))
        response = self.__process_response_from_server(path)
        if only_active:
            members = [GitlabUser(id=i['id'], username=i['username']) for i in response if i['state'] == 'active']
        else:
            members = [GitlabUser(id=i['id'], username=i['username']) for i in response]
        for member in members:
            users.append(
                ProviderUser(
                    username=member.username,
                    keys=self.__get_keys_from_user_id(member.id)
                )
            )
        return users

    def __get_keys_from_user_id(self, user_id: int) -> list:
        """
        Get all SSH public keys associated with a given user ID.
        :param user_id: The user ID to query
        :return: A list of SSH public keys associated with the user ID.
        """
        path = os.path.join(self.api_address, 'users/{}/keys'.format(user_id))
        response = self.__process_response_from_server(path)
        keys = [i["key"] for i in response]
        return keys

    def __process_response_from_server(self, path) -> List[dict]:
        """
        Performs queries to the Gitlab server and process the response for common errors/issues
        :param path: The path to query
        :return: The response object
        :raises GLApiQueryError: On any errors returned by the GL server query
        :raises GLConnectionError: On any connection issues with the GL server
        """
        try:
            response = json.loads(requests.get(path, params=self.payload_token).text)
        except requests.exceptions.ConnectionError:
            raise GLConnectionError
        if isinstance(response, dict):
            if "error" in response.keys():
                raise GLApiQueryError(message=response["error_description"])
            elif "message" in response.keys():
                raise GLApiQueryError(response["message"])
            else:
                raise GLApiQueryError(response[response])
        return response


class GLError(Exception):
    pass


class GLConnectionError(GLError):
    pass


class GLApiQueryError(GLError):

    def __init__(self, message):
        self.message = message
