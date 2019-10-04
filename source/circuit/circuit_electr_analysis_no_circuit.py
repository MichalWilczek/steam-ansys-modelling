
from source.circuit.circuit import Circuit

class CircuitElectricAnalysisNoCircuit(Circuit):

    def __init__(self, ansys_commands, class_geometry, input_data):
        Circuit.__init__(self, ansys_commands, class_geometry, input_data)

    def set_circuit_bcs_in_analysis(self):
        self.couple_nodes_in_analysis()
        self.set_initial_current()
        self.set_ground()

    def set_initial_current(self):
        self.ansys_commands.select_nodes_for_current(class_geometry=self.geometry)
        self.ansys_commands.set_current(node_number="all", value=self.factory.current_init)

    def set_ground(self):
        self.ansys_commands.set_ground_in_analysis(class_geometry=self.geometry)

