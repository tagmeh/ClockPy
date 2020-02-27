import unittest
import os

from lib import constants
from lib import utils


'''
Unittesting 
https://docs.python.org/3/library/unittest.html

To run tests:
    Navigate to ~/Clockpy (root directory)
    run "python -m unittest -v" to auto-discover and run the tests
    run "python -m unittest -v tests/test_*.py" to specify a test file
'''


class TestUtils(unittest.TestCase):

    def test_create_default_config_file(self):
        """
        Tests if the create_default_config_file function successfully creates a new config.ini file
        in the /files/ directory.
        """
        # Make it so there is never a config.ini file before the function runs.
        if os.path.exists(os.path.join(constants.FILES, 'config.ini')):
            os.remove(os.path.join(constants.FILES, 'config.ini'))

        utils.create_default_config_file()

        assert os.path.exists(os.path.join(constants.FILES, 'config.ini'))


if __name__ == '__main__':
    unittest.main()
