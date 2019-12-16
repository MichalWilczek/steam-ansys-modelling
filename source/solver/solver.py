
from source.solver.time_step import TimeStep
from source.factory.unit_conversion import UnitConversion
from source.post_processor.quench_detection import QuenchDetect
from source.factory.general_functions import GeneralFunctions

class Solver(TimeStep, QuenchDetect, UnitConversion):

    def __init__(self, factory, ansys_commands, class_geometry, circuit, ic_temperature_class, mat_props, mag_map):

        self.factory = factory
        self.input_data = factory.input_data
        self.directory = factory.directory
        self.output_directory = factory.output_directory

        self.temperature_ic = ic_temperature_class
        self.plots = ic_temperature_class.plots
        self.temperature_ic_profile = None
        self.geometry = class_geometry
        self.ansys_commands = ansys_commands
        self.circuit = circuit
        self.mat_props = mat_props
        self.magnetic_map = mag_map

        self.iteration = [0]
        self.time_step_vector = self.create_time_step_vector()
        self.t = [self.time_step_vector[self.iteration[0]]]

    def create_time_step_vector(self):

        discharge_statement = hasattr(self.input_data.circuit_settings.transient_electric_analysis_input, "magnet_discharge_current")
        no_discharge_statement = hasattr(self.input_data.analysis_settings, "time_total_simulation")

        if discharge_statement is True and no_discharge_statement is False:
            return TimeStep.linear_time_stepping(
                time_step=self.input_data.analysis_settings.time_step_cosimulation,
                total_time=self.input_data.analysis_settings.time_step_cosimulation)
        elif discharge_statement is False and no_discharge_statement is True:
            return TimeStep.linear_time_stepping(
                time_step=self.input_data.analysis_settings.time_step_cosimulation,
                total_time=self.input_data.analysis_settings.time_total_simulation)
        else:
            return ValueError("Please decide whether you input total simulation time or "
                              "the discharge statement for current")

    def time_to_string(self):
        print("------------------------------------------------------\
              \n iteration number: {} \n time step: {} \n \
               ------------------------------------------------------".
              format(self.iteration[0], self.time_step_vector[self.iteration[0]]))

    def create_ic_temperature_profile(self):
        self.temperature_ic_profile = self.temperature_ic.create_ic_temperature_profile()

    def set_circuit_bcs(self):
        self.circuit.set_circuit_bcs_in_analysis()

    def enter_solver_settings(self):
        self.ansys_commands.enter_solver()
        self.time_to_string()
        self.ansys_commands.set_analysis_setting()

        self.ansys_commands.set_ansys_time_step_settings(
            min_time_step=self.input_data.analysis_settings.time_step_min_ansys * UnitConversion.miliseconds_to_seconds,
            max_time_step=self.input_data.analysis_settings.time_step_max_ansys * UnitConversion.miliseconds_to_seconds,
            init_time_step=self.input_data.analysis_settings.time_step_min_ansys * UnitConversion.miliseconds_to_seconds)

    def set_time_step(self):
        self.ansys_commands.set_time_step(
            time_step=self.time_step_vector[self.iteration[0]], iteration=self.iteration[0])

    def set_initial_temperature(self):
        self.temperature_ic.set_initial_temperature()

    def set_time_step_temperature(self):
        self.temperature_ic.set_temperature_in_time_step(iteration=self.iteration[0])

    def set_solver_boundary_conditions(self):
        pass

    def solve(self):
        self.ansys_commands.input_solver()

    def end_of_time_step(self):
        self.iteration[0] += 1
        if len(self.time_step_vector) <= self.iteration[0]:
            self.t[0] = self.time_step_vector[self.iteration[0] - 2]
        else:
            self.t = [self.time_step_vector[self.iteration[0] - 1]]

    def restart_analysis(self):
        self.ansys_commands.restart_analysis()

