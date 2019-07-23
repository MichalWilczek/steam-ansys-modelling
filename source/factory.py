
import json


class AnalysisBuilder:

    def __init__(self):
        self.input_parameters = AnalysisBuilder.load_parameters()

    @staticmethod
    def load_parameters(filename='config.json'):
        with open(filename) as json_data_file:
            return json.load(json_data_file)

    def get_dimensionality(self):
        return self.input_parameters['dimensionality']

    def filename_nodal_position(self):
        return self.input_parameters['filename_nodal_position']

    def filename_nodal_temperature(self):
        return self.input_parameters['filename_nodal_temperature']

    def get_number_of_windings(self):
        return self.input_parameters['number_of_windings']

    def get_length_per_winding(self):
        return self.input_parameters['length_per_winding']

    def get_division_per_winding(self):
        return self.input_parameters['division_per_winding']

    def get_division_in_full_coil(self):
        return self.input_parameters['division_per_winding']*self.input_parameters['number_of_windings']

    def get_quench_init_pos(self):
        return self.input_parameters['quench_init_pos']

    def get_quench_init_length(self):
        return self.input_parameters['quench_init_length']

    def get_quench_init_x_down(self):
        return self.input_parameters['quench_init_pos']-self.input_parameters['quench_init_length']/2.0

    def get_quench_init_x_up(self):
        return self.input_parameters['quench_init_pos'] + self.input_parameters['quench_init_length'] / 2.0

    def get_total_time(self):
        return self.input_parameters['total_time']

    def get_time_division(self):
        return self.input_parameters['time_division']

    def get_current(self):
        return self.input_parameters['current']

    def get_initial_temperature(self):
        return self.input_parameters['initial_temperature']

    def get_winding_plane_max_number_nodes(self):
        return self.input_parameters['winding_plane_max_number_nodes']

    def get_transverse_dimension_winding(self):
        return self.input_parameters['transverse_dimension_winding']

    def get_transverse_dimension_insulation(self):
        return self.input_parameters['transverse_dimension_insulation']

    def get_transverse_division_winding(self):
        return self.input_parameters['transverse_division_winding']

    def get_transverse_division_insulation(self):
        return self.input_parameters['transverse_division_insulation']


class AnalysisDirectory:

    @staticmethod
    def get_directory():
        dimension = AnalysisBuilder().get_dimensionality()
        if dimension == "1D":
            return AnalysisDirectory().directory_1d()
        elif dimension == "2D":
            return AnalysisDirectory().directory_2d()
        elif dimension == "3D":
            return AnalysisDirectory().directory_3d()
        else:
            raise ValueError(dimension)

    @staticmethod
    def define_main_path():
        return "C:\\gitlab\\steam-ansys-modelling\\source"

    @staticmethod
    def directory_1d():
        return "C:\\gitlab\\steam-ansys-modelling\\source\\APDL\\1D"

    @staticmethod
    def directory_2d():
        return "C:\\gitlab\\steam-ansys-modelling\\source\\APDL\\2D"

    @staticmethod
    def directory_3d():
        return "C:\\gitlab\\steam-ansys-modelling\\source\\APDL\\3D"
