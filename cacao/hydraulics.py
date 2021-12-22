import numpy as np
from .generics import Block
  
        
class FlowRelease(Block):
    """
    Hydraulic orifice with constant cross-sectional area. To avoid some numerical issues, the 
    upstream height (h) is clipped to (0, +inf).

    .. math::

        Q(t) = Cv\sqrt{h(t)}
    
    :param Cv: Flow discharge coefficient
    :type Cv: float
    :param flowrate: The name of the flowrate variable. Must be unique along blocks in the same cacao.flowsheet.Flowsheet.
    :type flowrate: str
    """
    
    def __init__(self, Cv, flowrate="Q1"):
        super().__init__()
        self.Cv = Cv
        
        self.flowrate = flowrate
        setattr(self, self.flowrate, 0.0)
        
        self.h = 0.0
        
        self.states_name = []
        self.outputs_name = [self.flowrate]
        
    def change_inputs(self):
        self.h = getattr(self.inlet[0], self.inlet[0].height)
        
    def resid(self):
        Q = getattr(self, self.flowrate)
        h = np.clip(self.h, 0.0, None)
        resid = self.get_resid()
        resid[:,0] = Q - self.Cv*np.sqrt(h)
    
        return resid
    
class FlowConstant(Block):
    """
    Constant flowrate, as provided by pump.

    .. math::

        Q(t) = Constant
    
    :param qout: A constant flowrate value.
    :type qout: float
    :param flowrate: The name of the flowrate variable. Must be unique along blocks in the same cacao.flowsheet.Flowsheet.
    :type flowrate: str
    """
    
    def __init__(self, qout, flowrate='Q1'):
        super().__init__()
        self.value = qout
        
        self.flowrate = flowrate
        setattr(self, self.flowrate, 0.0)
        
        self.states_name = []
        self.outputs_name = [self.flowrate]
        
    def change_inputs(self):
        pass
        
    def resid(self):
        Q = getattr(self, self.flowrate)
        resid = self.get_resid()
        resid[:,0] = Q - self.value
    
        return resid
    
class FlowSource(Block):
    """
    A continuous source of fluid defined by a function qout(t)

    .. math::

        Q(t) = qout(t)
    
    :param qout: A function qout(t) providing the values of flowrate (should be continuous). e.g qout = lambda t: 0.4
    :type qout: Callable[float][float]
    :param flowrate: The name of the flowrate variable. Must be unique along blocks in the same cacao.flowsheet.Flowsheet.
    :type flowrate: str
    """
    
    def __init__(self, q_in, flowrate="Qin"):
        super().__init__()
        self.rule = q_in
        
        self.flowrate = flowrate
        setattr(self, self.flowrate, 0.0)
        
        self.states_name = []
        self.outputs_name = [self.flowrate]
        
    def resid(self):
        Q = getattr(self, self.flowrate)
        t = self.t
        resid = self.get_resid()
        resid[:,0] = Q - self.rule(t)
    
        return resid
    
class Reservoir(Block):
    """
    A container that can hold a volume V of fluid.

    .. math::

        dV/dt = Qin(t) - Qout(t)

        h(t) = \frac{V(t)}{Area}
    
    :param Area: Constant cross section area.
    :type Area: float
    :param IC: Initial Volume in the container. Defaults to 0.0.
    :type IC: float, optional
    :param volume: The name of the volume variable. Must be unique along blocks in the same cacao.flowsheet.Flowsheet.
    :type IC: str
    :param height: The name of the height variable. Must be unique along blocks in the same cacao.flowsheet.Flowsheet.
    :type IC: str
    """
    
    def __init__(self, Area, IC=0.0, volume='V1', height='h1'):
        super().__init__()
        self.Area = Area
        
        self.volume = volume
        self.height = height
        setattr(self, self.volume, IC)
        setattr(self, 'der_' + self.volume, 0.0)
        setattr(self, self.height, 0.0)
        
        self.Qin = 0.0
        self.Qout = 0.0
        
        self.states_name = [self.volume]
        self.outputs_name = [self.height]
    
    def change_inputs(self):
        n_rows = self.n_nodes
        
        self.Qin = np.zeros((n_rows))
        for elem in self.inlet:
            if hasattr(elem, 'flowrate'):
                Q = getattr(elem, elem.flowrate)
                self.Qin += Q
        
        self.Qout = np.zeros((n_rows))
        for elem in self.outlet:
            if hasattr(elem, 'flowrate'):
                Q = getattr(elem, elem.flowrate)
                self.Qout += Q
                
    def resid(self):
        Qin = self.Qin
        Qout = self.Qout
        
        V = getattr(self, self.volume)
        dV = getattr(self, 'der_' + self.volume)
        h = getattr(self, self.height)
        
        resid = self.get_resid()
        resid[:,0] = dV - (Qin - Qout)
        resid[:,1] = h - V/self.Area
    
        return resid