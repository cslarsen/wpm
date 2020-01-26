import os
import unittest

import wpm.config


class ConfigTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        wpm.config.Config.persist = False

    def test_default_config_file_is_resolved_to_homedir(self):
        config = wpm.config.Config()
        self.assertEquals(config.filename, os.path.expanduser("~/.wpmrc"))

    def test_custom_config_file_is_resolved_relative_to_workingdir(self):
        custom_config = ".wpmrc"
        config = wpm.config.Config(custom_config)
        self.assertEquals(config.filename, os.path.abspath(custom_config))

    def test_custom_config_file_with_user_path_is_resolved(self):
        custom_config = "~/.config/wpm/wpmrc"
        config = wpm.config.Config(custom_config)
        self.assertEquals(config.filename, os.path.expanduser(custom_config))
