
from source.physics.quench_velocity.quench_detection import QuenchDetect
from source.common_functions.general_functions import GeneralFunctions
from source.post_processor.plots import Plots
import numpy as np

class PostProcessor(QuenchDetect):

    def __init__(self, class_geometry, ansys_commands, v_quench, solver, input_data):

        self.directory = solver.directory
        self.input_data = solver.input_data

        # input instance which will detect quench front from mapped Python geometry
        self.npoints = class_geometry.load_ansys_output_one_line_txt_file(
            filename="Nnode.txt", directory=self.directory)
        self.q_det = QuenchDetect(npoints=self.npoints, class_geometry=class_geometry, mat_props=solver.mat_props)
        self.plots = solver.plots

        self.ansys_commands = ansys_commands
        self.geometry = class_geometry
        self.qf = v_quench
        self.factory = input_data

        self.quench_label = 1
        self.quench_fronts = []
        self.quench_fronts_new = []
        self.quench_state_plots = []
        self.quench_temperature_plots = []

        self.temperature_profile = solver.temperature_ic_profile
        self.magnetic_map = solver.magnetic_map
        self.mat_props = solver.mat_props
        self.circuit = solver.circuit
        self.time_step_vector = solver.time_step_vector
        self.iteration = solver.iteration

        self.min_coil_length = self.geometry.coil_geometry[0, 1]
        self.max_coil_length = self.geometry.coil_geometry[len(self.geometry.coil_geometry) - 1, 1]

        self.resistive_voltage = None

    def get_temperature_profile(self):
        self.temperature_profile = self.ansys_commands.get_temperature_profile(
            npoints=self.npoints, class_geometry=self.geometry)
        self.plot_temperature_profile()

    def get_current(self):
        pass

    def plot_temperature_profile(self):
        time_step = [self.time_step_vector[self.iteration[0]]][0]

        txt_temperature_filename = "Temperature_Profile_" + str(self.iteration[0]) + ".txt"
        GeneralFunctions.save_array(directory=self.plots.output_directory_temperature,
                                    filename=txt_temperature_filename,
                                    array=self.temperature_profile)

        if self.input_data.temperature_settings.input.png_temperature_output:
            temperature_plot = self.plots.plot_and_save_temperature(
                directory=self.directory, coil_length=self.geometry.coil_geometry,
                temperature_profile_1d=self.temperature_profile, iteration=self.iteration[0], time_step=time_step)
            self.quench_temperature_plots.append(temperature_plot)

    def check_quench_state_heat_balance(self):
        pass

    def check_quench_state_quench_velocity(self):
        pass

    def plot_quench_state_in_analysis(self):
        iteration = self.iteration[0]

        quench_state_array = self.geometry.create_quench_state_array(
            coil_length_array=self.geometry.coil_geometry,
            quench_fronts_list=self.quench_fronts)
        GeneralFunctions.save_array(directory=self.plots.output_directory_quench_state,
                                    filename="quench_state_{}.txt".format(self.iteration[0]),
                                    array=quench_state_array)

        if self.input_data.analysis_type.input.png_quench_state_output:
            quench_state_plot = self.plots.plot_and_save_quench_state(
                quench_state_array, iteration=iteration)
            self.quench_state_plots.append(quench_state_plot)

    def estimate_coil_resistance(self):
        pass

    def update_magnetic_field(self):
        pass

    def estimate_quench_velocity(self):
        pass

    def make_gif(self):
        if self.input_data.temperature_settings.input.png_temperature_output:
            Plots.create_gif(plot_array=self.quench_temperature_plots, filename='video_temperature_distribution.gif',
                             directory=self.plots.output_directory_temperature)
        if self.input_data.analysis_type.input.png_quench_state_output:
            Plots.create_gif(plot_array=self.quench_state_plots, filename='video_quench_state.gif',
                             directory=self.plots.output_directory_quench_state)

    def write_down_resistive_voltage_to_file(self, resistive_voltage):
        self.resistive_voltage = resistive_voltage
        time_step = [self.time_step_vector[self.iteration[0]]][0]
        res_voltage_array = np.zeros((1, 3))
        res_voltage_array[0, 0] = time_step
        res_voltage_array[0, 1] = self.resistive_voltage / self.circuit.return_current_in_time_step()
        res_voltage_array[0, 2] = self.resistive_voltage
        if self.iteration == 1:
            Plots.write_line_in_file(directory=self.plots.output_directory_resistive_voltage,
                                     filename="Res_Voltage.txt", mydata=res_voltage_array)
        else:
            Plots.write_line_in_file(directory=self.plots.output_directory_resistive_voltage,
                                     filename="Res_Voltage.txt", mydata=res_voltage_array,
                                     newfile=False)

    def plot_resistive_voltage(self):
        if self.input_data.analysis_type.input.png_resistive_voltage_output:
            res_voltage_array = GeneralFunctions.load_file(directory=self.plots.output_directory_resistive_voltage,
                                                           npoints=len(self.time_step_vector)-1,
                                                           filename="Res_Voltage.txt")
            self.plots.plot_resistive_voltage(time_vector=res_voltage_array[:, 0],
                                              voltage_vector=res_voltage_array[:, 2],
                                              additional_description="ansys")
