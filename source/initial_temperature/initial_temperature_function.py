
from source.initial_temperature.initial_temperature import InitialTemperature
from source.initial_temperature.polynomial_fit import Polynomials
from source.quench_velocity.nodes_search import SearchNodes

class InitialTemperatureFunction(InitialTemperature, Polynomials, SearchNodes):

    def __init__(self, ansys_commands, class_geometry, input_data):
        super.__init__(ansys_commands, class_geometry, input_data)
        self.initial_node_quench = SearchNodes.search_init_node(position=self.factory.quench_init_position,
                                                                coil_length=self.geometry.coil_geometry)

    def set_temperature_in_time_step(self, iteration, time_step_vector):
        temperature_bc_list = Polynomials.create_linear_interpolation_for_temp_vector(time_step_vector)
        self.ansys_commands.select_nodes_in_analysis(self.geometry, x_down_node=self.initial_node_quench,
                                                     x_up_node=self.initial_node_quench)
        self.ansys_commands.set_load_in_solver(dof='temp', value=temperature_bc_list[iteration])

