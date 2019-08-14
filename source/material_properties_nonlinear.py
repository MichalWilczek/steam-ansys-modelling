
import math
import numpy as np
import os
from source.material_properties import Materials

class MaterialsNonLinear(Materials):

    def __init__(self, plot_curves="no", plotting="no"):
        os.chdir(self.material_properties_directory)
        super().__init__(plotting)
        if plot_curves == "yes":
            self.plot_cu_resistivity(rrr=50.0)
            self.plot_cu_resistivity(rrr=150.0)
            self.plot_cu_thermal_cond(rrr=100.0)
            self.plot_cu_thermal_cond(rrr=150.0)
            self.plot_nb_ti_cp()

    def plot_cu_resistivity(self, rrr):
        magnetic_field = [0.0, 3.0]
        for i in range(len(magnetic_field)):
            cu_rho = self.calculate_cu_rho(magnetic_field[i], rrr=rrr)
            left_boundary = cu_rho[0, 0]
            right_boundary = cu_rho[len(cu_rho) - 1, 0]
            if i == 0:
                self.cu_res_fig = self.plt.figure()
                self.cu_res_plot = self.cu_res_fig.add_subplot(111)
                self.cu_res_plot.set_xlabel("Temperature, [K]")
                self.cu_res_plot.set_ylabel("Cu resistivity, [Ohm*m]")
                self.plt.ylim(0.0, 2.0*10**(-8.0))
                self.plt.xlim(left_boundary, right_boundary)
                self.cu_res_plot.plot(cu_rho[:, 0], cu_rho[:, 1])
                self.plt.grid(True)
            else:
                self.cu_res_plot.plot(cu_rho[:, 0], cu_rho[:, 1])
        self.plt.legend(("B = {} [T]".format(magnetic_field[0]), "B = {} [T]".format(magnetic_field[1])), loc="upper right")
        filename = "Cu_Rho_B_Depenedence_plot_rrr_{}.png".format(int(rrr))
        self.cu_res_fig.savefig(filename, dpi=200)

    def plot_cu_thermal_cond(self, rrr):
        magnetic_field = [0.0, 5.0, 10.0]
        for i in range(len(magnetic_field)):
            cu_k = self.calculate_cu_thermal_cond(magnetic_field[i], rrr=rrr)
            left_boundary = cu_k[0, 0]
            right_boundary = cu_k[len(cu_k) - 1, 0]
            if i == 0:
                self.cu_res_fig = self.plt.figure()
                self.cu_res_plot = self.cu_res_fig.add_subplot(111)
                self.cu_res_plot.set_xlabel("Temperature, [K]")
                self.cu_res_plot.set_ylabel("Cu thermal conductivity, [W/(m*K)]")
                self.plt.ylim(0.0, 5000.0)
                self.plt.xlim(left_boundary, right_boundary)
                self.cu_res_plot.plot(cu_k[:, 0], cu_k[:, 1])
                self.plt.grid(True)
            else:
                self.cu_res_plot.plot(cu_k[:, 0], cu_k[:, 1])
        self.plt.legend(("B = {} [T]".format(magnetic_field[0]), "B = {} [T]".format(magnetic_field[1]),
                         "B = {} [T]".format(magnetic_field[2])), loc="upper right")
        filename = "Cu_k_B_Depenedence_plot_rrr_{}.png".format(int(rrr))
        self.cu_res_fig.savefig(filename, dpi=200)

    def plot_nb_ti_cp(self):
        magnetic_field = [0.0, 3.0]
        for i in range(len(magnetic_field)):
            nbti_cp = self.calculate_nbti_cp(magnetic_field[i])
            left_boundary = nbti_cp[0, 0]
            right_boundary = nbti_cp[len(nbti_cp) - 1, 0]
            if i == 0:
                self.cu_res_fig = self.plt.figure()
                self.cu_res_plot = self.cu_res_fig.add_subplot(111)
                self.cu_res_plot.set_xlabel("Temperature, [K]")
                self.cu_res_plot.set_ylabel("Nb-Ti Cp, [J/(kg*K)]")
                self.plt.xlim(left_boundary, right_boundary)
                self.cu_res_plot.plot(nbti_cp[:, 0], nbti_cp[:, 1])
                self.plt.grid(True)
            else:
                self.cu_res_plot.plot(nbti_cp[:, 0], nbti_cp[:, 1])
        self.plt.legend(("B = {} [T]".format(magnetic_field[0]), "B = {} [T]".format(magnetic_field[1])), loc="upper right")
        filename = "NbTi_Cp_B_Depenedence_plot.png"
        self.cu_res_fig.savefig(filename, dpi=200)

    def calculate_cu_rho(self, magnetic_field, rrr):
        temperature_profile = self.create_temperature_step()
        cu_rho_array = np.zeros((len(temperature_profile), 2))
        for i in range(len(temperature_profile)):
            cu_rho_array[i, 0] = temperature_profile[i]
            cu_rho_array[i, 1] = self.cu_rho(magnetic_field, temperature=temperature_profile[i], rrr=rrr)
        if self.plot == "yes":
            self.plot_properties(cu_rho_array, "Cu resistivity, [Ohm*m]")
        return cu_rho_array

    def calculate_cu_thermal_cond(self, magnetic_field, rrr):
        temperature_profile = self.create_temperature_step()
        cu_thermal_cond_array = np.zeros((len(temperature_profile), 2))
        for i in range(len(temperature_profile)):
            cu_thermal_cond_array[i, 0] = temperature_profile[i]
            resistivity = self.cu_rho(magnetic_field, temperature=temperature_profile[i], rrr=rrr)
            cu_thermal_cond_array[i, 1] = self.cu_thermal_cond(resistivity, temperature_profile[i])
        if self.plot == "yes":
            self.plot_properties(cu_thermal_cond_array, "Cu thermal conductivity, [W/(m*K)]")
        return cu_thermal_cond_array

    def calculate_cu_cp(self):
        temperature_profile = self.create_temperature_step()
        cu_cp_array = np.zeros((len(temperature_profile), 2))
        for i in range(len(temperature_profile)):
            cu_cp_array[i, 0] = temperature_profile[i]
            cu_cp_array[i, 1] = self.cu_cp(temperature=temperature_profile[i])
        if self.plot == "yes":
            fig = self.plot_properties(cu_cp_array, "Cu Cp, [J/(kg*K)]")
            filename = "Cu_Cp_plot.png"
            fig.savefig(filename, dpi=200)
        return cu_cp_array

    def calculate_nbti_cp(self, magnetic_field):
        temperature_profile = self.create_temperature_step()
        nbti_cp_array = np.zeros((len(temperature_profile), 2))
        for i in range(len(temperature_profile)):
            nbti_cp_array[i, 0] = temperature_profile[i]
            nbti_cp_array[i, 1] = self.nb_ti_cp(magnetic_field, temperature=temperature_profile[i])
        if self.plot == "yes":
            self.plot_properties(nbti_cp_array, "Nb-Ti Cp, [J/(kg*K)]")
        return nbti_cp_array

    def calculate_winding_eq_cp(self, magnetic_field):
        temperature_profile = self.create_temperature_step()
        winding_cp_array = np.zeros((len(temperature_profile), 2))
        for i in range(len(temperature_profile)):
            winding_cp_array[i, 0] = temperature_profile[i]
            winding_cp_array[i, 1] = self.winding_eq_cp(magnetic_field, temperature=temperature_profile[i])
        if self.plot == "yes":
            fig = self.plot_properties(winding_cp_array, "Winding equivalent Cp, [J/(kg*K)]")
            filename = "Eq_Cp_plot.png"
            fig.savefig(filename, dpi=200)
        return winding_cp_array

    def calculate_g10_therm_cond(self):
        temperature_profile = self.create_temperature_step()
        g10_therm_cond_array = np.zeros((len(temperature_profile), 2))
        for i in range(len(temperature_profile)):
            g10_therm_cond_array[i, 0] = temperature_profile[i]
            g10_therm_cond_array[i, 1] = self.g10_therm_cond(temperature=temperature_profile[i])
        if self.plot == "yes":
            fig = self.plot_properties(g10_therm_cond_array, "G10 thermal conductivity, [W/(m*K)]")
            filename = "G10_k_plot.png"
            fig.savefig(filename, dpi=200)
        return g10_therm_cond_array

    def calculate_g10_cp(self):
        temperature_profile = self.create_temperature_step()
        g10_cp_array = np.zeros((len(temperature_profile), 2))
        for i in range(len(temperature_profile)):
            g10_cp_array[i, 0] = temperature_profile[i]
            g10_cp_array[i, 1] = self.g10_cp(temperature=temperature_profile[i])
        if self.plot == "yes":
            fig = self.plot_properties(g10_cp_array, "G10 Cp, [J/(kg*K)]")
            filename = "G10_Cp_plot.png"
            fig.savefig(filename, dpi=200)
        return g10_cp_array

    # Copper material properties
    def cu_rho(self, magnetic_field, temperature, rrr):
        i = temperature
        resistivity = (self.a0 / rrr + 1.0 / (self.a1 / i ** 5.0 + self.a2 / i ** 3.0 + self.a3 / i)) * 10.0 ** (-8.0) + (0.37 + 0.0005 * rrr) * magnetic_field * 10.0 ** (-10.0)
        return resistivity

    def winding_eq_cp(self, magnetic_field, temperature):
        cu_cp = self.cu_cp(temperature)
        nbti_cp = self.nb_ti_cp(magnetic_field, temperature)
        winding_eq_cp = self.f_cu*cu_cp + self.f_nbti*nbti_cp
        return winding_eq_cp

    @staticmethod
    def cu_thermal_cond(cu_resistivity, temperature):
        i = temperature
        conductivity = 2.45*10.0**(-8.0)*i/cu_resistivity
        return conductivity

    def cu_cp(self, temperature):
        i = temperature
        if i < 10.0:
            a = (-3.080*10.0**(-2.0))*i**4.0
            b = 7.230*i**3.0
            c = (-2.129)*i**2.0
            d = (1.019*10.0**(2.0))*i
            e = 2.563

        elif 10.0 <= i < 40.0:
            a = (-3.045*10.0**(-1.0))*i**4.0
            b = (2.987*10.0**(1.0))*i**3.0
            c = (-4.556*10.0**(2.0))*i**2.0
            d = (3.470*10.0**(3.0))*i
            e = -8.250*10.0**(3.0)

        elif 40.0 <= i < 125.0:
            a = (4.190*10.0**(-2.0))*i**4.0
            b = (-1.402*10.0**(1.0))*i**3.0
            c = (1.509*10.0**(3.0))*i**2.0
            d = (-3.160*10.0**(4.0))*i
            e = 1.784*10.0**(5.0)

        elif 125.0 <= i < 300.0:
            a = (-8.480*10.0**(-4.0))*i**4.0
            b = (8.419*10.0**(-1.0))*i**3.0
            c = (-3.255*10.0**(2.0))*i**2.0
            d = (6.059*10.0**(4.0))*i
            e = -1.290*10.0**(6.0)

        elif 300.0 <= i < 500.0:
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

        cu_cp = (a+b+c+d+e)/self.cu_dens
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
        elif tc <= i < 20.0:
            a = 0.0
            b = (1.62400*10.0**(1.0)) * i ** 3.0
            c = 0.0
            d = (9.28000*10.0**(2.0)) * i
            e = 0.0
        elif 20.0 <= i < 50.0:
            a = (-2.17700*10.0**(-1.0)) * i ** 4.0
            b = (1.19838*10.0**(1.0)) * i ** 3.0
            c = (5.53710*10.0**(2.0)) * i ** 2.0
            d = (-7.84610*10.0**(3.0)) * i
            e = 4.13830*10.0**(4.0)
        elif 50.0 <= i < 175.0:
            a = (-4.82000*10.0**(-3.0)) * i ** 4.0
            b = (2.97600) * i ** 3.0
            c = (-7.16300*10.0**(2.0)) * i ** 2.0
            d = (8.30220*10.0**(4.0)) * i
            e = -1.53000*10.0**(6.0)
        elif 175.0 <= i < 500.0:
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

        nb_ti_cp = (a+b+c+d+e)/self.nb_ti_dens
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

# MaterialsNonLinear(plot_curves="yes")
# Materials = MaterialsNonLinear(plotting="yes")
# Materials.calculate_cu_cp()
# Materials.calculate_g10_therm_cond()
# Materials.calculate_g10_cp()
# Materials.calculate_winding_eq_cp(magnetic_field=3.0)