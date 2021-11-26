from cacao.components.abstracts import Node

class Volume(Node):

    def __init__(self, name, initial_volume):
        super().__init__(name)
        self.value = initial_volume

    def set_value(self, value):
        self.value = value


class VolumeFlowRate(Node):
    pass