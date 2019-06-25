
import numpy as np
import matplotlib.pyplot as plt
import imageio
from variables import Variables
import os


class Plots:

    def file_length(self, filename):
        myfile = open(filename)
        return int(len(myfile.readlines()))

    def plot_quench(self, coil_length, quench_fronts):

        max_coil_length = coil_length[len(coil_length) - 1, 1]
        min_coil_length = coil_length[0, 1]
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_xlabel('coil length [m]')
        plt.xlim(min_coil_length, max_coil_length)
        plt.ylim(0, 2)

        # for qf in quench_fronts:
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

        plt.title('Quench Occurrence, q(t)')
        plt.grid(True)
        # plt.show()
        return fig

    def save_quench_plot(self, fig, iteration):
        filename = "quench_propagation_i{}.png".format(iteration)
        fig.savefig(filename)
        return filename

    def create_video(self, plot_array, filename, extension):
        with imageio.get_writer(filename+extension, mode='I', duration=0.02) as writer:
            for filename in plot_array:
                image = imageio.imread(filename)
                writer.append_data(image)

    def plot_temperature(self, coil_length, filename='Temperature_Data', extension='txt'):

        full_filename = "{}.{}".format(filename, extension)
        full_path = "{}\\{}".format(Variables().analysis_directory, full_filename)
        exists = False
        while exists is False:
            exists = os.path.isfile(full_path)
            # print("The file Process_Finished.txt exists = {}".format(exists))
            if exists and self.file_length(full_filename) == Variables().npoints:
                os.chdir(Variables().analysis_directory)
                f = open(full_filename, 'r')
                # temp_distr = np.loadtxt(full_filename)
                temp_distr = np.loadtxt(f)
                f.close()
            else:
                exists = False

        length_node_temp_array = np.column_stack((coil_length, temp_distr[:, 1]))
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_xlabel('position [m]')
        ax.set_ylabel('temperature [K]')
        ax.plot(length_node_temp_array[:, 1], length_node_temp_array[:, 2])
        plt.title('Quench position, x(t)')
        plt.grid(True)
        # plt.show()

        if os.path.isfile(full_path):
            os.remove(full_path)
        else:
            print("Error: {} file not found".format(full_filename))

        return fig

    def save_temperature_plot(self, fig, iteration):
        filename = "temperature_distrirbution{}.png".format(iteration)
        fig.savefig(filename)
        return filename






























