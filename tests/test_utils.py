import unittest

import cacao
from cacao.components import Tank, Orifice, Material, Content


class TestUtils(unittest.TestCase):
    def test_tank(self):
        water = Material(rho=1000)

        A = 16 # m2 area of tank
        content_tank = Content(water, volume=10*A)

        # tank model
        tank1 = Tank([0], A, content_tank)


        self.assertEqual(tank1.area, A)
        
if __name__ == '__main__':
    unittest.main()