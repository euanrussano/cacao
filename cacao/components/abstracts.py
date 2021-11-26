import networkx as nx

class Component:

    def __init__(self, instructions):
        name = instructions['name']
        
        self.graph = nx.Graph()

class Node:

    def __init__(self, name):
        self.name = name

    def set_initial_states(self, initial_states: dict):
        for state in self.states:
            state.set_value(initial_states[state.name])