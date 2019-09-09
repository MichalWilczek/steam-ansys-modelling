
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate


class MagneticMap(object):

    FILENAME = "steady_state_B_map.txt"
    DIRECTORY = "C:\\gitlab\\steam-ansys-modelling\\quadrupole_experimental_results\\field_data"
    NUMBER_TURNS_IN_LAYER = 29
    NUMBER_LAYERS = 26
    WINDING_WIDTH = 0.941

    def __init__(self, plot=False):
        self.mag_map = self.load_magnetic_field_map()
        self.pos_x_winding = self.make_winding_pos_x()
        self.pos_y_winding = self.make_winding_pos_y()
        self.interpolation_f = self.create_interpolation_f_magnetic_field()

        if plot:
            self.mag_plot_contour = self.make_magnetic_contour_plot()
            self.mag_plot_colour = self.make_magnetic_colour_plot()
            self.plot_winding_vector_arrangement()
            self.winding_pos_plot = self.make_winding_pos_map()
            self.plot_interpolated_function()
            self.interpol_error_plot = self.plot_error_between_meas_and_interpolation()

    def create_wind_real_number_list(self, winding_list):
        """
        Creates list of windings taken into consideration in analysis
        :param winding_list: list of integers
        :return: list of strings, winding%winding_number%
        """
        return self.create_list_with_winding_names(winding_list)

    @staticmethod
    def create_list_with_winding_names(list_numbers):
        """
        Returns the following list of strings; winding%winding_number%
        :param list_numbers: list of integers
        :return: list of strings
        """
        winding_list = []
        for item in list_numbers:
            winding_list.append("winding" + str(item))
        return winding_list

    @staticmethod
    def flatten_list(list_to_flatten):
        """
        Flattens list of list
        :param list_to_flatten: list of lists
        :return: list
        """
        flat_list = []
        for sublist in list_to_flatten:
            for item in sublist:
                flat_list.append(item)
        return flat_list

    @staticmethod
    def shorten_mag_map_dict(mag_map, winding_name_list):
        """
        Returns dictionary with only windings taken into analysis
        :param mag_map: full dictionary with assigned magnetic field
        :param winding_name_list: list of strings with winding names taken into analysis
        :return: reduced magnetic field map dictionary
        """
        new_mag_map = {}
        for name in winding_name_list:
            value = mag_map[name]
            new_mag_map[name] = value[2]
        return new_mag_map

    def plot_winding_vector_arrangement(self, transverse_lines=False):
        """
        Plots winding arrangement in a half quadrant of a quadrupole
        :param transverse_lines: transverse vector lines plotting as boolean, default as False
        """
        x_pos = self.winding_x_pos_list()
        y_pos = self.winding_y_pos_list()

        x_pos_up = x_pos[::2]
        x_pos_down = x_pos[1::2]

        y_pos_up = y_pos[0]
        y_pos_down = y_pos[-1]

        y_pos_up_list = []
        for i in range(len(x_pos_up)):
            y_pos_up_list.append(y_pos_up)

        y_pos_down_list = []
        for i in range(len(x_pos_down)):
            y_pos_down_list.append(y_pos_down)

        fig = plt.figure()
        plot = fig.add_subplot(111)
        plot.quiver(x_pos_up, y_pos_up_list, 0, 1, scale=1.5, color="red")
        plot.quiver(x_pos_down, y_pos_down_list, 0, -1, scale=1.5, color="red")

        if transverse_lines:
            x_pos_right = x_pos[:(len(x_pos) - 1)]
            y_pos_right = []
            for i in range(len(x_pos)):
                y_pos_right.append(y_pos_down)
                y_pos_right.append(y_pos_up)
            y_pos_right = y_pos_right[0:int((len(x_pos) - 1.0))]
            plot.quiver(x_pos_right, y_pos_right, 1, 0, scale=25, color="red")

        plt.axis('equal')
        plt.xlabel("x-direction [mm]")
        plt.ylabel("y-direction [mm]")
        plt.grid(True)
        filename = "Winding_Scheme.png"
        plt.savefig(filename, dpi=200)
        plt.show()

    @staticmethod
    def load_magnetic_field_map():
        """
        Loads file with magnetic field from file
        :return: numpy array 2D
        """
        os.chdir(MagneticMap.DIRECTORY)
        magnetic_map = np.loadtxt(MagneticMap.FILENAME, skiprows=8)
        return magnetic_map

    def create_interpolation_f_magnetic_field(self):
        """
        Creates interpolation function for rectangular mesh
        :return: interpolation function
        """
        x_meas = (self.mag_map[:, 0] - self.mag_map[:, 0].min())[:20]
        y_meas = (self.mag_map[:, 1] - self.mag_map[:, 1].min())[0::20]
        b_field_meas = self.mag_map[:, 5]
        b_field_meas_grid = b_field_meas.reshape(20, 20)
        return interpolate.RectBivariateSpline(y_meas, x_meas, b_field_meas_grid, kx=2, ky=2)

    def create_interpolated_mag_field_matrix(self):
        """
        Creates numpy array where with interpolated magnetic field strength based on windings' position
        :return: numpy array
        """
        f = self.create_interpolation_f_magnetic_field()
        pos_x_winding = self.winding_x_pos_list()
        pos_y_winding = self.winding_y_pos_list()
        matrix_interpol = f(pos_y_winding, pos_x_winding)
        return matrix_interpol

    def plot_interpolated_function(self):
        """
        Plots a 3D plot with magnetic field interpolation function over an x, y - coordinates
        """
        pos_x_winding = self.winding_x_pos_list()
        array_x = pos_x_winding
        for i in range(self.NUMBER_TURNS_IN_LAYER-1):
            pos_x_winding = np.vstack((pos_x_winding, array_x))

        pos_y_winding = self.winding_y_pos_list()
        array_y = pos_y_winding
        for i in range(self.NUMBER_LAYERS-1):
            pos_y_winding = np.vstack((pos_y_winding, array_y))
        pos_y_winding_trans = np.transpose(pos_y_winding)

        matrix_interpol = self.create_interpolated_mag_field_matrix()
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_wireframe(pos_x_winding, pos_y_winding_trans, matrix_interpol, rstride=2, cstride=3)
        plt.xlabel("x-direction [mm]")
        plt.ylabel("y-direction [mm]")
        ax.view_init(elev=30, azim=40)
        ax.dist = 10
        filename = "Quadrupole_Magnetic_Field_Interpolation_plot.png"
        plt.savefig(filename, dpi=200)
        plt.show()

    @staticmethod
    def winding_y_pos_list():
        """
        Creates a horizontal array with y-position of a consecutive magnet layer
        :return: numpy array with one row
        """
        init_pos_x = MagneticMap.WINDING_WIDTH / 2.0
        number_turns_in_layer = MagneticMap.NUMBER_TURNS_IN_LAYER
        array = np.arange(init_pos_x, MagneticMap.WINDING_WIDTH*number_turns_in_layer+init_pos_x,
                          MagneticMap.WINDING_WIDTH)
        return array

    @staticmethod
    def winding_x_pos_list():
        """
        Creates a horizontal array with x-position of a consecutive magnet layer
        :return: numpy array with one row
        """
        init_pos_x = MagneticMap.WINDING_WIDTH / 2.0
        number_layers = MagneticMap.NUMBER_LAYERS
        array = np.arange(init_pos_x, MagneticMap.WINDING_WIDTH*number_layers+init_pos_x, MagneticMap.WINDING_WIDTH)
        return array

    def make_magnetic_contour_plot(self):
        """
        Creates contour map of magnetic field distribution in the magnet cross-section
        :return: plot instance
        """
        x_axis = self.mag_map[:, 0] - self.mag_map[:, 0].min()
        y_axis = self.mag_map[:, 1] - self.mag_map[:, 1].min()
        b_field = self.mag_map[:, 5]
        x = x_axis.reshape(20, 20)
        y = y_axis.reshape(20, 20)
        z = b_field.reshape(20, 20)
        quad_mag_field_contour = plt.contour(x, y, z, 12)
        plt.clabel(quad_mag_field_contour, inline=1, fontsize=10)
        plt.axis('equal')
        plt.xlabel("x-direction [mm]")
        plt.ylabel("y-direction [mm]")
        plt.grid(True)
        filename = "Quadrupole_Magnetic_Contour_plot.png"
        plt.savefig(filename, dpi=200)
        plt.show()
        return quad_mag_field_contour

    def make_magnetic_colour_plot(self):
        """
        Creates colour map of magnetic field distribution in the magnet cross-section
        :return: plot instance
        """
        x_axis = self.mag_map[:, 0] - self.mag_map[:, 0].min()
        y_axis = self.mag_map[:, 1] - self.mag_map[:, 1].min()
        b_field = self.mag_map[:, 5]
        x = x_axis.reshape(20, 20)
        y = y_axis.reshape(20, 20)
        z = b_field.reshape(20, 20)
        quad_mag_field_colour = plt.contourf(x, y, z, 20)
        plt.axis('equal')
        plt.xlabel("x-direction [mm]")
        plt.ylabel("y-direction [mm]")
        filename = "Quadrupole_Magnetic_Colour_plot.png"
        plt.grid(True)
        plt.colorbar(label='Magnetic Field [T]')
        plt.savefig(filename, dpi=200)
        plt.show()
        return quad_mag_field_colour

    def plot_error_between_meas_and_interpolation(self):
        """
        Creates colour map with relative error between interpolation function and measurements from analysis
        :return: plot instance
        """
        x_axis = self.mag_map[:, 0] - self.mag_map[:, 0].min()
        y_axis = self.mag_map[:, 1] - self.mag_map[:, 1].min()
        b_field = self.mag_map[:, 5]
        x = x_axis.reshape(20, 20)
        y = y_axis.reshape(20, 20)
        z = b_field.reshape(20, 20)

        interpolation_matrix = np.zeros((len(z[:, 0]), len(z[0, :])))
        for i in range(len(z[:, 0])):
            for j in range(len(z[0, :])):
                x_value = x[i, j]
                y_value = y[i, j]
                interpolation_matrix[i, j] = self.interpolation_f.__call__(y_value, x_value)[0]
        error_matrix = (z - interpolation_matrix)/z*100.0
        quad_mag_error_colour = plt.contourf(x, y, error_matrix, 20)
        plt.axis('equal')
        plt.xlabel("x-direction [mm]")
        plt.ylabel("y-direction [mm]")
        filename = "Quadrupole_Magnetic_Field_Interpolation_Error_plot.png"
        plt.colorbar(label='Relative Error [%]')
        plt.savefig(filename, dpi=200)
        plt.show()
        return quad_mag_error_colour

    def make_winding_pos_map(self):
        """
        Plots winding positions in x-y Cartesian coordinate system
        :return: plot instance
        """
        pos_x = self.pos_x_winding
        pos_y = self.pos_y_winding
        fig = plt.figure()
        plot = fig.add_subplot(111)
        plot.set_xlabel('x-direction [mm]')
        plot.set_ylabel('y-direction [mm]')
        plt.axis('equal')
        plot.set_xlim(0.0, 24.46)
        plot.set_ylim(0.0, 27.3)
        plot.plot(pos_x, pos_y, 'o', markersize=4, color="b")
        plt.grid(True)
        filename = "Quadrupole_Winding_Map_plot.png"
        plt.savefig(filename, dpi=200)
        plt.show()
        return plot

    @staticmethod
    def make_winding_pos_x():
        """
        Creates vertical array where each row represents x_position of a winding in numerical order
        :return: numpy array, 1st column x_pos of winding as float
        """
        init_pos_x = 0.941 / 2.0
        number_turns_in_layer = MagneticMap.NUMBER_TURNS_IN_LAYER
        number_layers = MagneticMap.NUMBER_LAYERS
        pos_x = np.zeros((number_turns_in_layer * number_layers, 1))
        wind_counter_x = 1
        for i in range(number_layers):
            for j in range(number_turns_in_layer):
                pos_x[wind_counter_x - 1] = init_pos_x
                wind_counter_x += 1
            init_pos_x += 0.941
        return pos_x

    @staticmethod
    def make_winding_pos_y():
        """
        Creates vertical array where each row represents y_position of a winding in numerical order
        :return: numpy array, 1st column y_pos of winding as float
        """
        number_turns_in_layer = MagneticMap.NUMBER_TURNS_IN_LAYER
        number_layers = MagneticMap.NUMBER_LAYERS
        pos_y = np.zeros((number_turns_in_layer * number_layers, 1))
        wind_counter_y = 1
        for i in range(0, number_layers, 2):
            init_pos_y1 = 0.941 / 2.0
            for j in range(number_turns_in_layer):
                pos_y[wind_counter_y - 1] = init_pos_y1
                init_pos_y1 += 0.941
                wind_counter_y += 1
            wind_counter_y += number_turns_in_layer
        wind_counter_y = number_turns_in_layer
        for i in range(0, number_layers-1, 2):
            init_pos_y2 = 0.941 / 2.0 + (float(number_turns_in_layer)-1)*0.941
            for j in range(number_turns_in_layer):
                pos_y[wind_counter_y] = init_pos_y2
                if j != number_turns_in_layer - 1:
                    init_pos_y2 -= 0.941
                wind_counter_y += 1
            wind_counter_y += number_turns_in_layer
        return pos_y

    @staticmethod
    def check_if_kwarg_exists(kwargs, name):
        if name not in kwargs:
            raise ValueError("kwarg '{}' is not called in the function".format(name))
