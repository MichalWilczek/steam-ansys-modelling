
import math
import numpy as np
import matplotlib.pyplot as plt

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

    @staticmethod
    def plot_properties(array, y_axis_name):
        left_boundary = array[0, 0]
        right_boundary = array[len(array)-1, 0]
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_xlabel('Temperature, [K]')
        ax.set_ylabel(y_axis_name)
        plt.xlim(left_boundary, right_boundary)
        ax.plot(array[:, 0], array[:, 1])
        plt.grid(True)
        plt.show()

    def eq_winding_cu_diameter(self, wire_diameter):
        return (self.cu_nbti_volume_ratio/(1.0+self.cu_nbti_volume_ratio))**0.5 * wire_diameter

    def eq_winding_cu_area(self, wire_diameter):
        return math.pi*(self.eq_winding_cu_diameter(wire_diameter)**2.0)/4.0

    def winding_eq_cp(self, magnetic_field, temperature):
        cu_volume_fraction = self.cu_nbti_volume_ratio/(self.cu_nbti_volume_ratio+1.0)
        # cu_volume_fraction = 0.62263
        cu_cp = self.cu_cp(temperature)
        nbti_cp = self.nb_ti_cp(magnetic_field, temperature)
        winding_eq_cp = (cu_cp+(1.0/cu_volume_fraction-1.0)*nbti_cp)/self.cu_dens
        return winding_eq_cp

    @staticmethod
    def create_temperature_step(temp_min, temp_max, temp_step=1):
        temperature_step_profile = []
        i = temp_min
        while i <= temp_max:
            temperature_step_profile.append(i)
            i += temp_step
        return temperature_step_profile

    def calculate_cu_rho(self, magnetic_field):
        temperature_profile = Materials.create_temperature_step(temp_min=1, temp_max=100)
        cu_rho_array = np.zeros((len(temperature_profile), 2))
        for i in range(len(temperature_profile)):
            cu_rho_array[i, 0] = temperature_profile[i]
            cu_rho_array[i, 1] = self.cu_rho(magnetic_field, temperature=temperature_profile[i])
        self.plot_properties(cu_rho_array, "Cu resistivity, [Ohm*m]")
        return cu_rho_array

    def calculate_cu_thermal_cond(self, magnetic_field):
        temperature_profile = Materials.create_temperature_step(temp_min=1, temp_max=100)
        cu_thermal_cond_array = np.zeros((len(temperature_profile), 2))
        for i in range(len(temperature_profile)):
            cu_thermal_cond_array[i, 0] = temperature_profile[i]
            resistivity = self.cu_rho(magnetic_field, temperature=temperature_profile[i])
            cu_thermal_cond_array[i, 1] = self.cu_thermal_cond(resistivity, temperature_profile[i])
        self.plot_properties(cu_thermal_cond_array, "Cu thermal conductivity, [W/(m*K)]")
        return cu_thermal_cond_array

    def calculate_cu_cp(self):
        temperature_profile = Materials.create_temperature_step(temp_min=1, temp_max=100)
        cu_cp_array = np.zeros((len(temperature_profile), 2))
        for i in range(len(temperature_profile)):
            cu_cp_array[i, 0] = temperature_profile[i]
            cu_cp_array[i, 1] = self.cu_cp(temperature=temperature_profile[i])
        self.plot_properties(cu_cp_array, "Cu cp, [J/(kg*K)]")
        return cu_cp_array

    def calculate_nbti_cp(self, magnetic_field):
        temperature_profile = Materials.create_temperature_step(temp_min=1, temp_max=100)
        nbti_cp_array = np.zeros((len(temperature_profile), 2))
        for i in range(len(temperature_profile)):
            nbti_cp_array[i, 0] = temperature_profile[i]
            nbti_cp_array[i, 1] = self.nb_ti_cp(magnetic_field, temperature=temperature_profile[i])
        self.plot_properties(nbti_cp_array, "NbTi cp, [J/(kg*K)]")
        return nbti_cp_array

    def calculate_winding_eq_cp(self, magnetic_field):
        temperature_profile = Materials.create_temperature_step(temp_min=1, temp_max=100)
        winding_cp_array = np.zeros((len(temperature_profile), 2))
        for i in range(len(temperature_profile)):
            winding_cp_array[i, 0] = temperature_profile[i]
            winding_cp_array[i, 1] = self.winding_eq_cp(magnetic_field, temperature=temperature_profile[i])
        self.plot_properties(winding_cp_array, "Winding equivalent cp, [J/(kg*K)]")
        return winding_cp_array

    def calculate_g10_therm_cond(self):
        temperature_profile = Materials.create_temperature_step(temp_min=1, temp_max=100)
        g10_therm_cond_array = np.zeros((len(temperature_profile), 2))
        for i in range(len(temperature_profile)):
            g10_therm_cond_array[i, 0] = temperature_profile[i]
            g10_therm_cond_array[i, 1] = self.g10_therm_cond(temperature=temperature_profile[i])
        self.plot_properties(g10_therm_cond_array, "G10 thermal conductivity, [W/(m*K)]")
        return g10_therm_cond_array

    def calculate_g10_cp(self):
        temperature_profile = Materials.create_temperature_step(temp_min=1, temp_max=100)
        g10_cp_array = np.zeros((len(temperature_profile), 2))
        for i in range(len(temperature_profile)):
            g10_cp_array[i, 0] = temperature_profile[i]
            g10_cp_array[i, 1] = self.g10_cp(temperature=temperature_profile[i])
        self.plot_properties(g10_cp_array, "G10 Cp, [J/(kg*K)]")
        return g10_cp_array

    # Copper material properties
    def cu_rho(self, magnetic_field, temperature):
        i = temperature
        resistivity = (self.a0/self.rrr+1.0/(self.a1/i**5.0+self.a2/i**3.0+self.a3/i))*10.0**(-8.0)+(0.37+0.0005*self.rrr)*magnetic_field*10.0**(-10.0)
        return resistivity

    @staticmethod
    def cu_thermal_cond(cu_resistivity, temperature):
        i = temperature
        conductivity = 2.45*10.0**(-8.0)*i/cu_resistivity
        return conductivity

    @staticmethod
    def cu_cp(temperature):
        i = temperature
        if i < 10.0:
            a = (-3.080*10.0**(-2.0))*i**4.0
            b = (7.230)*i**3.0
            c = (-2.129)*i**2.0
            d = (1.019*10.0**(2.0))*i
            e = 2.563

        elif i >= 10.0 and i < 40.0:
            a = (-3.045*10.0**(-1.0))*i**4.0
            b = (2.987*10.0**(1.0))*i**3.0
            c = (-4.556*10.0**(2.0))*i**2.0
            d = (3.470*10.0**(3.0))*i
            e = -8.250*10.0**(3.0)

        elif i >= 40.0 and i < 125.0:
            a = (4.190*10.0**(-2.0))*i**4.0
            b = (-1.402*10.0**(1.0))*i**3.0
            c = (1.509*10.0**(3.0))*i**2.0
            d = (-3.160*10.0**(4.0))*i
            e = 1.784*10.0**(5.0)

        elif i >= 125.0 and i < 300.0:
            a = (-8.480*10.0**(-4.0))*i**4.0
            b = (8.419*10.0**(-1.0))*i**3.0
            c = (-3.255*10.0**(2.0))*i**2.0
            d = (6.059*10.0**(4.0))*i
            e = -1.290*10.0**(6.0)

        elif i >= 300.0 and i < 500.0:
            a = (-4.800*10.0**(-5.0))*i**4.0
            b = (9.173*10.0**(-2.0))*i**3.0
            c = (-6.412*10.0**(1.0))*i**2.0
            d = (2.036*10.0**(4.0))*i
            e = 1.030*10.0**(6.0)

        else:
            a = 0.000*i**4
            b = (1.200*10.0**(-5.0))*i**3.0
            c = (-2.149*10.0**(-1.0))*i**2.0
            d = (1.004*10.0**3.0)*i
            e = 3.180*10.0**6.0

        cu_cp = a+b+c+d+e
        return cu_cp

    # NiTi material properties
    def nb_ti_cp(self, magnetic_field, temperature):
        i = temperature
        tc = self.tc0*(1.0-magnetic_field/self.bc20)**0.59
        if i < tc:
            a = 0.0
            b = (4.91000*10.0**(1.0)) * i ** 3.0
            c = 0.0
            d = (6.40000*10.0**(1.0)) * i
            e = 0.0

        elif i >= tc and i < 20.0:
            a = 0.0
            b = (1.62400*10.0**(1.0)) * i ** 3.0
            c = 0.0
            d = (9.28000*10.0**(2.0)) * i
            e = 0.0

        elif i >= 20.0 and i < 50.0:
            a = (-2.17700*10.0**(-1.0)) * i ** 4.0
            b = (1.19838*10.0**(1.0)) * i ** 3.0
            c = (5.53710*10.0**(2.0)) * i ** 2.0
            d = (-7.84610*10.0**(3.0)) * i
            e = 4.13830*10.0**(4.0)

        elif i >= 50.0 and i < 175.0:
            a = (-4.82000*10.0**(-3.0)) * i ** 4.0
            b = (2.97600) * i ** 3.0
            c = (-7.16300*10.0**(2.0)) * i ** 2.0
            d = (8.30220*10.0**(4.0)) * i
            e = -1.53000*10.0**(6.0)

        elif i >= 175.0 and i < 500.0:
            a = (-6.29000*10.0**(-5.0)) * i ** 4.0
            b = (9.29600*10.0**(-2.0)) * i ** 3.0
            c = (-5.16600*10.0**(1.0)) * i ** 2.0
            d = (1.37060*10.0**(4.0)) * i
            e = 1.24000*10.0**(6.0)

        else:
            a = 0.00000 * i ** 4.0
            b = 0.00000 * i ** 3.0
            c = (-2.57000*10.0**(-1.0)) * i ** 2.0
            d = (9.55500*10.0**2.0) * i
            e = 2.45000*10.0**6.0

        nb_ti_cp = a + b + c + d + e
        return nb_ti_cp

    # G10 material properties
    def g10_therm_cond(self, temperature):
        a0 = -4.1236
        a1 = 13.788
        a2 = -26.068
        a3 = 26.272
        a4 = -14.663
        a5 = 4.4954
        a6 = -0.6905
        a7 = 0.0397
        log_T = math.log10(temperature)
        f_exp = a0 + a1*log_T + a2*log_T**2.0 + a3*log_T**3.0 + a4*log_T**4.0 + a5*log_T**5.0 + a6*log_T**6.0 + a7*log_T**7
        g10_therm_cond = 10.0**f_exp
        return g10_therm_cond

    def g10_cp(self, temperature):
        a = -2.4083
        b = 7.6006
        c = -8.2982
        d = 7.3301
        e = -4.2386
        f = 1.4294
        g = -0.24396
        h = 0.015236
        i = 0.0
        log_T = math.log10(temperature)
        f_exp = a + b*log_T + c*log_T**2.0 + d*log_T**3.0 + e*log_T**4.0 + f*log_T**5.0 + g*log_T**6.0 + h*log_T**7.0 + i*log_T**8.0
        g10_cp = 10.0**f_exp
        return g10_cp

Materials = Materials()
Materials.calculate_cu_rho(2.88)
Materials.calculate_cu_thermal_cond(magnetic_field=2.88)

Materials.calculate_winding_eq_cp(magnetic_field=2.88)
Materials.calculate_g10_therm_cond()
Materials.calculate_g10_cp()