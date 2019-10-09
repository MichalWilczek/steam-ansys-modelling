
from source.factory.general_functions import GeneralFunctions
import matplotlib.pyplot as plt
from matplotlib import rc
import math
import os


class Materials(GeneralFunctions):

    a0 = 1.7
    a1 = 2.33 * 10.0 ** 9.0
    a2 = 9.57 * 10 ** 5.0
    a3 = 163.0
    tc0 = 9.2
    bc20 = 14.5

    c1 = 3449.0
    c2 = -257.0

    cu_dens = 8960.0      # kg/m3, room temperature of copper
    nb_ti_dens = 6000.0   # kg/m3
    g10_dens = 1948.0     # kg/m3
    # cu_dens = 1.0      # kg/m3, room temperature of copper
    # nb_ti_dens = 1.0   # kg/m3
    # g10_dens = 1.0     # kg/m3

    temp_min = 1  # [K]
    temp_max = 300  # [K}
    temp_step = 3.5  # [K]

    def __init__(self, factory, plotting="no"):
        """
        Initialises plot creation if plotting is set to "yes"
        :param plotting: string, default as "no"
        """
        self.output_directory = factory.output_directory
        self.output_directory_materials = GeneralFunctions.create_folder_in_directory(self.output_directory, "mat_props")
        self.input_data = factory.input_data
        self.f_cu_f_nbti = self.input_data.material_settings.input.f_cu_f_nbti
        self.plt = plt
        self.plot = plotting
        self.f_nbti = self.ratio_nbti()
        self.f_cu = self.ratio_cu()

    def ratio_nbti(self):
        return 1.0/(1.0+self.f_cu_f_nbti)

    def ratio_cu(self):
        return 1.0 - self.ratio_nbti()

    def wire_area(self, wire_diameter):
        return math.pi/4.0 * (wire_diameter**2.0)

    def reduced_wire_area(self, wire_diameter):
        return self.wire_area(wire_diameter) * self.f_cu

    def reduced_wire_diameter(self, wire_diameter):
        return (4.0*self.reduced_wire_area(wire_diameter)/math.pi)**0.5

    def calculate_critical_temperature(self, magnetic_field):
        """
        :param magnetic_field: magnetic field strength as float
        :return: critical temperature as float
        """
        critical_temperature_0 = self.tc0              # [K]
        critical_magnetic_field_0 = self.bc20          # [T]
        critical_temperature = critical_temperature_0*(1.0-magnetic_field/critical_magnetic_field_0)**0.59
        return critical_temperature

    @staticmethod
    def create_temperature_step(temp_min, temp_max, temp_step):
        """
        Creates temperature values to be input in all material properties functions
        :param temp_min: minimum temperature as integer
        :param temp_max: maximum temperature as integer
        :param temp_step: temperature step as integer
        :return: list of temperature steps
        """
        temperature_step_profile = []
        i = temp_min
        while i <= temp_max:
            temperature_step_profile.append(i)
            i += temp_step
        return temperature_step_profile

    @staticmethod
    def plot_properties(array, y_axis_name, x_axis_name='temperature, ' + r'[K]', fontsize=15):
        """
        Plots material properties
        :param array: numpy array to be plotted; 1st column: x values as float, 2nd column: y values as float
        :param y_axis_name: y-axis name as string
        :param x_axis_name: x-axis name as string set default as 'Temperature, [K]'
        :return: instance with figure
        """
        left_boundary = array[0, 0]
        right_boundary = array[len(array) - 1, 0]
        fig = plt.figure()
        # plt.rc('text', usetex=True)
        ax = fig.add_subplot(111)
        ax.set_xlabel(x_axis_name, fontsize=fontsize)
        ax.set_ylabel(y_axis_name, fontsize=fontsize)
        plt.xlim(left_boundary, right_boundary)
        ax.plot(array[:, 0], array[:, 1])
        plt.grid(True)
        # plt.rcParams()

        # plt.rc('font', family='serif')
        plt.show()
        # plt.savefig("tex_demo")
        return fig
