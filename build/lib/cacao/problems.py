from scipy.optimize import minimize

import numpy as np

class SimulationProblem:
    """
    Create a simulation problem, i.e a problem with no degrees of freedom (number of variables = number of constraints)

    :param model: The cacao model to be simulated
    :type model: cacao.generics.Composite
    """
    def __init__(self, model):
        self.model = model
    
    def run(self, verbose = False):
        """
        Perform a simulation of the cacao model along the time steps defined in the model (model.time)

        :param verbose: Set to True to see extended output. Defaults to False.
        :type verbose: bool, optional

        :return: Simulation results (attribute x contains the actual solution value of the variables).
        :rtype: scipy.optimize.OptimizeResult
        """
        obj = lambda x: 0.0
        xGuess = self.model.get_initial_guess()
        bnds = self.model.get_bounds()
        cons = self.model.get_constraints()
        res = minimize(obj, xGuess, method='trust-constr',bounds=bnds, constraints=cons)
        if verbose:
            print(res)
        return res