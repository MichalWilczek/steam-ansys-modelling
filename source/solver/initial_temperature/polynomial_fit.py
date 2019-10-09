
import os
import numpy as np
import matplotlib.pyplot as plt

# TO BE MODIFIED !!! CAUSE IT IS NOT WORKING AT THE MOMENT

class PolynomialFit(object):

    def __init__(self, factory, input_filename):
        self.input_data = factory.input_data
        self.input_directory = factory.input_directory
        self.time_function_filename = input_filename

    def create_linear_interpolation_array(self):
        os.chdir(self.input_directory)
        array = np.loadtxt(self.time_function_filename)
        interpolation_vector = np.interp(x=array[:, 0], xp=array[:, 1], fp=array[:, 1])
        return interpolation_vector

    def extract_meas_power_function(self):
        """
        Creates array with power deposition fuction with respect to time
        :return: numpy array; column1: time, column2: power [W]
        """
        power = PolynomialFit.load_data(directory=self.input_directory, filename=PolynomialFit.FILENAME)
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
    def create_polyfit(function, time):
        """
        Creates polynomial interpolation function
        :param power: power 1D numpy vector
        :param time: time 1D numpy vector
        :return: polynomial function instance
        """
        p = np.polyfit(time, function, deg=8)
        print("Polynomial parameters: \n {}".format(p))
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

