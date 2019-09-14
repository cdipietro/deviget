import logging
import os
import sys
import yaml
from itertools import product as lists_product


from minesweeper import (
    PACKAGE_NAME,
    PACKAGE_PATH,
)
from minesweeper.common.exceptions import MinesweeperException


class Config(dict):
    """Dictionary-like class for loading and storing application configuration values from configuration files.
    """

    config_search_paths = [
        os.path.join(PACKAGE_PATH, 'config'),
        os.path.join(os.getenv('HOME'), f'.config/{PACKAGE_NAME}'),
        os.path.join('/etc', PACKAGE_NAME),
    ]
    config_extensions = ['yml', 'yaml']
    config_basenames = ['config', 'conf', 'cfg']

    def load(self, config_file=None):
        """Loads configuration values from configuration files.

        :param config_file: Path to the application configuration file
        :type config_file: str

        :raises MinesweeperException: If `config_file` is not provided and one can't be found among the
        `config_search_paths`.
        """
        # Clear any previous stored configuration values
        self.clear()

        # Get user given config file or look for it in the config search paths
        config_file = config_file or self._find_config_file()

        # If no configuration file was found, raise an exception
        if not config_file or not os.path.isfile(config_file):
            raise MinesweeperException(f'Could not find configuration file for {PACKAGE_NAME.title()}.')

        # Otherwise, load all its configuration values
        with open(config_file, encoding='utf8') as cfg:
            config_data = yaml.load(cfg, Loader=yaml.FullLoader)
            for key, value in config_data.items():
                self[key] = value

    @classmethod
    def _find_config_file(cls):
        """Searches for configurations files among the directores listed in `Confg.config_search_paths`.

        return: Returns the path of the configuration file, if found. Otherwise, it returns `None`
        rtype: str | None
        """
        expected_config_filenames = ['.'.join(x) for x in lists_product(cls.config_basenames, cls.config_extensions)]
        for path in cls.config_search_paths:
            if os.path.isdir(path):
                for file in os.listdir(path):
                    if os.path.isfile(os.path.join(path, file)) and file in expected_config_filenames:
                        return os.path.join(path, file)


config = Config()
