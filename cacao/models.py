from scipy.integrate import odeint
from scipy import interpolate

import numpy as np

from typing import Dict

class ConcreteModel:

    def __init__(self, model_components, data_config, timeseries ):
        self.model_components = model_components
        self.data_config = data_config
        self.timeseries = timeseries
        self.time = 0.0
        self.dt = 0.1

    
    def initialize(self, config):
        
        self.time = config['start_time']
        self.dt = config['time_step']

        self.data_exchange = dict()
        for ts_name in self.data_config['import']:
            self.data_exchange[ts_name] = self.timeseries[ts_name]

        self.export = {'t': np.array([])}
        for ts_name in self.data_config['export']:
            self.export[ts_name] = np.array([])

        for model_component in self.model_components:
            model_component.initialize(config)

    def run_until(self, end_time):

        dt = self.dt
        start_time = self.time
        N = int( (end_time - start_time)/dt + 1 )
        for t in np.linspace(start_time, end_time, N):
            for model_component in self.model_components:
                self.data_exchange = model_component.update(t, self.data_exchange)
                for var_name in self.data_config['export']:
                    var_value = model_component.get_value(var_name)
                    self.export[var_name] = np.append(self.export[var_name], var_value )
            self.export['t'] = np.append(self.export['t'], t )
            self.time = t
            

    def get_outputs(self):
        return self.export

class ComponentBuilder:

    def __init__(self):
        pass
    
    @staticmethod
    def build(component, attributes):
        if component == 'reservoir':
            model_component = Component(
                                        id = attributes['id'],
                                        state_var_names = attributes['states'],
                                        input_var_names = attributes['inputs'],
                                        output_var_names = attributes['outputs'],
                                        model = Reservoir,
                                        model_args = {
                                            'storage_characteristics': attributes['storageCharacteristics']
                                        })

        return model_component

class Timeseries:

    def __init__(self, t_list, value_list):
        self.t = t_list
        self.values = value_list
    
    def __getitem__(self, t):
        return np.interp(t, self.t, self.values)

class Component:

    def __init__(self, id, state_var_names, input_var_names, output_var_names, model, model_args):

        self.id = id
        self.time = 0.0

        self.model = model(**model_args)

        self.state_var_names = state_var_names
        
        self.input_var_names = input_var_names
        
        self.output_var_names = output_var_names

        
    def initialize(self, config):
        self.time = config['start_time']
        self.reset_states(config['initial_states'])

    def reset_states(self, initial_states: Dict[str, float]):
        state_var_names = list(self.state_var_names.values())
        #print(state_var_names)
        for state_var_name in initial_states:
            #print(state_var_name)
            if state_var_name in state_var_names:
                pos = state_var_names.index(state_var_name)
                state = list(self.state_var_names.keys())[pos]
                initial_value = initial_states[state_var_name]
                setattr(self.model, state, initial_value)

    def get_value(self, var_name):
        for output_name, output_var_name in self.output_var_names.items():
            if output_var_name == var_name:
                return getattr(self.model, output_name)
            
    def update(self, t, data_exchange):
        # update_inputs
        self.update_inputs(t, data_exchange)
        # update_states
        self.update_states(t)
        # update outputs
        data_exchange = self.update_outputs(t, data_exchange)

        return data_exchange

    def update_inputs(self, t, inputs):
        for input_name, input_var_name in self.input_var_names.items():
            if input_var_name not in inputs:
                raise ValueError('Input + <' + input_var_name + 'was not provided as an input for ' + str(self))
            else:
                value = inputs[input_var_name][t]
                setattr(self.model, input_name, value)
            
    
    def update_states(self, t):
        x = []
        for state_name, state_var_name in self.state_var_names.items():
            x.append( getattr(self.model, state_name) )
        
        xnew = odeint(self.model.deriv, x, [self.time, t])[-1]
        
        i = 0
        for state_name, state_var_name in self.state_var_names.items():
            
            # CHECK IF STATES ARE BOUNDED
            if 'bounds__' + state_name in self.model.__dict__:
                state_lower_bound, state_upper_bound = getattr(self.model, 'bounds__' + state_name)
                if xnew[i] < state_lower_bound:
                    xnew[i] = state_lower_bound
                    print(Warning('At t = ' + str(t) + ' state <' + state_name + ' ' + state_var_name + '> was reset to bounds.'))
                elif xnew[i] > state_upper_bound:
                    xnew[i] = state_upper_bound
                    print(Warning('At t = ' + str(t) + ' state <' + state_name + ' ' + state_var_name + '> was reset to bounds.'))
                
            setattr(self.model, state_name, xnew[i])
        
        self.time = t
        

    def update_outputs(self, t, outputs):
        for output_name, output_var_name in self.output_var_names.items():
            if output_var_name not in outputs:
                outputs[output_var_name] = {t: getattr(self.model, output_name)}
            else:
                outputs[output_var_name][t] = getattr(self.model, output_name)

        return outputs


class Model:

    def __init__(self):
        pass
    
    def deriv(self, x, t):
        pass

class Reservoir(Model):

    def __init__(self, storage_characteristics):

        elevations = storage_characteristics['storageTable']['elevations']
        values = storage_characteristics['storageTable']['values']
        storage_table = interpolate.interp1d(elevations, values)

        self.storage_table = storage_table
        
        self.storage = 0.0
        self.bounds__storage = (0.0, 1000000.0)

        self.inflow = 0.0
        self.release = 0.0

    @property
    def pressure(self):
        m = 1000.0
        g = 9.81
        h = self.level
        P = m*g*h
        return P
    
    @property
    def cross_section(self):
        h = self.level
        V = self.storage
        Area = V/h
        return Area
    
    @property
    def level(self):
        try:
            h = self.storage_table( self.storage )
        except ValueError as error:
            print('Probable cause: Extrapolating a lookup table')
            print('Component ' + str(self))
            raise(error)
        return h
    
    def deriv(self, V, t):
        self.storage = V
        dV = (self.inflow - self.release)

        return dV