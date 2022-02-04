from .generics import Variable, Block

import numpy as np

class Material:
    """
    A chemical property object.

    :param rho: Specific mass (kg/m^3)
    :type rho: float
    """
    def __init__(self, rho=1.0):
        self.rho = rho

class Content(Block):
    """
    Finite mass of material.

    :param material: chemical properties object.
    :type material: cacao.components.thermo.Material

    :param volume: volume of material (m^3)
    :type volume: float
    """
    def __init__(self, material, volume):
        self.material = material
        self.initial_mass  = material.rho * volume