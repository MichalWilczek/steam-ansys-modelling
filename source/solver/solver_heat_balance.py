
from source.solver.solver import Solver
from source.processor_post.plots import Plots

class SolverHeatBalance(Solver, Plots):

    def __init__(self, ansys_commands, class_geometry, input_data, circuit, ic_temperature_class, mat_props, mag_map):
        Solver.__init__(self, ansys_commands, class_geometry, input_data,
                        circuit, ic_temperature_class, mat_props, mag_map)
        Plots.__init__(self)

    def set_solver_bcs(self):
        self.ansys_commands.input_heat_generation_table(class_mat=self.material_properties,
                                                        magnetic_field=self.magnetic_map.im_short_mag_dict["winding1"])
        self.ansys_commands.set_heat_generation_in_nodes(node_number="all", value="%heatgen%")
