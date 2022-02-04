from .generics import Block, Constant, Variable, Constraint

from scipy import interpolate
import numpy as np

g = 9.81 # m/s2 gravity

class Tank(Block):
    """
    Create a container (vessel, reservoir, etc) unit that has liquid holdup and one or more inlets and outlets.

    :param time_vec: An array defining time steps.
    :type client: Iterable

    :param area: Cross-section area (m^2)
    :type bounds: float
    :param content: The characteristics of the material inside the tank.
    :type bounds: cacao.components.thermo.Content

    """
    def __init__(self, time_vec, area, content):
        super().__init__()
        self.inlet = []
        self.outlet = []
        self.mass = Variable(time_vec)
        self.height = Variable(time_vec)
        self.area = area
        self.content = content

        self.mass[0] = content.initial_mass # initial condition

        def mass_balance(block):
            dmdt = np.diff(block.mass())/np.diff(block.time)
            inflow = np.zeros_like(block.time)
            for block2 in block.inlet:
                inflow += block2.mass_flow_rate()
            outflow = np.zeros_like(block.time)
            for block2 in block.outlet:
                outflow += block2.mass_flow_rate()
            resid = dmdt - (inflow[1:] - outflow[1:])
            return resid

        self.mass_balance = Constraint(mass_balance)

        def volume_height(block):
            resid = block.mass() - block.area * content.material.rho * block.height()
            return resid

        self.volume_height = Constraint(volume_height)

class Orifice(Block):
    """
    Create an orifice. i.e a duct where liquid flows due to upstream pressure.

    :param time_vec: An array defining time steps.
    :type client: Iterable

    :param area: Cross-section area of the orifice (m^2).
    :type bounds: float
    :param c: Outflow coefficient due to orifice properties, normally obtained empirically.
    :type bounds: float

    """
    def __init__(self, time_vec, area, c):
        super().__init__()
        self.mass_flow_rate = Variable(time_vec)
        self.area = area
        self.inlet = []
        self.outlet = []

        def outflow(block):
            h = np.maximum(0.0, block.inlet[0].height())
            content = block.inlet[0].content
            resid = block.mass_flow_rate() - content.material.rho*block.area*c*(2*g*h)**0.5

            return resid

        self.mech_energy = Constraint(outflow)

class Stream(Block):
    """
    A fluid stream of chemical compounds.

    :param time_vec: An array defining time steps.
    :type client: Iterable

    :param x: time vector for given stream timeseries.
    :type bounds: Iterable, optional
    :param y: stream timeseries.
    :type bounds: Iterable.

    """
    def __init__(self, time_vec, *args):
        super().__init__()
        if len(args) == 1:
            flow_rate = [args[0] for i in time_vec]
        elif len(args) == 2:
            x = args[0]
            y = args[1]
            
            func = interpolate.interp1d(x, y, kind='previous')
            flow_rate = func(time_vec)


        self.mass_flow_rate = Constant(flow_rate)
        self.outport_flow = OutPort(self.mass_flow_rate)
        self.inlet = []
        self.outlet = []