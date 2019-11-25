
import numpy as np
from source.factory.interpolation_functions import InterpolationFunctions
from source.circuit.circuit import Circuit

class CircuitElectricAnalysisWithCircuit(Circuit, InterpolationFunctions):

    def __init__(self, ansys_commands, class_geometry, factory):
        Circuit.__init__(self, ansys_commands, class_geometry, factory)
        self.diff_inductance = self.upload_differential_inductance()
        self.diff_inductance_interpolation = InterpolationFunctions.interpolate_linear_function(
            x=self.diff_inductance[:, 0], y=self.diff_inductance[:, 1])
        self.build_circuit()

    def set_circuit_bcs_in_analysis(self):
        self.couple_nodes_in_analysis()
        self.set_ground()

    def build_circuit(self):
        resistance_dump = self.input_data.circuit_settings.transient_electric_analysis_input.resistance_dump
        current_init = self.input_data.circuit_settings.electric_ansys_element_input.current_init
        inductance_init = InterpolationFunctions.get_value_from_linear_1d_interpolation(
            f_interpolation=self.diff_inductance_interpolation, x=current_init)
        self.ansys_commands.define_parameter(parameter_name="resistance_dump", parameter=str(resistance_dump))
        self.ansys_commands.define_parameter(parameter_name="inductance_init", parameter=str(inductance_init))
        self.ansys_commands.define_parameter(parameter_name="current_init", parameter=str(current_init))

        self.ansys_commands.input_file(filename="1D_1D_1D_Circuit", extension="inp",
                                       directory=self.ansys_commands.ansys_input_directory)

    def upload_differential_inductance(self):

        filename_directory = self.input_data.circuit_settings.transient_electric_analysis_input.\
            inductance_filename_directory
        diff_inductance_array = np.loadtxt(filename_directory, delimiter=",", skiprows=1)
        return diff_inductance_array

