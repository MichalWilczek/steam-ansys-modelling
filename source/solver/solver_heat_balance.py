
from source.solver.solver import Solver

class SolverHeatBalance(Solver):

    def __init__(self, factory, ansys_commands, class_geometry, circuit, ic_temperature_class, mat_props, mag_map):
        Solver.__init__(self, factory, ansys_commands, class_geometry,
                        circuit, ic_temperature_class, mat_props, mag_map)

    def set_solver_boundary_conditions(self):
        self.ansys_commands.input_heat_generation_table(class_mat=self.mat_props,
                                                        magnetic_field=self.magnetic_map.im_short_mag_dict["winding1"])
        winding_node_list = self.geometry.winding_node_dict["winding1"]
        winding_nodes_ansys = self.geometry.prepare_ansys_nodes_selection_list(winding_node_list)
        self.ansys_commands.select_nodes_list(winding_nodes_ansys)
        self.ansys_commands.set_heat_generation_in_nodes(node_number="all", value="%heatgen%")

