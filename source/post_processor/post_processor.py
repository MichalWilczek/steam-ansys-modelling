
from source.post_processor.plots import Plots
from source.post_processor.quench_detection import QuenchDetect

class PostProcessor(Plots, QuenchDetect):

    def __init__(self, class_geometry, ansys_commands, v_quench, solver, input_data):

        # input instance which will detect quench front from mapped Python geometry
        self.npoints = class_geometry.load_parameter(filename="Nnode.txt")
        self.q_det = QuenchDetect(npoints=self.npoints, class_geometry=class_geometry, input_data=input_data)
        Plots.__init__(self)
        self.ansys_commands = ansys_commands
        self.geometry = class_geometry
        self.qf = v_quench
        self.factory = input_data

        self.quench_label = 1
        self.quench_fronts = []
        self.quench_state_plots = []
        self.quench_temperature_plots = []

        self.temperature_profile = solver.temperature_ic_profile
        self.magnetic_map = solver.magnetic_map
        self.material_properties = solver.material_properties
        self.circuit = solver.circuit
        self.t = solver.t
        self.time_step_vector = solver.time_step_vector
        self.iteration = solver.iteration
        self.directory = self.geometry.directory

    def get_temperature_profile(self):
        self.temperature_profile = self.ansys_commands.get_temperature_profile(
            npoints=self.npoints, class_geometry=self.geometry)
        self.plot_temperature_profile()

    def plot_temperature_profile(self):
        time_step = [self.time_step_vector[self.iteration[0]]][0]
        temperature_plot = Plots.plot_and_save_temperature(
            directory=self.directory, coil_length=self.geometry.coil_geometry,
            temperature_profile_1d=self.temperature_profile, iteration=self.iteration[0], time_step=time_step)
        plot_name = "Temperature_Profile_" + str(self.iteration[0]) + ".txt"
        Plots.save_array(directory=self.directory, filename=plot_name, array=self.temperature_profile)
        self.quench_temperature_plots.append(temperature_plot)

    def check_quench_state(self):
        pass

    def plot_quench_state_in_analysis(self):
        iteration = self.iteration[0]
        time_step = self.time_step_vector[iteration]
        quench_state_plot = self.plot_and_save_quench_state(
            directory=self.directory, coil_length=self.geometry.coil_geometry,
            quench_fronts=self.quench_fronts, iteration=iteration, time_step=time_step)
        self.quench_state_plots.append(quench_state_plot)

    def estimate_coil_resistance(self):
        pass

    def estimate_initial_quench_velocity(self):
        pass

    def estimate_quench_velocity(self):
        pass

    def make_gif(self):
        self.create_gif(plot_array=self.quench_state_plots, filename='video_quench_state.gif')
        self.create_gif(plot_array=self.quench_temperature_plots, filename='video_temperature_distribution.gif')
