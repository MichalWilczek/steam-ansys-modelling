
from source.circuit.circuit import Circuit

class CircuitNoTransient(Circuit):

    def __init__(self, ansys_commands, class_geometry, factory):
        Circuit.__init__(self, ansys_commands, class_geometry, factory)

    def build_circuit(self):
        pass

    def set_initial_current(self):
        self.ansys_commands.select_nodes_for_current(class_geometry=self.geometry)
        self.ansys_commands.set_current(
            node_number="all", value=self.input_data.circuit_settings.electric_ansys_element_input.current_init)




