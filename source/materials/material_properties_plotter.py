
import matplotlib.pyplot as plt
import os

class MaterialPropertiesPlotter(object):

    @staticmethod
    def plot_material_properties(directory, filename, array,
                                 y_axis_name, x_axis_name='temperature, ' r'$K$', fontsize=12):
        """
        Saves material property plot
        :param directory: directory for saving the file as string
        :param filename: filename for saving as string
        :param array: numpy array to be plotted; 1st column: x values as float, 2nd column: y values as float
        :param y_axis_name: y-axis name as string
        :param x_axis_name: x-axis name as string set default as 'temperature, K'
        :param fontsize: fontsize of y- and x-axis as string, default-12
        """
        left_boundary = array[0, 0]
        right_boundary = array[len(array) - 1, 0]
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_xlabel(x_axis_name, fontsize=fontsize)
        ax.set_ylabel(y_axis_name, fontsize=fontsize)
        plt.xlim(left_boundary, right_boundary)
        ax.plot(array[:, 0], array[:, 1])
        plt.grid(True)
        ax.ticklabel_format(axis='y', scilimits=(0, 0))
        os.chdir(directory)
        fig.savefig(filename)
