
import os
import matplotlib as mpl
import matplotlib.pyplot as plt
from source.magnetic_field.magnetic_field_map import MagneticFieldMap
from source.factory.general_functions import GeneralFunctions
import numpy as np

class MagneticFieldPlotting(GeneralFunctions):

    @staticmethod
    def plot_mag_field_in_windings(x_vector, y_vector, b_field_vector, discretisation_number=51):
        discretisation_array = np.linspace(0, 1, discretisation_number)
        discrete_colors = plt.cm.jet(discretisation_array)

        cmap = plt.get_cmap('jet', discretisation_number)
        Vmin = b_field_vector.min()
        Vmax = b_field_vector.max()
        Vrange = np.absolute(Vmax - Vmin)
        color_vector = (b_field_vector - Vmin) / Vrange

        norm = mpl.colors.Normalize(vmin=Vmin, vmax=Vmax)
        discrete_color_vector = []
        for x in np.nditer(color_vector):
            discrete_color_vector.append(GeneralFunctions.find_nearest_in_numpy_array(discretisation_array, x))

        discrete_color_vector = np.array(discrete_color_vector)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_xlabel('x-direction [mm]')
        ax.set_ylabel('y-direction [mm]')
        for i in range(np.size(x_vector)):
            ax.plot(x_vector[i], y_vector[i], 'o', markersize=4,
                    color=discrete_colors[int(np.where(discretisation_array == discrete_color_vector[i])[0])])
        plt.axis('equal')
        plt.grid(True)

        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        fig.colorbar(sm, ticks=np.linspace(Vmin, Vmax, int(discretisation_number / 5)),
                     boundaries=np.arange(Vmin - Vrange * 0.05, Vmax + Vrange * 0.05, Vrange/10), label='Magnetic Field [T]')
        plt.show()

    @staticmethod
    def plot_winding_vector_arrangement(x_pos_windings, y_pos_windings, directory, transverse_lines=False) :
        """
        Plots winding arrangement in a half quadrant of a quadrupole
        :param transverse_lines: transverse vector lines plotting as boolean, default as False
        """
        x_pos = x_pos_windings
        y_pos = y_pos_windings

        x_pos_up = x_pos[: :2]
        x_pos_down = x_pos[1 : :2]

        y_pos_up = y_pos[0]
        y_pos_down = y_pos[-1]

        y_pos_up_list = []
        for i in range(len(x_pos_up)) :
            y_pos_up_list.append(y_pos_up)

        y_pos_down_list = []
        for i in range(len(x_pos_down)) :
            y_pos_down_list.append(y_pos_down)

        fig = plt.figure()
        plot = fig.add_subplot(111)
        plot.quiver(x_pos_up, y_pos_up_list, 0, 1, scale=1.5, color="red")
        plot.quiver(x_pos_down, y_pos_down_list, 0, -1, scale=1.5, color="red")

        if transverse_lines :
            x_pos_right = x_pos[:(len(x_pos) - 1)]
            y_pos_right = []
            for i in range(len(x_pos)) :
                y_pos_right.append(y_pos_down)
                y_pos_right.append(y_pos_up)
            y_pos_right = y_pos_right[0 :int((len(x_pos) - 1.0))]
            plot.quiver(x_pos_right, y_pos_right, 1, 0, scale=25, color="red")

        plt.axis('equal')
        plt.xlabel("x-direction [mm]")
        plt.ylabel("y-direction [mm]")
        plt.grid(True)
        filename = "Winding_Scheme.png"
        os.chdir(directory)
        plt.savefig(filename, dpi=200)

    @staticmethod
    def plot_interpolated_function(mag_map, winding_side, layers, number_turns_in_layer, directory):
        """
        Plots a 3D plot with magnetic field interpolation function over an x, y - coordinates
        """
        pos_x_winding = MagneticFieldMap.winding_x_pos_list(winding_side, layers)
        array_x = pos_x_winding
        for i in range(number_turns_in_layer-1):
            pos_x_winding = np.vstack((pos_x_winding, array_x))

        pos_y_winding = MagneticFieldMap.winding_y_pos_list(winding_side, number_turns_in_layer)
        array_y = pos_y_winding
        for i in range(layers-1):
            pos_y_winding = np.vstack((pos_y_winding, array_y))
        pos_y_winding_trans = np.transpose(pos_y_winding)

        matrix_interpol = MagneticFieldMap.create_interpolated_mag_field_matrix(mag_map, winding_side,
                                                                                number_turns_in_layer, layers)
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
