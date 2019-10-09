
from source.solver.solver import Solver
from source.post_processor.plots import Plots

class SolverHeatBalance(Solver, Plots):

    def __init__(self, factory, ansys_commands, class_geometry, circuit, ic_temperature_class, mat_props, mag_map):
        Solver.__init__(self, factory, ansys_commands, class_geometry,
                        circuit, ic_temperature_class, mat_props, mag_map)

    def set_solver_bcs(self):
        self.ansys_commands.input_heat_generation_table(class_mat=self.mat_props,
                                                        magnetic_field=self.magnetic_map.im_short_mag_dict["winding1"])
        self.ansys_commands.set_heat_generation_in_nodes(node_number="all", value="%heatgen%")

