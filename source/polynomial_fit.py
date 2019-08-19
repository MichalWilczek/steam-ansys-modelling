
import os
import numpy as np
import matplotlib.pyplot as plt


class Polynomials(object):

    FILENAME = "Power_Data.txt"
    DIRECTORY = "C:\\gitlab\\steam-ansys-modelling\\quadrupole_experimental_results"

    @staticmethod
    def extract_polynomial_function():
        power = Polynomials.load_power_data()
        time = Polynomials.create_time_vector()
        f_polyfit = Polynomials.create_polyfit(power, time)
        Polynomials.plot_data(power, time, f_polyfit)
        return Polynomials.create_polyfit_array(time, f_polyfit)

    @staticmethod
    def load_power_data():
        """
        Loads file with magnetic field from file
        :return: numpy array 2D
        """
        os.chdir(Polynomials.DIRECTORY)
        power_meas = np.loadtxt(Polynomials.FILENAME)
        return power_meas

    @staticmethod
    def create_time_vector():
        return np.arange(0.0, 0.0102, 0.0002)

    @staticmethod
    def create_polyfit(power, time):
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
        array = np.zeros((len(time), 2))
        for i in range(len(time)):
            array[i, 0] = time[i]
            array[i, 1] = p_f[i]
        return array

    @staticmethod
    def plot_data(power, time, f_fit):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_xlabel('Time, [s]')
        ax.set_ylabel('Power, [W]')
        ax.plot(time, power, color="b")
        ax.plot(time, f_fit, color="r")
        plt.grid(True)
        filename = "Polynomial_Power_Fit.png"
        plt.savefig(filename, dpi=200)
        plt.show()


