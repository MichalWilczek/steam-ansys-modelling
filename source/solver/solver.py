
from source.physics.time_stepping.time_step import TimeStep
from source.common_functions.unit_conversion import UnitConversion

class Solver(object):

    def __init__(self, factory, ansys_commands, class_geometry,
                 circuit, ic_temperature_class, mat_props, mag_map):

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
        self.end_of_analysis = False

    def create_time_step_vector(self):
        return TimeStep.create_initial_time_step_vector(
            time_step=self.input_data.analysis_settings.time_step_cosimulation,
            total_time=self.input_data.analysis_settings.time_step_cosimulation)

    def check_if_analysis_is_finished(self):
        self.end_of_analysis = self.circuit.check_if_analysis_is_finished()

    def set_next_time_step(self):
        last_time_window = self.time_step_vector[-1]
        self.time_step_vector.append(last_time_window+self.input_data.analysis_settings.time_step_cosimulation)

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
            init_time_step=self.input_data.analysis_settings.time_step_min_ansys *
                           UnitConversion.miliseconds_to_seconds)

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
        self.ansys_commands.upload_apdl_solver_input_file()

    def end_of_time_step(self):
        self.iteration[0] += 1
        if len(self.time_step_vector) <= self.iteration[0]:
            self.t[0] = self.time_step_vector[self.iteration[0] - 2]
        else:
            self.t = [self.time_step_vector[self.iteration[0] - 1]]

    def restart_analysis(self):
        self.ansys_commands.restart_analysis()
