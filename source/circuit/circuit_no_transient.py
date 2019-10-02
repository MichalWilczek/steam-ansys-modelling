
from source.circuit.circuit import Circuit

class CircuitNoTransient(Circuit):

    def __init__(self, ansys_commands, class_geometry, input_data):
        super.__init__(ansys_commands, class_geometry, input_data)

    def build_circuit(self):
        pass

    def set_initial_current(self):
        self.ansys_commands.select_nodes_for_current(class_geometry=self.geometry)
        self.ansys_commands.set_current(node_number="all", value=self.factory.current_init)

    def set_ground(self):
        self.ansys_commands.set_ground_in_analysis(class_geometry=self.geometry)


