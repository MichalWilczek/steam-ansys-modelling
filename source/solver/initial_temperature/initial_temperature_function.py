
from source.solver.initial_temperature.initial_temperature import InitialTemperature
from source.solver.initial_temperature.polynomial_fit import PolynomialFit
from source.post_processor.quench_velocity.nodes_search import SearchNodes

class InitialTemperatureFunction(InitialTemperature, PolynomialFit, SearchNodes):

    def __init__(self, ansys_commands, class_geometry, mat_props, factory):
        InitialTemperature.__init__(self, ansys_commands, class_geometry, mat_props, factory)
        PolynomialFit.__init__(self, factory, self.input_data.temperature_settings.input.temperature_function_filename)
        self.initial_node_quench = SearchNodes.search_init_node(position=self.input_data.quench_init_position,
                                                                coil_length=self.geometry.coil_geometry)
        # TIME STEP VECTOR IS NOT YET DEFINED IN THE ANALYSIS !!!
        temperature_bc_list = PolynomialFit.create_linear_interpolation_array(self.time_step_vector)


    def set_temperature_in_time_step(self, iteration):
        self.ansys_commands.select_nodes_in_analysis(self.geometry, x_down_node=self.initial_node_quench,
                                                     x_up_node=self.initial_node_quench)
        self.ansys_commands.set_load_in_solver(dof='temp', value=temperature_bc_list[iteration])

