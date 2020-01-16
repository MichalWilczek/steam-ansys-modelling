
from source.physics.initial_temperature.initial_temperature import InitialTemperature
from source.physics.quench_velocity.nodes_search import SearchNodes
from source.common_functions.general_functions import GeneralFunctions
import numpy as np

class InitialTemperatureUniform(InitialTemperature):

    def __init__(self, ansys_commands, class_geometry, mat_props, factory):
        InitialTemperature.__init__(self, ansys_commands, class_geometry, mat_props, factory)
        self.initial_temperature_profile = None

    def create_ic_temperature_profile(self):
        self.initial_temperature_profile = np.zeros((len(self.geometry.coil_geometry[:, 0]), 2))
        self.initial_temperature_profile[:, 0] = self.geometry.coil_geometry[:, 0]
        self.initial_temperature_profile[:, 1] = self.input_data.temperature_settings.input.temperature_init

        geometry_dimensions = InitialTemperatureUniform.find_start_and_end_length_of_coil(self.geometry.coil_geometry)
        ic_zone_dimensions = InitialTemperatureUniform.set_length_of_initial_ic_temperature_zone(
            zone_centre=self.input_data.analysis_settings.quench_init_position,
            zone_length=self.input_data.analysis_settings.quench_init_length,
            geometry_dimensions=geometry_dimensions)
        ic_zone_node_min = SearchNodes.search_init_node(position=ic_zone_dimensions[0],
                                                        coil_length=self.geometry.coil_geometry)
        ic_zone_node_max = SearchNodes.search_init_node(position=ic_zone_dimensions[1],
                                                        coil_length=self.geometry.coil_geometry)
        self.initial_temperature_profile[(ic_zone_node_min-1):ic_zone_node_max, 1] = \
            self.input_data.temperature_settings.input.temperature_max_init_quenched_zone
        self.plots.plot_and_save_temperature(
            self.output_directory, self.geometry.coil_geometry,
            self.initial_temperature_profile, iteration=0, time_step=0.0)
        GeneralFunctions.save_array(self.plots.output_directory_temperature,
                        "Initial_temperature_profile.txt", self.initial_temperature_profile)
        return self.initial_temperature_profile

    @staticmethod
    def find_start_and_end_length_of_coil(coil_geometry):
        min_coil_length = coil_geometry[0, 1]
        max_coil_length = coil_geometry[len(coil_geometry) - 1, 1]
        return [min_coil_length, max_coil_length]

    @staticmethod
    def set_length_of_initial_ic_temperature_zone(zone_centre, zone_length, geometry_dimensions):
        zone_min = zone_centre - zone_length/2.0
        zone_max = zone_centre + zone_length/2.0
        if zone_min < geometry_dimensions[0]:
            zone_min = geometry_dimensions[0]
        if zone_max > geometry_dimensions[1]:
            zone_max = geometry_dimensions[1]
        return [zone_min, zone_max]

    def set_initial_temperature(self):
        self.ansys_commands.set_initial_temperature(
            temperature=self.input_data.temperature_settings.input.temperature_init)

        geometry_dimensions = InitialTemperatureUniform.find_start_and_end_length_of_coil(self.geometry.coil_geometry)
        ic_zone_dimensions = InitialTemperatureUniform.set_length_of_initial_ic_temperature_zone(
            zone_centre=self.input_data.analysis_settings.quench_init_position,
            zone_length=self.input_data.analysis_settings.quench_init_length,
            geometry_dimensions=geometry_dimensions)
        ic_zone_node_min = SearchNodes.search_init_node(
            position=ic_zone_dimensions[0], coil_length=self.geometry.coil_geometry)
        ic_zone_node_max = SearchNodes.search_init_node(
            position=ic_zone_dimensions[1], coil_length=self.geometry.coil_geometry)
        self.ansys_commands.select_nodes_in_analysis(
            self.geometry, x_down_node=ic_zone_node_min, x_up_node=ic_zone_node_max)
        self.ansys_commands.set_initial_temperature(
            temperature=self.input_data.temperature_settings.input.temperature_max_init_quenched_zone, allsel=False)

        self.calculate_energy_initially_deposited_inside_the_coil(
            magnetic_field_value=self.input_data.temperature_settings.input.magnetic_field_initially_quenched_winding,
            temperature_init_distr=self.initial_temperature_profile)

    @staticmethod
    def create_private_temperature_profile(node_down, node_up, temperature_constant):
        temp_profile = np.zeros((node_up-node_down+1, 2))
        temp_profile[:, 1] = temperature_constant
        j = 0
        for i in range(node_down, node_up+1):
            temp_profile[j, 0] = i
            j += 1
        return temp_profile
