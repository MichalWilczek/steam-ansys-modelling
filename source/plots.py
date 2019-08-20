
from source.factory import AnalysisDirectory, AnalysisBuilder
import numpy as np
import matplotlib.pyplot as plt
import imageio
import os

def file_length(filename, analysis_directory):
    """
    :param filename: filename with extension as string
    :param analysis_directory: string
    :return: number of rows in a file as integer
    """
    os.chdir(analysis_directory)
    with open(filename) as myfile:
        return int(len(myfile.readlines()))


class Plots(object):

    def __init__(self):
        self.factory = AnalysisBuilder()
        self.directory = AnalysisDirectory().get_directory(self.factory.get_dimensionality())
        self.voltage_plot = None

    @staticmethod
    def plot_quench(coil_length, quench_fronts, time_step):
        """
        Plots quench state
        :param coil_length: coil length numpy array; 1st column - node number, 2nd column position in [m]
        :param quench_fronts: list of QuenchFront objects
        :param time_step: time step as float
        """
        time_step = round(time_step, 4)
        max_coil_length = coil_length[len(coil_length) - 1, 1]
        min_coil_length = coil_length[0, 1]
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_xlabel('Position [m]')
        ax.set_ylabel('Quench state')
        ax.set_ylim(0, 1.1)
        plt.title("Time step: {} s".format(time_step))
        plt.xlim(min_coil_length, max_coil_length)
        plt.ylim(0, 2)
        if len(quench_fronts) != 0:
            for j in range(len(quench_fronts)):
                x_down = quench_fronts[j].x_down
                x_up = quench_fronts[j].x_up
                if j == 0 and len(quench_fronts) != 1:
                    x_set = [min_coil_length, x_down, x_down, x_up, x_up]
                    y_set = [0, 0, 1, 1, 0]
                elif j == 0 and len(quench_fronts) == 1:
                    x_set = [min_coil_length, x_down, x_down, x_up, x_up, max_coil_length]
                    y_set = [0, 0, 1, 1, 0, 0]
                elif j != 0 and j == len(quench_fronts)-1:
                    x_set = [quench_fronts[j-1].x_up, x_down, x_down, x_up, x_up, max_coil_length]
                    y_set = [0, 0, 1, 1, 0, 0]
                else:
                    x_set = [quench_fronts[j-1].x_up, x_down, x_down, x_up, x_up]
                    y_set = [0, 0, 1, 1, 0]
                plt.plot(x_set, y_set, '-', marker='8', markersize=8, linewidth=5, color='b')
        else:
            x_set = [min_coil_length, max_coil_length]
            y_set = [0, 0]
            plt.plot(x_set, y_set, '-', marker='8', markersize=8, linewidth=5, color='b')

        plt.grid(True)
        return fig

    def save_array(self, filename, array):
        array_filename = self.directory + "\\" + filename
        np.savetxt(array_filename, array)

    def write_line_in_file(self, filename, mydata, newfile=True):
        if newfile:
            with open(filename, "wb") as f:
                np.savetxt(f, mydata, delimiter=' ')
        else:
            with open(filename, "ab") as f:
                np.savetxt(f, mydata, delimiter=' ')

    @staticmethod
    def save_quench_plot(fig, iteration):
        """
        Saves quench state plot
        :param fig: quench plot as plt.figure()
        :param iteration: simulation iteration as integer
        """
        filename = "quench_state_{}.png".format(iteration)
        fig.savefig(filename)
        return filename

    def plot_and_save_quench(self, coil_length, quench_fronts, iteration, time_step):
        """
        Plots and saves quench state plot
        :param coil_length: coil length numpy array; 1st column - node number, 2nd column position in [m]
        :param quench_fronts: list of QuenchFront objects
        :param time_step: time step as float
        :param fig: quench plot as plt.figure()
        :param iteration: simulation iteration as integer
        """
        os.chdir(self.directory)
        fig = Plots.plot_quench(coil_length=coil_length, quench_fronts=quench_fronts, time_step=time_step)
        filename = Plots.save_quench_plot(fig=fig, iteration=iteration)
        return filename

    @staticmethod
    def create_video(plot_array, filename, duration=0.2):
        """
        Creates gif from series of plots
        :param plot_array: list of plots as plt.figure()
        :param filename: filename as string
        :param duration: time of each plot frame as float (optional)
        """
        with imageio.get_writer(filename, duration=duration) as writer:
            for filename in plot_array:
                image = imageio.imread(filename)
                writer.append_data(image)

    @staticmethod
    def load_file(directory, npoints, filename='Temperature_Data.txt'):
        """
        Loads file as numpy array if its number of rows corresponds to number of nodes in geometry
        :param directory: analysis directory as string
        :param npoints: number of nodes in defined geometry
        :param filename: filename as string, 'Temperature_Data.txt' set as default
        """
        temp_distr = None
        exists = False
        while exists is False:
            exists = os.path.isfile(directory+"\\."+filename)
            if exists and file_length(filename, analysis_directory=directory) == npoints:
                os.chdir(directory)
                temp_distr = np.loadtxt(directory+"\\."+filename)
            else:
                exists = False
        return temp_distr

    @staticmethod
    def delete_file(directory, filename='Temperature_Data'):
        """
        Deletes file with temperature profile
        :param directory: analysis directory as string
        :param filename: filename as string, 'Temperature_Data' set as default
        """
        full_filename = "{}.".format(filename)
        full_path = "{}\\{}".format(directory, full_filename)
        if os.path.isfile(full_path):
            os.remove(full_path)
        else:
            print("Error: {} file not found".format(full_filename))

    @staticmethod
    def plot_temperature(coil_length, directory, temperature_profile_1d, time_step, filename):
        """
        Plots temperature distribution
        :param coil_length: coil length numpy array; 1st column - node number, 2nd column position in [m]
        :param directory: analysis directory as string
        :param filename: filename as string
        :param time_step: time step as float
        """
        time_step = round(time_step, 4)
        length_node_temp_array = np.column_stack((coil_length, temperature_profile_1d[:, 1]))
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_xlabel('Position [m]')
        ax.set_ylabel('Temperature [K]')
        # ax.set_ylim(0, 10)
        plt.title("Time step: {} s".format(time_step))
        ax.plot(length_node_temp_array[:, 1], length_node_temp_array[:, 2])
        plt.grid(True)
        plt.show()
        Plots.delete_file(directory=directory, filename=filename)
        return fig

    def plot_resistive_voltage(self, voltage, time_step, iteration):
        """
        Plots resistive voltage as a function of time
        :param voltage: voltage value as float
        :param time_step: time step as float
        :param iteration: iteration number as integer
        """
        if iteration == 0:
            self.voltage_fig = plt.figure()
            self.voltage_plot = self.voltage_fig.add_subplot(111)
            self.voltage_plot.set_xlabel('Time [s]')
            self.voltage_plot.set_ylabel('Electric Potential [V]')
            self.voltage_plot.set_xlim(0, self.factory.get_total_time()+0.01)
            self.voltage_plot.set_ylim(0, 1.0)
            self.voltage_plot.plot(time_step, voltage, 'o', markersize=5, color="b")
            plt.grid(True)
        else:
            self.voltage_plot.plot(time_step, voltage, 'o', markersize=5, color="b")
            plt.show()
        filename = "resistive_voltage_{}.png".format(iteration)
        self.voltage_fig.savefig(filename)

    @staticmethod
    def save_temperature_plot(fig, iteration):
        """
        Saves temperature distribution plot
        :param fig: temperature distribution as plt.figure()
        :param iteration: simulation iteration as integer
        """
        filename = "temperature_distrirbution_{}.png".format(iteration)
        fig.savefig(filename)
        return filename

    def plot_and_save_temperature(self, coil_length, temperature_profile_1d, iteration, time_step, filename="Temperature_Data.txt"):
        """
        Plots and saves temperature disitribution
        :param coil_length: coil length numpy array; 1st column - node number, 2nd column position in [m]
        :param directory: analysis directory as string
        :param filename: filename as string
        :param time_step: time step as float
        :param fig: temperature distribution as plt.figure()
        :param iteration: simulation iteration as integer
        """
        fig = Plots.plot_temperature(coil_length, self.directory, temperature_profile_1d, time_step, filename)
        saved_file = Plots.save_temperature_plot(fig=fig, iteration=iteration)
        return saved_file

    @staticmethod
    def plot_gaussian_temperature_distribution(temperature_distribution, coil_geometry):
        """
        Plots the initial temperature distribution set in ANSYS
        :param temperature_distribution: temperature profile numpy array; 1st column: node number as integer,
        2nd column: temperature as float
        :param coil_geometry: 1D imaginary coil geometry as numpy array
        :return: instance with a plot
        """
        temp_plot_array = np.column_stack((coil_geometry[:, 1], temperature_distribution[:, 1]))
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_xlabel('Position [m]')
        ax.set_ylabel('Initial Temperature [K]')
        plt.title("Initial temperature distribution")
        ax.plot(temp_plot_array[:, 0], temp_plot_array[:, 1])
        plt.grid(True)
        plt.show()
        filename = "initial_temperature_distribution.png"
        fig.savefig(filename)
        return fig
