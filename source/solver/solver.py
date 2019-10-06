
from source.solver.time_step import TimeStep
from source.processor_post.quench_detection import QuenchDetect

class Solver(TimeStep, QuenchDetect):

    def __init__(self, ansys_commands, class_geometry, input_data, circuit, ic_temperature_class, mat_props, mag_map):
        self.temperature_ic = ic_temperature_class
        self.temperature_ic_profile = None
        self.geometry = class_geometry
        self.ansys_commands = ansys_commands
        self.circuit = circuit
        self.factory = input_data
        self.material_properties = mat_props
        self.magnetic_map = mag_map

        self.iteration = [0]
        self.time_step_vector = TimeStep.linear_time_stepping(time_step=self.factory.time_step_cosimulation,
                                                              total_time=self.factory.time_total_simulation)
        self.t = [self.time_step_vector[self.iteration[0]]]

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

        self.ansys_commands.set_ansys_time_step_settings(min_time_step=self.factory.time_step_min_ansys/1000.0,
                                                         max_time_step=self.factory.time_step_max_ansys/1000.0,
                                                         init_time_step=self.factory.time_step_min_ansys/1000.0)

    def set_time_step(self):
        self.ansys_commands.set_time_step(time_step=self.time_step_vector[self.iteration[0]], iteration=self.iteration[0])

    def set_initial_temperature(self):
        self.temperature_ic.set_initial_temperature()

    def set_time_step_temperature(self):
        self.temperature_ic.set_temperature_in_time_step(iteration=self.iteration[0])

    def set_solver_bcs(self):
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
