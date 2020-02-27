import os
from lib import constants


"""
The home of utility functions
"""


def create_default_config_file():
    """
    Copies the contents of "default_config.txt" over to "config.ini".
    Creates the config.ini file if it doesn't already exist.
    """

    with open(os.path.join(constants.FILES, 'config.ini'), 'w+') as c:  # open/create for writing
        # for line in constants.DEFAULT_CONFIG.splitlines():
        c.write(constants.DEFAULT_CONFIG)



