class Constant:
    """
    A simple class to represent constants in an optimization problem.

    :param value: The value of the constant. May be a scalar or a vector
    :type client: list, array, float or int.
    """
    def __init__(self, value):
        self.value = value

    def __call__(self):
        return self.value

class Variable:
    """
    This class representa a decision variable in an optimization problem.

    :param index_var: An array that defines the length of the variable.
    :type client: Iterable

    :param bounds: Bounds of the variable. Use None for no bound. For example physical variables such as mass or temperature (K) may be
    only positive, so the bounds would be (0.0, None).
    :type bounds: tuple
    """
    def __init__(self, index_var=[0], bounds=(None, None)):
        self.value = [100] * len(index_var)
        # create array of Nones with 2 None for each variable
        #bnds = np.array([None for i in range(len(index_var)* 2)])
        bnds = [bounds for i in range(len(index_var))]

        # reshape to have 2 Nones on last dimension
        #bnds = bnds.reshape(len(index_var), 2)
        self.bounds = bnds

    def get_bounds(self):
        return self.bounds
    
    def  __setitem__(self, key, item):
        '''
        This method is used to set a bound on a index of the variable
        e.g height[0] = 0.0
        '''
        # specify a single value or (min, max) for as a constraint for an
        # indexed var
        if isinstance(item, float) or isinstance(item, int):
            self.bounds[key] = (item, item)
        elif isinstance(item, tuple):
            self.bounds[key] = item
        else:
            raise ValueError('Only tuple or numeric values are allowed as bounds.')


    def set_value(self, x):
        self.value = x

    def __call__(self):
        return self.value

class Constraint:
    """
    This class representa a constraint equation in an optimization problem, written in the residual format:
    f(x) = 0

    :param rule: A python function defining the constraint. The signature must be 
    .. highlight:: python
    .. code-block:: python

        def rule(block):
            f = ....
            return f
        ...
    
    :type rule: Callable

    :param lb: The lower bound of constraint. Normally for an equality constraint lower and upper bound are set to zero.
    :type lb: float or int, optional.
    :param ub: The upper bound of constraint. Normally for an equality constraint lower and upper bound are set to zero.
    :type ub: float or int, optional.
    """
    def __init__(self, rule, lb=0, ub=0):
        self.rule = rule
        self.ub = lb
        self.lb = ub
    
    def __call__(self, model):
        return self.rule(model)

class Block:
    """
    This class represents a conceptual block, a unit which has some meaning to hold certain variables and constraints within
    the optimization problem.
    """
    def __init__(self):
        self.variables = []
        self.constraints = []
        self.parent = None
        self.time = None

    def set_parent(self, parent):
        self.parent = parent
    
    def __setattr__(self, name, value):
        if isinstance(value, Variable):
            super().__setattr__(name, value)
            self.variables.append(value)
        elif isinstance(value, Constraint):
            self.add_cons( value, value.lb, value.ub)
        else:
            super().__setattr__(name, value)

    def update_time(self, time_vec):
        self.time = time_vec

    def change_inputs(self, x):
        self.parent.change_inputs(x)

    def add_cons(self, constraint, lb=0, ub=0):

        def cons(x):
            self.change_inputs(x)
            return constraint(self)

        self.constraints.append( {'type': 'eq', 'fun': cons} )


class Composite:
    """
    This class represents a higher-level block, able to "aggregate" multiple blocks. In Composite design pattern, the
    composite is a high-level block while the Block class is a leaf. 
    """
    def __init__(self):
        self.variables = []
        self.constraints = []
        self.blocks = []
        self.time = [0]
        self.parent=None

    def __setattr__(self, name, value):
        if isinstance(value, Block):
            block = value
            for variable in block.variables:
                self.variables.append(variable)
            for constraint in block.constraints:
                self.constraints.append(constraint)
            block.set_parent(self)
            block.update_time( self.time )
            self.blocks.append( block )
        super().__setattr__(name, value)

    def update_time(self, time_vec):
        self.time = time_vec
        for block in self.blocks:
            block.update_time( time_vec )

    def change_inputs(self, x):
        # if this is not a root block, then call recursively the parent until it reaches the root node
        if self.parent:
            self.parent.change_inputs(x)
        else: # this is the root node
            curr_index = 0
            for variable in self.variables:
                variable.set_value(x[curr_index:curr_index+len(variable.value)])
                curr_index += len(variable.value)
    
    def get_initial_guess(self):
        if self.parent:
            self.parent.get_initial_guess()
        else: # this is the root node
            xGuess = []
            for variable in self.variables:
                xGuess.extend(variable.value)

        return xGuess

    def get_bounds(self):
        # collect the bounds for all variables
        bnds = []
        for variable in self.variables:
            bnds.extend( variable.get_bounds() ) 

        return bnds
    
    def get_constraints(self):
        return self.constraints

    def connect(self, block1, block2):
        #inport.set_variable(outport.get_variable())
        block1.outlet.append(block2)
        block2.inlet.append(block1)
