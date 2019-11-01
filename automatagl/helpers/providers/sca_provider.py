from typing import List
import os
import json
import requests

from automatagl.helpers.providers.base_provider import BaseProvider
from automatagl.helpers.provider_operations import ProviderUser

# ---
# config:
#   provider: sca
#   provider_config:
#     sca_address: https://sca.address.com/api
#     username: username
#     password: password


class SCAProvider(BaseProvider):

    config: dict
    api_address: str
    jwt_token: str
    header: dict

    def __init__(self, config: dict):
        super().__init__(config)
        self.address = self.config['api_address']
        self.jwt_token = self.__get_jwt_token(
            config['username'],
            config['password'],
        )
        self.header = {"Authorization": "Bearer {}".format(self.jwt_token)}

    def get_users_from_group(self, group: str) -> List[ProviderUser]:
        group = self.get_group_from_sca(group)
        if not group:
            return []
        group_info_path = self.generate_full_path('group/{}'.format(group['id']))
        group_info = json.loads(requests.get(group_info_path, headers=self.header).text)
        users = list()
        for u in group_info['users']:
            users.append(ProviderUser(username=u['username'], keys=[k['pub_ssh_key'] for k in u['keys']]))
        return users

    def get_group_from_sca(self, group: str) -> dict:
        path = self.generate_full_path('groups')
        groups = json.loads(requests.get(path, headers=self.header).text)
        group_query = [g for g in groups if g['name'] == group]
        if group_query:
            return group_query[0]
        return {}

    def generate_full_path(self, relative_path: str):
        return os.path.join(self.address, relative_path)

    def __get_jwt_token(self, username: str, password: str):
        payload = {
            "username": username,
            "password": password,
        }
        path = self.generate_full_path('login')
        response = json.loads(requests.post(path, json=payload).text)
        if 'access_token' not in response.keys():
            raise SCANotAuthorized(response["message"])
        return response['access_token']


class SCAError(Exception):
    pass


class SCANotAuthorized(SCAError):

    def __init__(self, message):
        self.message = message
