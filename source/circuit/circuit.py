
class Circuit(object):

    def __init__(self, ansys_commands, class_geometry, factory):
        self.ansys_commands = ansys_commands
        self.geometry = class_geometry
        self.input_data = factory.input_data

    def set_circuit_bcs_in_analysis(self):
        pass

    def couple_nodes_in_analysis(self):
        nodes_to_couple_windings_list = self.geometry.create_node_list_to_couple_windings()
        for nodes_list in nodes_to_couple_windings_list:
            nodes_to_select_ansys = self.geometry.prepare_ansys_nodes_selection_list(real_nodes_list=nodes_list)
            self.ansys_commands.select_nodes_list(nodes_list=nodes_to_select_ansys)
            self.ansys_commands.couple_nodes(dof="temp")
            self.ansys_commands.couple_nodes(dof="volt")

    def return_current_in_time_step(self):
        return self.input_data.circuit_settings.electric_ansys_element_input.current_init










