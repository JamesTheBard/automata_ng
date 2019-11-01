from typing import List

from automatagl.helpers.provider_operations import ProviderUser


class BaseProvider:

    config: dict

    def __init__(self, config: dict) -> None:
        self.config = config

    def get_users_from_group(self, group: str) -> List[ProviderUser]:
        pass
