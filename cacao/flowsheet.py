import numpy as np
from scipy.optimize import fsolve

from .collocation import tc, colloc
class Flowsheet:
    """
    Instantiate a dynamical process consisting of multiple dynamical processes.
    Perform numerical simulation of the system using Orthogonal Collocation (FEM).
    
    :param blocks: A list containing Block elements.
    :type blocks: List[cacao.generics.Block]
    """

    def __init__(self, blocks):
        
        
        # set state_idx and output_idx for each block and for flowsheet(global)
        global_state_idx = []
        global_output_idx = []
        
        state_idx=[]
        output_idx=[]
        
        out_idx = 0
        x_idx = 0
        for block in blocks:
            for output_name in block.outputs_name:
                output_idx.append( (output_name, out_idx) )
                global_output_idx.append( (output_name, out_idx) )
                out_idx += 1
            for state_name in block.states_name:
                state_idx.append( (state_name, x_idx) )
                global_state_idx.append( (state_name, x_idx) )
                x_idx += 1
            block.state_idx = state_idx
            block.output_idx = output_idx
            state_idx=[]
            output_idx=[]
            
        # collect initial conditions
        IC = []
        for block in blocks:
            for state_name in block.states_name:
                IC.append( getattr(block, state_name) )
        
        self.blocks = blocks
        self.IC = IC
        self.num_states = sum([len(block.states_name) for block in self.blocks])
        self.num_outputs = sum([len(block.outputs_name) for block in self.blocks])
        self.state_idx = global_state_idx
        self.output_idx = global_output_idx
    
    def initialize(self, n_nodes=5, dt=1.0, time=0.0):
        """
        Set time related values (initial time, time step, etc) and number collocation of collocation nodes.
        Then calculates consistent initial outputs given the initial condition of each block state.
        Returns the initial time(t), states(x) and outputs(y).
        
        :param n_nodes: Number of collocation nodes (max. 6). Defaults to 5.
        :type n_nodes: int, optional
        :param dt: timestep between collocations. Defaults to 1.0.
        :type dt: float, optional
        :param time: initial simulation time. Defaults to 0.0.
        :type dt: float, optional
    
        :returns: 
            - time - initial simulation time
            - states - a dictionary with key as state names and value of state (float)
            - outputs - a dictionary with key as output names and value of output (float)
        """
        self.n_nodes = n_nodes
        self.dt = dt
        self.k = 0
        self.time = time
        self.reset_states()
        
        states, outputs = self.find_initial_outputs()
        
        
        states, outputs = self.to_dict(states, outputs)
        
        return self.time, states, outputs
    
    def to_dict(self, states, outputs):
        '''
        Transform states and outputs 2d array into dict.
        '''
        
        states_dict = {key: states.flatten()[idx] for key, idx in self.state_idx}
        outputs_dict = {key: outputs.flatten()[idx] for key, idx in self.output_idx}
        
        return states_dict, outputs_dict
    
    def reset_states(self):
        '''
        reset states to IC
        '''
        self.states = self.IC.copy()
    
    def find_initial_outputs(self):
        '''
        Calculate consistent outputs given fixed states from blocks.
    
        :returns: 
            - states - 2D array of state values
            - outputs - 2D array of output values
        '''
        
        states = np.array([self.IC])
        dstates = np.zeros_like(states)
        outputsGuess = np.ones((1, self.num_outputs))

        def model0(y):
            y = y.reshape(1,-1)
            resid = self.step(dstates, states, y, 0.0)
            resid = resid[:, -self.num_outputs:].reshape(-1)
            return resid

        outputs = fsolve(model0, outputsGuess)
        outputs = outputs.reshape(1,-1)
        return states, outputs
        
    def connect(self, block1, block2):
        '''
        Connect outlet of block1 with inlet of block 2.
        
        :param block1: A block upstream
        :type block1: cacao.generics.Block
        :param block2: A block downstream
        :type block2: cacao.generics.Block
        '''
        block1.outlet.append(block2)
        block2.inlet.append(block1)
        
    def step(self, xdot, x, y, t):
        '''
        Iterate once over blocks and calculate all residuals for orthogonal collocation.
        
        :param xdot: Derivative of states 
        :type xdot: 2D numpy.array with shape(n_nodes, n_states)
        :param x: states
        :type x: 2D array with shape(n_nodes, n_states)
        :param y: outputs
        :type y: 2D array with shape(n_nodes, n_outputs)
        :param t: the current time of simulation
        :type t: float
        '''
    
        for block in self.blocks:
            block.set_values(xdot, x, y, t)
        
        for block in self.blocks:
            block.change_inputs()
        
        resids = []
        for block in self.blocks:
            resids.append( block.resid() )
        
        resid = np.concatenate(resids,1)
        
        return resid
    
    def collocation_residuals(self, z):
        '''
        Function actually used to perform orthogonal collocation. It receives 1D array of all derivatives, states amd outputs,
        and returns all residuals.
        
        :param z: value of xdot, x, y
        :type z: 1D numpy.array with shape(n_states*2 + n_outputs)
        '''
        n = self.n_nodes
        
        num_states = self.num_states # number of states
        num_outputs = self.num_outputs # number of outputs
        IC = self.states # initial conditions on current step ([x1_0, x2_0, x3_0, ...])

        NC = colloc(n)
        t = tc(n)*self.dt + self.k*self.dt

        # rename z as x and xdot variables
        x = np.empty((n-1) * num_states)
        xdot = np.empty((n-1) * num_states)
        y = np.empty((n-1) * num_outputs)

        z = z.reshape(n-1, 2*num_states + num_outputs)
        x = z[:,:num_states]
        xdot = z[:,num_states:2*num_states]
        y = z[:,2*num_states:]

        x0 = np.ones_like(x)*IC

        # function evaluation residuals
        F1 = np.empty((n-1, num_states + num_outputs))
        F2 = np.empty((n-1, num_states))

        # nonlinear differential equations at each node
        F1 = self.step(xdot, x, y, t[1:])

        # collocation equations
        F2 = self.dt*np.dot(NC,xdot) - x + x0

        F1 = F1.reshape(-1)
        F2 = F2.reshape(-1)

        F = np.concatenate((F1, F2))

        return F
    
    def update(self):
        '''
        Move simulation forward one time step (dt).
        '''
        
        zGuess = np.ones((self.n_nodes-1)*self.num_states*2 + (self.n_nodes-1)*self.num_outputs)
        z = fsolve(self.collocation_residuals,zGuess)
        
        # update IC
        z = z.reshape(self.n_nodes-1, 2*self.num_states + self.num_outputs)
        x = z[:,:self.num_states]
        xdot = z[:,self.num_states:2*self.num_states]
        y = z[:,2*self.num_states:]
        
        IC = x[-1,:]
        self.states = IC
        # store results

        states = x[-1,:].reshape(1,-1)
        outputs = y[-1,:].reshape(1,-1)
        
        
        states, outputs = self.to_dict(states, outputs)
        
        # advance one time shift
        self.k += 1
        self.time = self.dt*self.k
        
        return self.time, states, outputs
        
    def update_until(self, tf=1.0):
        '''
        Move simulation forward multiple time steps, until it reaches tf.

        :param tf: final simulation time. Defaults to 1.0
        :type tf: float, optional.
        '''
        states, outputs = self.find_initial_outputs()      
        x, y = self.to_dict(states, outputs)

        timesteps = np.array([self.time])
        states = {key: [value] for key, value in x.items()}
        outputs = {key: [value] for key, value in y.items()}
        
        N = int((tf - self.time)/self.dt)
        for i in range(N):
            t, x, y = self.update()
            timesteps = np.append(timesteps, t)
            for state_name in x:
                states[state_name].append(x[state_name])
            for output_name in y:
                outputs[output_name].append(y[output_name])
                
        return timesteps, states, outputs