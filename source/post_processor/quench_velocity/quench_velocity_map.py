
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d
from scipy import interpolate
import os


class QuenchVelocityMap(object):

    def __init__(self, factory, plot=False):
        self.input_directory = factory.input_directory
        self.quench_velocity_map_filename = factory.input_data.analysis_type.input.numerical_map_filename
        self.time_axis = self.load_q_v_array()[:, 0]
        self.q_v_array = self.load_q_v_array()[:, 1:]
        self.f_interpolation = self.create_interpolation_f_qv()
        if plot:
            self.plot_interpolated_function(self.f_interpolation)

    def load_q_v_array(self):
        """
        Loads Quench velocity array from file
        :return: numpy array
        """
        filename = os.path.join(self.input_directory, self.quench_velocity_map_filename)
        array = np.loadtxt(fname=filename, skiprows=1)
        return array

    def create_interpolation_f_qv(self):
        """
        Creates interpolation quench velocity function
        :return: interpolation instance
        """
        t_axis = self.time_axis.ravel()
        B_axis = np.arange(0.0, 3.5, 0.5)
        q_v_grid = self.q_v_array
        return interpolate.RectBivariateSpline(t_axis, B_axis, q_v_grid, kx=3, ky=1)

    @staticmethod
    def plot_interpolated_function(f_interpolation):
        """
        Plots 3D quench velocity interpolation plot as function of time and B-field
        :param f_interpolation: interpolation instance
        """
        t_axis = np.arange(0.0, 0.16, 0.01)
        B_axis = np.arange(0.0, 3.1, 0.1)
        T = t_axis
        B = B_axis
        for i in range(len(B_axis)-1):
            T = np.vstack((T, t_axis))
        for j in range(len(t_axis)-1):
            B = np.vstack((B, B_axis))
        B_trans = np.transpose(B)
        q_v_matrix = f_interpolation(t_axis, B_axis)
        Q_V_trans = np.transpose(q_v_matrix)
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_wireframe(T, B_trans, Q_V_trans, rstride=5, cstride=2)
        plt.xlabel("Time [s]", fontsize=10)
        # ax.set_xticks(ticks=[0.0, 0.1], minor=True)
        ax.set_xticks(ticks=[0.0, 0.05, 0.1, 0.15])
        # plt.set_x
        plt.ylabel("B-field [T]")
        ax.view_init(elev=25, azim=35)
        ax.dist = 10
        filename = "Quench_Velocity_Map.png"
        plt.savefig(filename, dpi=200)
        plt.show()

