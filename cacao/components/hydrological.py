from cacao.components import dimensions
from .abstracts import Component
import networkx as nx

class Storage(Component):

    def __init__(self, instructions):
        super().__init__(instructions)        
        volume = instructions['volume']

        inflow = dimensions.VolumeFlowRate(self.name + '__inflow')
        volume = dimensions.Volume(self.name + '__volume', volume)
        outflow = dimensions.VolumeFlowRate(self.name + '__outflow')
        self.graph.add_edges_from([
            (inflow, volume),
            (volume, outflow)
        ])

class Inflow(Component):
        
    def __init__(self, instructions):
        super().__init__(instructions) 

        inflow = dimensions.VolumeFlowRate(self.name + '__inflow')
        outflow = dimensions.VolumeFlowRate(self.name + '__outflow')
        self.graph.add_edges_from([
            (inflow, outflow),
        ])

class Terminal(Component):
    
    def __init__(self, instructions):
        super().__init__(instructions) 

        inflow = dimensions.VolumeFlowRate(self.name + '__inflow')
        
        self.graph.add_node(inflow)