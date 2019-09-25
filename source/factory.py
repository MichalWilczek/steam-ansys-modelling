
import json
import os


class AnalysisBuilder(object):

    def __init__(self):
        self.parameters = self.load_parameters()

    @staticmethod
    def load_parameters(filename='config.json'):
        os.chdir(AnalysisDirectory.define_main_path())
        with open(filename) as json_data_file:
            return json.load(json_data_file)

    def get_magnet_type(self):
        return self.parameters['magnet_type']

    def get_geometry_type(self):
        return self.parameters['geometry_type']

    def get_dimensionality(self):
        return self.parameters['dimensionality']

    def get_peak_initial_temperature(self):
        return self.parameters['initial_peak_temperature']

    def get_initial_temperature(self):
        return self.parameters['initial_temperature']

    def get_division_long_side(self):
        return self.parameters['division_long_side']

    def get_division_short_side(self):
        return self.parameters['division_short_side']

    def get_division_radius(self):
        return self.parameters['division_radius']

    def get_number_of_windings_in_reel(self):
        return self.parameters['number_of_windings_in_reel']

    def get_material_properties_type(self):
        return self.parameters['nonlinear_material_properties']

    def filename_nodal_position(self):
        return self.parameters['filename_nodal_position']

    def filename_nodal_temperature(self):
        return self.parameters['filename_nodal_temperature']

    def get_number_of_windings(self):
        return self.parameters['number_of_windings']

    def get_length_per_winding(self):
        return self.parameters['length_per_winding']

    def get_division_per_winding(self):
        return self.parameters['division_per_winding']

    def get_division_in_full_coil(self):
        return self.parameters['division_per_winding'] * self.parameters['number_of_windings']

    def get_quench_init_pos(self):
        return self.parameters['quench_init_pos']

    def get_quench_init_length(self):
        return self.parameters['quench_init_length']

    def get_quench_init_x_down(self):
        return self.parameters['quench_init_pos'] - self.parameters['quench_init_length']/2.0

    def get_quench_init_x_up(self):
        return self.parameters['quench_init_pos'] + self.parameters['quench_init_length'] / 2.0

    def get_total_time(self):
        return self.parameters['total_time']

    def get_time_division(self):
        return self.parameters['time_division']

    def get_time_step(self):
        return self.parameters['total_time'] / self.parameters['time_division']

    def get_current(self):
        return self.parameters['current']

    def get_winding_plane_max_number_nodes(self):
        return self.parameters['winding_plane_max_number_nodes']

    def get_transverse_dimension_winding(self):
        return self.parameters['transverse_dimension_winding']

    def get_transverse_dimension_insulation(self):
        return self.parameters['transverse_dimension_insulation']

    def get_transverse_division_winding(self):
        return self.parameters['transverse_division_winding']

    def get_transverse_division_insulation(self):
        return self.parameters['transverse_division_insulation']

    def get_electric_analysis(self):
        return self.parameters['electric_analysis']

    def get_quench_velocity_model(self):
        return self.parameters['quench_velocity_model']

    def get_magnetic_map_model(self):
        return self.parameters["magnetic_map_model"]

class AnalysisDirectory(object):

    @staticmethod
    def get_directory(dimension):
        if dimension == "1D":
            return AnalysisDirectory.directory_1d()
        elif dimension == "1D_1D":
            return AnalysisDirectory.directory_1d_1d()
        elif dimension == "1D_1D_1D":
            return AnalysisDirectory.directory_1d_1d_1d()
        elif dimension == "2D":
            return AnalysisDirectory.directory_2d()
        elif dimension == "3D":
            return AnalysisDirectory.directory_3d()
        else:
            raise ValueError(dimension)

    @staticmethod
    def define_main_path():
        CWD = os.path.dirname(__file__)
        return CWD

    @staticmethod
    def directory_1d():
        source = AnalysisDirectory.define_main_path()
        path = os.path.join(source, 'APDL', '1D')
        return path

    @staticmethod
    def directory_1d_1d():
        source = AnalysisDirectory.define_main_path()
        path = os.path.join(source, 'APDL', '1D_1D')
        return path

    @staticmethod
    def directory_1d_1d_1d():
        source = AnalysisDirectory.define_main_path()
        path = os.path.join(source, 'APDL', '1D_1D_1D')
        return path

    @staticmethod
    def directory_2d():
        source = AnalysisDirectory.define_main_path()
        path = os.path.join(source, 'APDL', '2D')
        return path

    @staticmethod
    def directory_3d():
        source = AnalysisDirectory.define_main_path()
        path = os.path.join(source, 'APDL', '3D')
        return path
