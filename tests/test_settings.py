import unittest
import os

from context import cacao

from cacao.core.management import load_settings

class MultiplicationTestCase(unittest.TestCase):

    def setUp(self):
        self.project_name = 'testing098ACD'
        self.settings = load_settings(self.project_name)

    def test_base_path(self):
        """Test BASE PATH from settings"""

        base_path = self.settings['BASE_PATH']
        expected_base_path = os.path.join(os.getcwd(), self.project_name)
        self.assertEqual(expected_base_path, base_path)

if __name__ == '__main__':
    unittest.main()