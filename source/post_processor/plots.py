
from source.common_functions.general_functions import GeneralFunctions
import numpy as np
import matplotlib.pyplot as plt
import imageio
import os


class Plots(object):

    def __init__(self, factory):
        self.output_directory = factory.output_directory
        self.output_directory_quench_state = GeneralFunctions.create_folder_in_directory(
            self.output_directory, "quench_state_output")
        self.output_directory_resistive_voltage = GeneralFunctions.create_folder_in_directory(
            self.output_directory, "resistive_voltage_output")
        self.output_directory_temperature = GeneralFunctions.create_folder_in_directory(
            self.output_directory, "temperature_profile_output")

    def plot_resistive_voltage(self, time_vector, voltage_vector, additional_description):
        """
        Plots resistive voltage as a function of time
        :param time_vector:
        :param voltage_vector:
        :param additional_description:
        """
        os.chdir(self.output_directory_resistive_voltage)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_xlabel('Time [s]')
        ax.set_ylabel('V_res, V')
        ax.plot(time_vector, voltage_vector)
        plt.grid(True)
        plt.show()
        filename = "resistive_voltage_{}.png".format(additional_description)
        fig.savefig(filename)
        return fig

    @staticmethod
    def plot_quench_state(quench_state_array):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_xlabel('L_coil, m')
        ax.set_ylabel('Quench state')
        ax.set_yticks(ticks=[0, 1])
        ax.plot(quench_state_array[:, 0], quench_state_array[:, 1], linewidth=1.5)
        plt.grid(True)
        plt.show()
        return fig

    @staticmethod
    def write_line_in_file(directory, filename, mydata, newfile=True):
        os.chdir(directory)
        if newfile:
            with open(filename, "wb") as f:
                np.savetxt(f, mydata, delimiter=' ')
        else:
            with open(filename, "ab") as f:
                np.savetxt(f, mydata, delimiter=' ')

    @staticmethod
    def save_quench_state_plot(fig, iteration, filename="quench_state_"):
        """
        Saves quench state plot
        :param fig: quench plot as plt.figure()
        :param iteration: simulation iteration as integer
        """
        filename = "{}{}.png".format(filename, iteration)
        fig.savefig(filename)
        return filename

    def plot_and_save_quench_state(self, quench_state_array, iteration):
        """
        Plots and saves quench state plot
        :param coil_length: coil length numpy array; 1st column - node number, 2nd column position in [m]
        :param quench_fronts: list of QuenchFront objects
        :param time_step: time step as float
        :param iteration: simulation iteration as integer
        """
        os.chdir(self.output_directory_quench_state)
        fig = self.plot_quench_state(quench_state_array)
        filename = Plots.save_quench_state_plot(fig=fig, iteration=iteration)
        return filename

    @staticmethod
    def create_gif(directory, plot_array, filename, duration=0.2):
        """
        Creates gif from series of plots
        :param plot_array: list of plots as plt.figure()
        :param filename: filename as string
        :param duration: time of each plot frame as float (optional)
        """
        os.chdir(directory)
        with imageio.get_writer(filename, duration=duration) as writer:
            for filename in plot_array:
                image = imageio.imread(filename)
                writer.append_data(image)

    @staticmethod
    def plot_temperature(coil_length, directory, temperature_profile_1d, time_step, filename):
        """
        Plots temperature distribution
        :param coil_length: coil length numpy array; 1st column - node number, 2nd column position in [m]
        :param directory: analysis output_directory as string
        :param filename: filename as string
        :param time_step: time step as float
        """
        time_step = round(time_step, 4)
        length_node_temp_array = np.column_stack((coil_length, temperature_profile_1d[:, 1]))
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_xlabel('L_coil, m')
        ax.set_ylabel('T, K')
        plt.title("t = {} s".format(time_step))
        ax.plot(length_node_temp_array[:, 1], length_node_temp_array[:, 2])
        plt.grid(True)
        plt.show()
        if os.path.isfile(filename):
            GeneralFunctions.delete_file(directory=directory, filename=filename)
        return fig

    @staticmethod
    def save_temperature_plot(fig, iteration):
        """
        Saves temperature distribution plot
        :param fig: temperature distribution as plt.figure()
        :param iteration: simulation iteration as integer
        """
        filename = "temperature_distribution_{}.png".format(iteration)
        fig.savefig(filename)
        return filename

    def plot_and_save_temperature(self, directory, coil_length, temperature_profile_1d,
                                  iteration, time_step, filename="Temperature_Data.txt"):
        """
        Plots and saves temperature distribution
        :param coil_length: coil length numpy array; 1st column - node number, 2nd column position in [m]
        :param directory: analysis output_directory as string
        :param filename: filename as string
        :param time_step: time step as float
        :param iteration: simulation iteration as integer
        """
        os.chdir(self.output_directory_temperature)
        fig = Plots.plot_temperature(coil_length, directory, temperature_profile_1d, time_step, filename)
        saved_file = Plots.save_temperature_plot(fig=fig, iteration=iteration)
        return saved_file
