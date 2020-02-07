
import os
import numpy as np
from source.common_functions.interpolation_functions import InterpolationFunctions
from source.common_functions.general_functions import GeneralFunctions
from source.physics.circuit.circuit import Circuit


class CircuitElectricAnalysisWithCircuit(Circuit):

    def __init__(self, ansys_commands, class_geometry, factory):
        Circuit.__init__(self, ansys_commands, class_geometry, factory)
        self.factory = factory
        self.diff_inductance = self.upload_differential_inductance()
        self.diff_inductance_interpolation = InterpolationFunctions.interpolate_linear_1d_function(
            x=self.diff_inductance[:, 0], y=self.diff_inductance[:, 1])
        self.build_circuit()

    def set_circuit_bcs_in_analysis(self):
        self.couple_nodes_in_analysis()
        self.set_ground()

    def build_circuit(self):
        resistance_dump = self.input_data.circuit_settings.transient_electric_analysis_input.R_dump
        inductance_init = InterpolationFunctions.get_value_from_linear_1d_interpolation(
            f_interpolation=self.diff_inductance_interpolation, x=self.current)[0]
        self.ansys_commands.define_parameter(parameter_name="resistance_dump", parameter=str(resistance_dump))
        self.ansys_commands.define_parameter(parameter_name="inductance_init", parameter=str(inductance_init))
        self.ansys_commands.define_parameter(parameter_name="current_init", parameter=str(self.current[0]))
        self.ansys_commands.input_file(filename="1D_1D_1D_Circuit", extension="inp",
                                       directory=self.ansys_commands.ansys_input_directory)

    def upload_differential_inductance(self):
        filename_directory = os.path.join(
            self.factory.input_file_directory,
            self.input_data.circuit_settings.transient_electric_analysis_input.L_diff_filename)
        diff_inductance_array = np.loadtxt(filename_directory, delimiter=",", skiprows=1)
        GeneralFunctions.copy_file_to_directory(
            filename=self.input_data.circuit_settings.transient_electric_analysis_input.L_diff_filename,
            filename_directory=self.factory.input_file_directory,
            desired_filename_directory=self.factory.input_copy_directory)
        return diff_inductance_array

    @staticmethod
    def qds_to_string(time_step):
        return "QUENCH HAS BEEN DETECTED AT t={}".format(time_step)

    def check_quench_with_qds(self, class_postprocessor):
        resistive_voltage = abs(class_postprocessor.resistive_voltage)
        time_step_vector = class_postprocessor.time_step_vector
        if not self.check_if_qds_was_applied():

            if self.qds_start_time is None and resistive_voltage >= self.input_data.circuit_settings.\
                    transient_electric_analysis_input.V_th:
                self.qds_start_time = time_step_vector[class_postprocessor.iteration[0]]
                self.qds_current_time = time_step_vector[class_postprocessor.iteration[0]]

            elif resistive_voltage >= self.input_data.circuit_settings.\
                    transient_electric_analysis_input.V_th:
                self.qds_current_time = time_step_vector[class_postprocessor.iteration[0]]

                # if self.detect_qds_duration_time(self.qds_start_time, self.qds_current_time):
                if self.detect_qds_duration_time(self.qds_start_time, self.qds_current_time):
                    print(self.qds_to_string(time_step=self.qds_current_time))
                    return True

    def detect_qds_duration_time(self, qds_start_time, qds_current_time):
        qds_duration_time = qds_current_time - qds_start_time
        if qds_duration_time >= self.input_data.circuit_settings.transient_electric_analysis_input.t_delay:
            self.qds_detection = True
            return True
        else:
            return False

    def check_if_qds_was_applied(self):
        if self.qds_detection:
            return True
        else:
            return False

    def check_if_analysis_is_finished(self, *args, **kwargs):
        if self.current[0] < self.input_data.circuit_settings.transient_electric_analysis_input.I_discharge_criterion:
            return True
        else:
            return False

    def check_discharge_input_statement(self):
        discharge_statement = hasattr(self.input_data.circuit_settings.transient_electric_analysis_input,
                                      "I_discharge_criterion")
        no_discharge_statement = hasattr(self.input_data.analysis_settings, "t_simulation")
        if discharge_statement is True and no_discharge_statement is True:
            raise AttributeError("Please decide whether you input total simulation time or "
                                 "the current discharge criterion")
        elif discharge_statement is False:
            raise AttributeError("Please input the current discharge criterion")
