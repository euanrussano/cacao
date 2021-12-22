import numpy as np
from .generics import Block
  
        
class FlowRelease(Block):
    
    def __init__(self, Cv, flowrate="Q1", state_idx=[], output_idx=[]):
        super().__init__(state_idx, output_idx)
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
    
    def __init__(self, qout, flowrate='Q1', state_idx=[], output_idx=[]):
        super().__init__(state_idx, output_idx)
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
    
    def __init__(self, q_in, flowrate="Qin", state_idx=[], output_idx=[]):
        super().__init__(state_idx, output_idx)
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
    
    def __init__(self, Area, IC=0.0, volume='V1', height='h1', state_idx=[], output_idx=[]):
        super().__init__(state_idx, output_idx)
        self.Area = Area
        
        self.volume = volume
        self.height = height
        setattr(self, self.volume, IC)
        setattr(self, 'der_' + self.volume, 0.0)
        setattr(self, self.height, 0.0)
        #self.V = IC
        #self.der_V = 0.0
        #self.h = 0.0
        
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