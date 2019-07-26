
import json
import os


class AnalysisBuilder:

    @staticmethod
    def load_parameters(filename='config.json'):
        os.chdir(AnalysisDirectory.define_main_path())
        with open(filename) as json_data_file:
            return json.load(json_data_file)
    @staticmethod
    def get_dimensionality():
        return AnalysisBuilder.load_parameters()['dimensionality']
    @staticmethod
    def filename_nodal_position():
        return AnalysisBuilder.load_parameters()['filename_nodal_position']
    @staticmethod
    def filename_nodal_temperature():
        return AnalysisBuilder.load_parameters()['filename_nodal_temperature']
    @staticmethod
    def get_number_of_windings():
        return AnalysisBuilder.load_parameters()['number_of_windings']
    @staticmethod
    def get_length_per_winding():
        return AnalysisBuilder.load_parameters()['length_per_winding']
    @staticmethod
    def get_division_per_winding():
        return AnalysisBuilder.load_parameters()['division_per_winding']
    @staticmethod
    def get_division_in_full_coil():
        return AnalysisBuilder.load_parameters()['division_per_winding'] * \
               AnalysisBuilder.load_parameters()['number_of_windings']
    @staticmethod
    def get_quench_init_pos():
        return AnalysisBuilder.load_parameters()['quench_init_pos']

    @staticmethod
    def get_quench_init_length():
        return AnalysisBuilder.load_parameters()['quench_init_length']

    @staticmethod
    def get_quench_init_x_down():
        return AnalysisBuilder.load_parameters()['quench_init_pos'] - \
               AnalysisBuilder.load_parameters()['quench_init_length']/2.0

    @staticmethod
    def get_quench_init_x_up():
        return AnalysisBuilder.load_parameters()['quench_init_pos'] + \
               AnalysisBuilder.load_parameters()['quench_init_length'] / 2.0

    @staticmethod
    def get_total_time():
        return AnalysisBuilder.load_parameters()['total_time']

    @staticmethod
    def get_time_division():
        return AnalysisBuilder.load_parameters()['time_division']

    @staticmethod
    def get_current():
        return AnalysisBuilder.load_parameters()['current']

    @staticmethod
    def get_initial_temperature():
        return AnalysisBuilder.load_parameters()['initial_temperature']

    @staticmethod
    def get_winding_plane_max_number_nodes():
        return AnalysisBuilder.load_parameters()['winding_plane_max_number_nodes']

    @staticmethod
    def get_transverse_dimension_winding():
        return AnalysisBuilder.load_parameters()['transverse_dimension_winding']

    @staticmethod
    def get_transverse_dimension_insulation():
        return AnalysisBuilder.load_parameters()['transverse_dimension_insulation']

    @staticmethod
    def get_transverse_division_winding():
        return AnalysisBuilder.load_parameters()['transverse_division_winding']

    @staticmethod
    def get_transverse_division_insulation():
        return AnalysisBuilder.load_parameters()['transverse_division_insulation']


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
