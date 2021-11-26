from .hydrological import Storage, Inflow, Terminal
from .dimensions import Volume, VolumeFlowRate


class ComponentFactory:
    
    @staticmethod
    def create(instructions: dict):
        component_obj = instructions['component']

        if component_obj == 'Storage':
            component = Storage(instructions)

        elif component_obj == 'Inflow':
            component = Inflow(instructions)

        elif component_obj == 'Terminal':
            component = Terminal(instructions)
            
        elif component_obj == 'VolumeFlowRate':
            component = VolumeFlowRate(instructions)

        return component
