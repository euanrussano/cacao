import networkx as nx

class Process:

    def __init__(self):
        self.graph = nx.Graph()

    def add_component( self, component ):
        self.graph = nx.union(self.graph, component)

    def add_input( self, input_instruction ):
        input_name = input_instruction['name']
        for node in self.graph:
            if node.name == input_name:
                


    def add_output( self, component ):
        pass

    def add_connect( self, source, target ):
        pass