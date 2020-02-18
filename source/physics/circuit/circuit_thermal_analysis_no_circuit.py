
from source.physics.circuit.circuit import Circuit

class CircuitThermalAnalysisNoCircuit(Circuit):

    def __init__(self, ansys_commands, class_geometry, factory):
        Circuit.__init__(self, ansys_commands, class_geometry, factory)

    def set_circuit_bcs_in_analysis(self):
        self.couple_nodes_in_analysis()

    def couple_nodes_in_analysis(self):
        nodes_to_couple_windings_list = self.geometry.create_node_list_to_couple_windings()
        for nodes_list in nodes_to_couple_windings_list:
            nodes_to_select_ansys = self.geometry.prepare_ansys_nodes_selection_list(real_nodes_list=nodes_list)
            self.ansys_commands.select_nodes_list(nodes_list=nodes_to_select_ansys)
            self.ansys_commands.couple_nodes(dof="temp")
