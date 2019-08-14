
import matplotlib.pyplot as plt
import math


class Materials(object):

    material_properties_directory = "C:\\gitlab\\steam-ansys-modelling\\source\\Material_Properties"

    a0 = 1.7
    a1 = 2.33 * 10.0 ** 9.0
    a2 = 9.57 * 10 ** 5.0
    a3 = 163.0
    rrr = 100.0
    tc0 = 9.2
    bc20 = 14.5

    cu_dens = 8960.0      # kg/m3
    # cu_dens = 1.0  # kg/m3
    nb_ti_dens = 6000.0   # kg/m3
    # nb_ti_dens = 1.0  # kg/m3
    g10_dens = 1420.0     # kg/m3
    f_cu_f_nbti = 2.2

    temp_min = 1        # [K]
    temp_max = 300      # [K}
    temp_step = 0.01       # [K]

    def __init__(self, plotting="no"):

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
        return fig
