import numpy as np

class Block:
    """
    An interface for dynamic elements that can be simulated.

    :param state_idx: tuples of (state_name, idx) e.g state_idx = [('Q',0),('T',1)]
    :type state_idx: list of tuples
    :param output_idx: tuples of (output_name, idx) e.g output_idx = [('Q',0),('T',1)]
    :type output_idx: list of tuples
    """
    def __init__(self, state_idx=[], output_idx=[]):
        '''
        state_idx = [('Q',0),('T',1)]
        '''
        self.state_idx = state_idx
        self.output_idx = output_idx
        
        self.inlet = []
        self.outlet = []
    
    def change_inputs(self):
        pass
    
    def get_resid(self):
        n_rows = self.n_nodes
        n_cols = len(self.state_idx) + len(self.output_idx)
        resid = np.zeros((n_rows, n_cols))
        return resid
        
    def set_values(self, xdot, x, y, t):
        self.n_nodes = y.shape[0]
        self.t = t
        for state_name, state_idx in self.state_idx:
            setattr(self, 'der_' + state_name, xdot[:,state_idx])
            setattr(self, state_name, x[:,state_idx])
        for output_name, output_idx in self.output_idx:
            setattr(self, output_name, y[:,output_idx])      