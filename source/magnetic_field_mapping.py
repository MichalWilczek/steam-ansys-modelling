
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

    def __init__(self):
        self.mag_map = self.load_magnetic_field_map()
        self.mag_plot_contour = self.make_magnetic_contour_plot()
        self.mag_plot_colour = self.make_magnetic_colour_plot()
        self.pos_x_winding = self.make_winding_pos_x()
        self.pos_y_winding = self.make_winding_pos_y()
        self.winding_pos_plot = self.make_winding_pos_map()
        self.interpolation_f = self.create_interpolation_f_magnetic_field()
        self.wind_mag_dict = self.assign_magnetic_field_to_windings()
        self.plot_interpolated_function()
        self.interpol_error_plot = self.plot_error_between_meas_and_interpolation()

    def assign_magnetic_field_to_windings(self):
        winding_main_dict = {}
        pos_x_win = self.pos_x_winding
        pos_y_wind = self.pos_y_winding
        for i in range(len(pos_x_win)):
            wind_data = []
            wind_data.append(pos_x_win[i, :][0])
            wind_data.append(pos_y_wind[i, :][0])
            wind_data.append(self.interpolation_f.__call__(pos_y_wind[i, :][0], pos_x_win[i, :][0])[0][0])
            winding_main_dict["winding"+str(i+1)] = wind_data
        return winding_main_dict

    def load_magnetic_field_map(self):
        os.chdir(self.DIRECTORY)
        magnetic_map = np.loadtxt(self.FILENAME, skiprows=8)
        return magnetic_map

    def create_interpolation_f_magnetic_field(self):
        x_meas = (self.mag_map[:, 0] - self.mag_map[:, 0].min())[:20]
        y_meas = (self.mag_map[:, 1] - self.mag_map[:, 1].min())[0::20]
        B_field_meas = self.mag_map[:, 5]
        B_field_meas_grid = B_field_meas.reshape(20, 20)
        return interpolate.RectBivariateSpline(y_meas, x_meas, B_field_meas_grid, kx=2, ky=2)

    def create_interpolated_mag_field_matrix(self):
        f = self.create_interpolation_f_magnetic_field()
        pos_x_winding = self.winding_x_pos_list()
        pos_y_winding = self.winding_y_pos_list()
        matrix_interpol = f(pos_y_winding, pos_x_winding)
        return matrix_interpol

    def plot_real_data(self):
        x_axis = self.mag_map[:, 0] - self.mag_map[:, 0].min()
        y_axis = self.mag_map[:, 1] - self.mag_map[:, 1].min()
        B_field = self.mag_map[:, 5]
        x = x_axis.reshape(20, 20)
        y = y_axis.reshape(20, 20)
        z = B_field.reshape(20, 20)
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_wireframe(x, y, z, rstride=2, cstride=3)
        ax.view_init(elev=30, azim=40)
        ax.dist = 10
        plt.show()

    def plot_interpolated_function(self):
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

    def winding_y_pos_list(self):
        init_pos_x = self.WINDING_WIDTH / 2.0
        number_turns_in_layer = self.NUMBER_TURNS_IN_LAYER
        array = np.arange(init_pos_x, self.WINDING_WIDTH*number_turns_in_layer+init_pos_x, self.WINDING_WIDTH)
        return array

    def winding_x_pos_list(self):
        init_pos_x = self.WINDING_WIDTH / 2.0
        number_layers = self.NUMBER_LAYERS
        array = np.arange(init_pos_x, self.WINDING_WIDTH*number_layers+init_pos_x, self.WINDING_WIDTH)
        return array

    def make_magnetic_contour_plot(self):
        x_axis = self.mag_map[:, 0] - self.mag_map[:, 0].min()
        y_axis = self.mag_map[:, 1] - self.mag_map[:, 1].min()
        B_field = self.mag_map[:, 5]
        x = x_axis.reshape(20, 20)
        y = y_axis.reshape(20, 20)
        z = B_field.reshape(20, 20)
        Quad_mag_field_contour = plt.contour(x, y, z, 12)
        plt.clabel(Quad_mag_field_contour, inline=1, fontsize=10)
        plt.axis('equal')
        plt.xlabel("x-direction [mm]")
        plt.ylabel("y-direction [mm]")
        plt.grid(True)
        filename = "Quadrupole_Magnetic_Contour_plot.png"
        plt.savefig(filename, dpi=200)
        plt.show()
        return Quad_mag_field_contour

    def make_magnetic_colour_plot(self):
        x_axis = self.mag_map[:, 0] - self.mag_map[:, 0].min()
        y_axis = self.mag_map[:, 1] - self.mag_map[:, 1].min()
        B_field = self.mag_map[:, 5]
        x = x_axis.reshape(20, 20)
        y = y_axis.reshape(20, 20)
        z = B_field.reshape(20, 20)
        Quad_mag_field_colour = plt.contourf(x, y, z, 20)
        plt.axis('equal')
        # plt.title('Magnetic field contour map')
        plt.xlabel("x-direction [mm]")
        plt.ylabel("y-direction [mm]")
        filename = "Quadrupole_Magnetic_Colour_plot.png"
        plt.grid(True)
        plt.colorbar(label='Magnetic Field [T]')
        plt.savefig(filename, dpi=200)
        plt.show()
        return Quad_mag_field_colour

    def plot_error_between_meas_and_interpolation(self):
        x_axis = self.mag_map[:, 0] - self.mag_map[:, 0].min()
        y_axis = self.mag_map[:, 1] - self.mag_map[:, 1].min()
        B_field = self.mag_map[:, 5]
        x = x_axis.reshape(20, 20)
        y = y_axis.reshape(20, 20)
        z = B_field.reshape(20, 20)

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

    def make_winding_pos_x(self):
        init_pos_x = 0.941 / 2.0
        number_turns_in_layer = self.NUMBER_TURNS_IN_LAYER
        number_layers = self.NUMBER_LAYERS
        pos_x = np.zeros((number_turns_in_layer * number_layers, 1))
        wind_counter_x = 1
        for i in range(number_layers):
            for j in range(number_turns_in_layer):
                pos_x[wind_counter_x - 1] = init_pos_x
                wind_counter_x += 1
            init_pos_x += 0.941
        return pos_x

    def make_winding_pos_y(self):
        number_turns_in_layer = self.NUMBER_TURNS_IN_LAYER
        number_layers = self.NUMBER_LAYERS
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












