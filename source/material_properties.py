
import matplotlib.pyplot as plt
import math


class Materials(object):

    def __init__(self):

        self.a0 = 1.7
        self.a1 = 2.33*10.0**9.0
        self.a2 = 9.57*10**5.0
        self.a3 = 163.0
        self.rrr = 150.0

        self.tc0 = 9.2
        self.bc20 = 14.5

        self.cu_dens = 8960     # kg/m3
        self.g10_dens = 1420    # kg/m3
        self.cu_nbti_volume_ratio = 2.2

        self.temp_min = 1       # [K]
        self.temp_max = 100     # [K}
        self.temp_step = 1      # [K]

        self.plot = "no"

    def eq_winding_cu_diameter(self, wire_diameter):
        return (self.cu_nbti_volume_ratio/(1.0+self.cu_nbti_volume_ratio))**0.5 * wire_diameter

    def eq_winding_cu_area(self, wire_diameter):
        return math.pi*(self.eq_winding_cu_diameter(wire_diameter)**2.0)/4.0

    def create_temperature_step(self):
        temperature_step_profile = []
        i = self.temp_min
        while i <= self.temp_max:
            temperature_step_profile.append(i)
            i += self.temp_step
        return temperature_step_profile

    @staticmethod
    def plot_properties(array, y_axis_name):
        left_boundary = array[0, 0]
        right_boundary = array[len(array) - 1, 0]
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_xlabel('Temperature, [K]')
        ax.set_ylabel(y_axis_name)
        plt.xlim(left_boundary, right_boundary)
        ax.plot(array[:, 0], array[:, 1])
        plt.grid(True)
        plt.show()
