
from source.magnetic_field.magnetic_field import MagneticField
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate

class MagneticFieldMap(MagneticField):

    def __init__(self, factory):
        MagneticField.__init__(self, factory)

    @staticmethod
    def create_wind_real_number_list(winding_list):
        """
        Creates list of windings taken into consideration in analysis
        :param winding_list: list of integers
        :return: list of strings, winding%winding_number%
        """
        return MagneticFieldMap.create_list_with_winding_names(winding_list)

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

    @staticmethod
    def plot_winding_vector_arrangement(x_pos_windings, y_pos_windings, directory, transverse_lines=False):
        """
        Plots winding arrangement in a half quadrant of a quadrupole
        :param transverse_lines: transverse vector lines plotting as boolean, default as False
        """
        x_pos = x_pos_windings
        y_pos = y_pos_windings

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
        os.chdir(directory)
        plt.savefig(filename, dpi=200)

    @staticmethod
    def load_magnetic_field_map(directory, filename):
        """
        Loads file with magnetic field from file
        :return: numpy array 2D
        """
        os.chdir(directory)
        magnetic_map = np.loadtxt(filename, skiprows=8)
        return magnetic_map

    @staticmethod
    def create_interpolation_f_magnetic_field(mag_map):
        """
        Creates interpolation function for rectangular mesh
        :return: interpolation function
        """
        x_meas = (mag_map[:, 0] - mag_map[:, 0].min())[:20]
        y_meas = (mag_map[:, 1] - mag_map[:, 1].min())[0::20]
        b_field_meas = mag_map[:, 5]
        b_field_meas_grid = b_field_meas.reshape(20, 20)
        return interpolate.RectBivariateSpline(y_meas, x_meas, b_field_meas_grid, kx=2, ky=2)

    @staticmethod
    def create_interpolated_mag_field_matrix(mag_map, winding_side, number_turns_in_layer, number_layers):
        """
        Creates numpy array where with interpolated magnetic field strength based on windings' position
        :return: numpy array
        """
        f = MagneticFieldMap.create_interpolation_f_magnetic_field(mag_map)
        pos_x_winding = MagneticFieldMap.winding_x_pos_list(winding_side, number_layers)
        pos_y_winding = MagneticFieldMap.winding_y_pos_list(winding_side, number_turns_in_layer)
        matrix_interpol = f(pos_y_winding, pos_x_winding)
        return matrix_interpol

    @staticmethod
    def plot_interpolated_function(mag_map, winding_side, number_layers, number_turns_in_layer, directory):
        """
        Plots a 3D plot with magnetic field interpolation function over an x, y - coordinates
        """
        pos_x_winding = MagneticFieldMap.winding_x_pos_list(winding_side, number_layers)
        array_x = pos_x_winding
        for i in range(number_turns_in_layer-1):
            pos_x_winding = np.vstack((pos_x_winding, array_x))

        pos_y_winding = MagneticFieldMap.winding_y_pos_list(winding_side, number_turns_in_layer)
        array_y = pos_y_winding
        for i in range(number_layers-1):
            pos_y_winding = np.vstack((pos_y_winding, array_y))
        pos_y_winding_trans = np.transpose(pos_y_winding)

        matrix_interpol = MagneticFieldMap.create_interpolated_mag_field_matrix(mag_map, winding_side,
                                                                                number_turns_in_layer, number_layers)
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_wireframe(pos_x_winding, pos_y_winding_trans, matrix_interpol, rstride=2, cstride=3)
        plt.xlabel("x-direction [mm]")
        plt.ylabel("y-direction [mm]")
        ax.view_init(elev=30, azim=40)
        ax.dist = 10
        filename = "Quadrupole_Magnetic_Field_Interpolation_plot.png"
        os.chdir(directory)
        plt.savefig(filename, dpi=200)

    @staticmethod
    def winding_y_pos_list(winding_side, number_turns_in_layer):
        """
        Creates a horizontal array with y-position of a consecutive magnet layer
        :return: numpy array with one row
        """
        init_pos_x = winding_side / 2.0
        array = np.arange(init_pos_x, winding_side*number_turns_in_layer+init_pos_x, winding_side)
        return array

    @staticmethod
    def winding_x_pos_list(winding_side, number_layers):
        """
        Creates a horizontal array with x-position of a consecutive magnet layer
        :return: numpy array with one row
        """
        init_pos_x = winding_side / 2.0
        array = np.arange(init_pos_x, winding_side*number_layers+init_pos_x, winding_side)
        return array

    @staticmethod
    def make_magnetic_contour_plot(mag_map, directory):
        """
        Creates contour map of magnetic field distribution in the magnet cross-section
        :return: plot instance
        """
        x_axis = mag_map[:, 0] - mag_map[:, 0].min()
        y_axis = mag_map[:, 1] - mag_map[:, 1].min()
        b_field = mag_map[:, 5]
        x = x_axis.reshape(20, 20)
        y = y_axis.reshape(20, 20)
        z = b_field.reshape(20, 20)
        plt.clabel(plt.contour(x, y, z, 12), inline=1, fontsize=10)
        plt.axis('equal')
        plt.xlabel("x-direction [mm]")
        plt.ylabel("y-direction [mm]")
        plt.grid(True)
        filename = "Quadrupole_Magnetic_Contour_plot.png"
        os.chdir(directory)
        plt.savefig(filename, dpi=200)

    @staticmethod
    def make_magnetic_colour_plot(mag_map, directory):
        """
        Creates colour map of magnetic field distribution in the magnet cross-section
        :return: plot instance
        """
        x_axis = mag_map[:, 0] - mag_map[:, 0].min()
        y_axis = mag_map[:, 1] - mag_map[:, 1].min()
        b_field = mag_map[:, 5]
        x = x_axis.reshape(20, 20)
        y = y_axis.reshape(20, 20)
        z = b_field.reshape(20, 20)
        plt.contourf(x, y, z, 20)
        plt.axis('equal')
        plt.xlabel("x-direction [mm]")
        plt.ylabel("y-direction [mm]")
        filename = "Quadrupole_Magnetic_Colour_plot.png"
        plt.grid(True)
        plt.colorbar(label='Magnetic Field [T]')
        os.chdir(directory)
        plt.savefig(filename, dpi=200)

    @staticmethod
    def make_winding_pos_map(pos_x_winding, pos_y_winding, directory):
        """
        Plots winding positions in x-y Cartesian coordinate system
        :return: plot instance
        """
        pos_x = pos_x_winding
        pos_y = pos_y_winding
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
        os.chdir(directory)
        plt.savefig(filename, dpi=200)

    @staticmethod
    def make_winding_pos_x(winding_side, number_turns_in_layer, number_layers):
        """
        Creates vertical array where each row represents x_position of a winding in numerical order
        :return: numpy array, 1st column x_pos of winding as float
        """
        init_pos_x = winding_side / 2.0
        pos_x = np.zeros((number_turns_in_layer * number_layers, 1))
        wind_counter_x = 1
        for i in range(number_layers):
            for j in range(number_turns_in_layer):
                pos_x[wind_counter_x - 1] = init_pos_x
                wind_counter_x += 1
            init_pos_x += winding_side
        return pos_x

    @staticmethod
    def make_winding_pos_y(winding_side, number_turns_in_layer, number_layers):
        """
        Creates vertical array where each row represents y_position of a winding in numerical order
        :return: numpy array, 1st column y_pos of winding as float
        """
        pos_y = np.zeros((number_turns_in_layer * number_layers, 1))
        wind_counter_y = 1
        for i in range(0, number_layers, 2):
            init_pos_y1 = winding_side / 2.0
            for j in range(number_turns_in_layer):
                pos_y[wind_counter_y - 1] = init_pos_y1
                init_pos_y1 += winding_side
                wind_counter_y += 1
            wind_counter_y += number_turns_in_layer
        wind_counter_y = number_turns_in_layer
        for i in range(0, number_layers-1, 2):
            init_pos_y2 = winding_side / 2.0 + (float(number_turns_in_layer)-1)*winding_side
            for j in range(number_turns_in_layer):
                pos_y[wind_counter_y] = init_pos_y2
                if j != number_turns_in_layer - 1:
                    init_pos_y2 -= winding_side
                wind_counter_y += 1
            wind_counter_y += number_turns_in_layer
        return pos_y
