# Providers

Providers are very simple to setup.  The provider used is dictated by the `config` -> `provider` configuration option.
This string is used to figure out which class to call via the `automata_providers` dictionary located in the `__init__.py`
file (`automatagl.helpers.providers.__init__`).

If you want to make a new provider, the `BaseProvider` class has a template of all the things necessary.  In short,
it will be given the group name (`str`) via the `get_users_from_group` method, and be expected to return a list of
`ProviderUser`s.  The ProviderUsers is located in the `provider_operations` module, and is basically a `namedtuple`
that consists of a `username` and the public SSH `keys`s associated with that user.
