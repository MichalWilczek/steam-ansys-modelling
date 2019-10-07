
import os
import numpy as np
import matplotlib.pyplot as plt


class PolynomialFit(object):

    FILENAME = "Power_Data.txt"
    FILENAME_TEMP_INSULATION = "Nodal_Temperature_Last_node.txt"
    DIRECTORY = "C:\\gitlab\\steam-ansys-modelling\\quadrupole_experimental_results"

    @staticmethod
    def create_linear_interpolation_for_temp_vector(time_vector):
        temp_array = PolynomialFit.load_data(directory=PolynomialFit.DIRECTORY, filename=PolynomialFit.FILENAME_TEMP_INSULATION)
        temperature_vector = np.interp(x=time_vector, xp=temp_array[:, 0], fp=temp_array[:, 1])
        return temperature_vector

    @staticmethod
    def extract_meas_power_function():
        """
        Creates array with power deposition fuction with respect to time
        :return: numpy array; column1: time, column2: power [W]
        """
        power = PolynomialFit.load_data(directory=PolynomialFit.DIRECTORY, filename=PolynomialFit.FILENAME)
        time = PolynomialFit.create_time_vector()
        PolynomialFit.plot_data(power, time)
        return PolynomialFit.create_polyfit_array(time, power)

    @staticmethod
    def extract_polynomial_function():
        """
        Created array with interpolation fuction corresponding to power deposition with respect to time
        :return: numpy array; column1: time, column2: power interpolation function [W]
        """
        power = PolynomialFit.load_data(directory=PolynomialFit.DIRECTORY, filename=PolynomialFit.FILENAME)
        time = PolynomialFit.create_time_vector()
        f_polyfit = PolynomialFit.create_polyfit(power, time)
        PolynomialFit().plot_data(power, time, f_fit=f_polyfit)
        return PolynomialFit.create_polyfit_array(time, f_polyfit)

    @staticmethod
    def load_data(directory, filename):
        """
        Loads file with power data from file
        :return: numpy array 1D, column1: power [W]
        """
        os.chdir(directory)
        power_meas = np.loadtxt(filename)
        return power_meas

    @staticmethod
    def create_time_vector():
        """
        Creates time vector
        :return: 1D numpy array
        """
        return np.arange(0.0, 0.0102, 0.0002)

    @staticmethod
    def create_polyfit(power, time):
        """
        Creates polynomial interpolation function
        :param power: power 1D numpy vector
        :param time: time 1D numpy vector
        :return: polynomial function instance
        """
        p = np.polyfit(time, power, deg=8)
        print("Polynomial parameters: ")
        print(p)
        f_fit = np.zeros((len(time)))
        for i in range(len(time)):
            f_fit[i] = p[0] * time[i] ** 8.0 + p[1] * time[i] ** 7.0 + p[2] * time[i] ** 6.0 + \
                       p[3] * time[i] ** 5.0 + p[4] * time[i] ** 4.0 + p[5] * time[i] ** 3.0 + \
                       p[6] * time[i] ** 2.0 + p[7] * time[i] ** 1.0 + p[8]
        return f_fit

    @staticmethod
    def create_polyfit_array(time, p_f):
        """
        Creates power 2D numpy array corresponding to interpolation power function instance
        :param time: numpy 1D time vector
        :param p_f: polynomial function instance
        :return: 2D numpy array, column1:time, column2: interpolated power [W]
        """
        array = np.zeros((len(time), 2))
        for i in range(len(time)):
            array[i, 0] = time[i]
            array[i, 1] = p_f[i]
        return array

    @staticmethod
    def plot_data(power, time, **kwargs):
        """
        Plots power function
        :param power: 1D power vector
        :param time: 1D time vector
        :param kwargs: any other 1D vector that fits the size of time vector
        """
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_xlabel('Time, [s]')
        ax.set_ylabel('Power, [W]')
        ax.plot(time, power, color="b")

        if kwargs is not None:
            for key, value in kwargs.items():
                ax.plot(time, value, color="r")

        plt.grid(True)
        filename = "Polynomial_Power_Fit.png"
        plt.savefig(filename, dpi=200)
        plt.show()
