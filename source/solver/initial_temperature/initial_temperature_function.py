
from source.solver.initial_temperature.initial_temperature import InitialTemperature
from source.solver.initial_temperature.polynomial_fit import PolynomialFit
from source.processor_post.quench_velocity.nodes_search import SearchNodes

class InitialTemperatureFunction(InitialTemperature, PolynomialFit, SearchNodes):

    def __init__(self, ansys_commands, class_geometry, input_data, mat_props):
        InitialTemperature.__init__(self, ansys_commands, class_geometry, input_data, mat_props)
        self.initial_node_quench = SearchNodes.search_init_node(position=self.factory.quench_init_position,
                                                                coil_length=self.geometry.coil_geometry)

    def set_temperature_in_time_step(self, iteration, time_step_vector):
        temperature_bc_list = PolynomialFit.create_linear_interpolation_for_temp_vector(time_step_vector)
        self.ansys_commands.select_nodes_in_analysis(self.geometry, x_down_node=self.initial_node_quench,
                                                     x_up_node=self.initial_node_quench)
        self.ansys_commands.set_load_in_solver(dof='temp', value=temperature_bc_list[iteration])

