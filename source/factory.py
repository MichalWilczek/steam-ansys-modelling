

config = {
    # variables for all cases
    'dimensionality': '2D',
    'number_of_windings': 2,
    'length_per_winding': 0.5,        # winding_length, [m]
    'division_per_winding': 500,      # winding_division, number of element divisions across the coil cross-section

    # analysis parameters
    'quench_init_pos': 0.25,          # [m], with respect to the 1st winding defined in ansys
    'quench_init_length': 0.01,       # [m]
    'total_time': 0.5,                # [s]
    'time_division': 200.0,           # number of time steps

    # variables for ansys boundary/initial conditions
    'current': 1000,                  # [A]
    'initial_temperature': 1.9,       # [K]

    # variables for 2D analysis
    'winding_plane_max_number_nodes': 5,             # max_nodes_cross_section, verify ansys element type to be used
    'transverse_dimension_winding': 0.840*0.001,     # winding_width, [m]
    'transverse_dimension_insulation': 0.101*0.001,  # insulation_width, [m]
    'transverse_division_winding': 2,    # winding_division, number of element divisions across the coil cross-section
    'transverse_division_insulation': 3  # insulation_division, number of element divisions across the insulation layer
}


class AnalysisBuilder:

    def __call__(self, *args):
        print(*args)


test_code = AnalysisBuilder()
test_code.__call__(config)


class QuenchFactory:

    def __init__(self):
        self.dimensionality = {}

    def register_dimensionality(self, dimension, creator):
        self.dimensionality[dimension] = creator

    def get_dimensionality(self, dimension):
        creator = self.dimensionality.get(dimension)
        if not creator:
            raise ValueError(dimension)
        return creator






class AnalysisDirectory:

    def get_directory(self, dimension):
        if dimension == "1D":
            return self.directory_1d()
        elif dimension == "2D":
            return self.directory_2d()
        elif dimension == "3D":
            return self.directory_3d()
        else:
            raise ValueError(dimension)

    @staticmethod
    def directory_1d():
        return "C:\\gitlab\\steam-ansys-modelling\\source\APDL\\1D"

    @staticmethod
    def directory_2d():
        return "C:\\gitlab\\steam-ansys-modelling\\source\\APDL\\2D"

    @staticmethod
    def directory_3d():
        return "C:\\gitlab\\steam-ansys-modelling\\source\\APDL\\3D"


 # class VariableFile:
 #
 #    @staticmethod
 #    def create_variable_file_2d():


























