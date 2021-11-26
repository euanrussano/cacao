import numpy as np
from scipy.integrate import odeint

class Operation:
    """Represents a graph node that performs a computation.

    An `Operation` is a node in a `Graph` that takes zero or
    more objects as input, and produces zero or more objects
    as output.
    """

    def __init__(self, name='', input_nodes=[]):
        """Construct Operation
        """
        self.name = name
        self.input_nodes = input_nodes
        self.output = []

        # Initialize list of consumers (i.e. nodes that receive this operation's output as input)
        self.consumers = []

        # Append this operation to the list of consumers of all input nodes
        for input_node in input_nodes:
            input_node.consumers.append(self)

        # Append this operation to the list of operations in the currently active default graph
        Graph().operations.append(self)

    def compute(self):
        """Computes the output of this operation.
        "" Must be implemented by the particular operation.
        """
        pass

    def __repr__(self):
        return str(type(self)) + self.name

class add(Operation):
    """Returns x + y element-wise.
    """

    def __init__(self, name, x, y):
        super().__init__(name,[x, y])

    def compute(self, x_value, y_value):
        
        return x_value + y_value

# class integrator(Operation):
#     """Returns x + y element-wise.
#     """

#     def __init__(self, dx, initial_state):
#         super().__init__([dx])
#         self.state = initial_state
#         self.time = 0.0

#     def compute(self, dx_value, time, *args, **kwargs):
#         t_final = time
#         xnew = self.state + (t_final - self.time)*dx_value
#         self.state = xnew
#         self.time = t_final
#         return xnew

class divide(Operation):
    """Returns x / y element-wise.
    """

    def __init__(self, name, x, y):
        super().__init__(name,[x, y])

    def compute(self, x_value, y_value):
    
        return x_value / y_value

class multiply(Operation):
    """Returns x * y element-wise.
    """

    def __init__(self, name, x, y):
        super().__init__(name,[x, y])

    def compute(self, x_value, y_value):
    
        return x_value * y_value


class subtract(Operation):
    """Returns x - y element-wise.
    """

    def __init__(self, name, x, y):
        super().__init__(name, [x, y])

    def compute(self, x_value, y_value):
    
        return x_value - y_value

class sqrt(Operation):
    """Returns sqrt(x) element-wise.
    """

    def __init__(self, name, x):
        super().__init__(name, [x])

    def compute(self, x_value):
    
        return np.sqrt(x_value)

class matmul(Operation):
    """Multiplies matrix a by matrix b, producing a * b.
    """

    def __init__(self, name, a, b):
        super().__init__(name, [a, b])

    def compute(self, a_value, b_value):
       
        return a_value.dot(b_value)

class inputPort(Operation):
    """Multiplies matrix a by matrix b, producing a * b.
    """

    def __init__(self, name):
        super().__init__(name,[])
    
    def connect(self, input_node):
        self.input_nodes.append(input_node)

        # Append this operation to the list of consumers of all input nodes
        input_node.consumers.append(self)

    def compute(self, a_value):
       
        return a_value

class placeholder:
    """Represents a placeholder node that has to be provided with a value
       when computing the output of a computational graph
    """

    def __init__(self, name):
        """Construct placeholder
        """
        self.name = name
        self.consumers = []
        self.output = []

        # Append this placeholder to the list of placeholders in the currently active default graph
        Graph().placeholders.append(self)

    def __repr__(self):
        return 'Placeholder ' + self.name

class parameter:
    """Represents a parameter (i.e. an intrinsic, changeable parameter of a computational graph).
    """

    def __init__(self, name, initial_value=None):
        self.name = name
        self.value = initial_value
        self.consumers = []
        self.output = []

        # Append this variable to the list of variables in the currently active default graph
        Graph().parameters.append(self)

    def __repr__(self) -> str:
        return 'Parameter ' + self.name

class output(Operation):
    """Represents an output i.e terminal node of a computation graph.
    """

    def __init__(self, name, prev_node):
        super().__init__(name, [prev_node])
        self.output = []

        Graph().outputs.append(self)

    def compute(self, a_value):
       
        return a_value

class state:
    """Represents a state (i.e. a value that changes with time in a computational graph).
    """

    def __init__(self, name, deriv, initial_value=[0.0]):
        self.name = name
        self.deriv = deriv   
        self.output = initial_value
        self.consumers = []

        Graph().states.append(self)    

    def __repr__(self) -> str:
        return 'State ' + self.name


# singleton - https://riptutorial.com/python/example/10954/create-singleton-class-with-a-decorator
def singleton(cls):    
    instance = [None]
    def wrapper(*args, **kwargs):
        if instance[0] is None:
            instance[0] = cls(*args, **kwargs)
        return instance[0]

    return wrapper

@singleton
class Graph:
    """Represents a computational graph
    """

    def __init__(self):
        """Construct Graph"""
        self.operations = []
        self.placeholders = []
        self.parameters = []
        self.states = []
        self.outputs = []

import numpy as np


class Environment:
    """Represents a particular execution of a computational graph.
    """
    def compile(self):
        self.trees = []
        # traverse the graph for each state
        for state in Graph().states:
            # Perform a post-order traversal of the graph to bring the nodes into the right order
            nodes_postorder = traverse_postorder(state.deriv)
            self.trees.append(nodes_postorder)
        # traverse the graph for each output
        for output in Graph().outputs:
            # Perform a post-order traversal of the graph to bring the nodes into the right order
            nodes_postorder = traverse_postorder(output)
            self.trees.append(nodes_postorder)

    def run(self, feed_dict={}):
        """Computes the output of an operation

        Args:
          feed_dict: A dictionary that maps placeholders to values for this session
        """

        # clean all the outputs from Operation nodes before running
        self.clean_operations()

        # Iterate all nodes to determine their value
        for nodes_postorder in self.trees:
            for node in nodes_postorder:
                # only updates nodes that have no output
                if len(node.output) == 0:
                    if type(node) == placeholder:
                        # Set the node value to the placeholder value from feed_dict
                        node.output = feed_dict[node]
                    elif type(node) == parameter:
                        # Set the node value to the variable's value attribute
                        node.output = node.value
                    elif isinstance(node, Operation):
                        # Get the input values for this operation from the output values of the input nodes
                        node.inputs = [input_node.output for input_node in node.input_nodes]
                        # Compute the output of this operation
                        #print(node) 
                        #print(node.inputs)
                        node.output = node.compute(*node.inputs)
                        #print(node.output)
                    # Convert lists to numpy arrays
                    if type(node.output) == list:
                        node.output = np.array(node.output)

    def clean_operations(self):
        for nodes_postorder in self.trees:
            for node in nodes_postorder:
                if isinstance(node, Operation):
                    node.output = []

def traverse_postorder(operation):
    """Performs a post-order traversal, returning a list of nodes
    in the order in which they have to be computed

    Args:
       operation: The operation to start traversal at
    """

    nodes_postorder = []

    def recurse(node):
        if isinstance(node, Operation):
            for input_node in node.input_nodes:
                recurse(input_node)
        nodes_postorder.append(node)

    recurse(operation)
    return nodes_postorder

