
import math
import numpy as np
import os
from source.material_properties import Materials

class MaterialsNonLinear(Materials):

    def __init__(self, plot_curves="no", plotting="no"):
        os.chdir(self.material_properties_directory)
        self.plot_curves = plot_curves
        super().__init__(plotting)
        if self.plot_curves == "yes":
            self.plot_cu_resistivity(rrr=50.0)
            self.plot_cu_resistivity(rrr=150.0)
            self.plot_cu_thermal_cond(rrr=50.0)
            self.plot_cu_thermal_cond(rrr=150.0)
            self.plot_nb_ti_cp()

    def plot_cu_resistivity(self, rrr):
        """
        Plots copper resistivity for two values of magnetic field strength
        :param rrr: residual resistivity ratio as float
        """
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
        """
        Plots copper thermal conductivity for three values of magnetic field strength
        :param rrr: residual resistivity ratio as float
        """
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
                self.plt.ylim(0.0, 4000.0)
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
        """
        Plots niobium titanium specific heat capacity for two values of magnetic field strength
        """
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
        """
        Returns copper resistivity array, plots the data if "plotting" instance is set to "yes"
        :param magnetic_field: magnetic field strength as float
        :param rrr: residual resistivity ratio as float
        :return: numpy array; 1st column temperature as float, 2nd column: resistivity as float
        """
        temperature_profile = self.create_temperature_step(temp_max=self.temp_max, temp_min=self.temp_min, temp_step=self.temp_step)
        cu_rho_array = np.zeros((len(temperature_profile), 2))
        for i in range(len(temperature_profile)):
            cu_rho_array[i, 0] = temperature_profile[i]
            cu_rho_array[i, 1] = self.cu_rho_nist(magnetic_field, temperature=temperature_profile[i], rrr=rrr)
        if self.plot == "yes":
            self.plot_properties(cu_rho_array, "Cu resistivity, [Ohm*m]")
        return cu_rho_array

    def calculate_cu_thermal_cond(self, magnetic_field, rrr):
        """
        Returns copper thermal conductivity array, plots the data if "plotting" instance is set to "yes"
        :param magnetic_field: magnetic field strength as float
        :param rrr: residual resistivity ratio as float
        :return: numpy array; 1st column temperature as float, 2nd column: thermal conductivity as float
        """
        temperature_profile = self.create_temperature_step(temp_max=self.temp_max, temp_min=self.temp_min, temp_step=self.temp_step)
        cu_thermal_cond_array = np.zeros((len(temperature_profile), 2))
        for i in range(len(temperature_profile)):
            cu_thermal_cond_array[i, 0] = temperature_profile[i]
            cu_thermal_cond_array[i, 1] = self.cu_thermal_cond_nist(magnetic_field=magnetic_field, temperature=temperature_profile[i], rrr=rrr)
        if self.plot == "yes":
            self.plot_properties(cu_thermal_cond_array, "Cu thermal conductivity, [W/(m*K)]")
        return cu_thermal_cond_array

    def calculate_cu_cp(self):
        """
        Returns copper specific heat capacity array, plots the data if "plotting" instance is set to "yes"
        :return: numpy array; 1st column temperature as float, 2nd column: spec. heat capacity as float
        """
        temperature_profile = self.create_temperature_step(temp_max=self.temp_max, temp_min=self.temp_min, temp_step=self.temp_step)
        cu_cp_array = np.zeros((len(temperature_profile), 2))
        for i in range(len(temperature_profile)):
            cu_cp_array[i, 0] = temperature_profile[i]
            cu_cp_array[i, 1] = self.cu_cp_nist(temperature=temperature_profile[i])
        if self.plot == "yes":
            fig = self.plot_properties(cu_cp_array, "Cu Cp, [J/(kg*K)]")
            filename = "Cu_Cp_plot.png"
            fig.savefig(filename, dpi=200)
        return cu_cp_array

    def calculate_nbti_cp(self, magnetic_field):
        """
        Returns nb-ti specific heat capacity array, plots the data if "plotting" instance is set to "yes"
        :param magnetic_field: magnetic field strength as float
        :return: numpy array; 1st column temperature as float, 2nd column: spec. heat capacity as float
        """
        temperature_profile = self.create_temperature_step(temp_max=self.temp_max, temp_min=self.temp_min, temp_step=self.temp_step)
        nbti_cp_array = np.zeros((len(temperature_profile), 2))
        for i in range(len(temperature_profile)):
            nbti_cp_array[i, 0] = temperature_profile[i]
            nbti_cp_array[i, 1] = self.nb_ti_cp_cudi(magnetic_field, temperature=temperature_profile[i])
        if self.plot == "yes":
            self.plot_properties(nbti_cp_array, "Nb-Ti Cp, [J/(kg*K)]")
        return nbti_cp_array

    def calculate_winding_eq_cp(self, magnetic_field):
        """
        Returns strand equivalent specific heat capacity array, plots the data if "plotting" instance is set to "yes"
        :param magnetic_field: magnetic field strength as float
        :return: numpy array; 1st column temperature as float, 2nd column: spec. heat capacity as float
        """
        temperature_profile = self.create_temperature_step(temp_max=self.temp_max, temp_min=self.temp_min, temp_step=self.temp_step)
        winding_cp_array = np.zeros((len(temperature_profile), 2))
        for i in range(len(temperature_profile)):
            winding_cp_array[i, 0] = temperature_profile[i]
            winding_cp_array[i, 1] = self.winding_eq_cp(magnetic_field, temperature=temperature_profile[i])
        if self.plot == "yes":
            fig = self.plot_properties(winding_cp_array, "Winding equivalent Cp, [J/(kg*K)]")
            filename = "Eq_Cp_plot.png"
            fig.savefig(filename, dpi=200)
        return winding_cp_array

    def winding_eq_cp(self, magnetic_field, temperature):
        """
        Calculates strand equivalent specific heat capacity
        :param magnetic_field: magnetic field strength as float
        :param temperature: temperature as float
        :return: specific heat capacity as float
        """
        cu_cp = self.cu_cp_nist(temperature)
        nbti_cp = self.nb_ti_cp_cudi(magnetic_field, temperature)
        winding_eq_cp = self.f_cu*cu_cp + self.f_nbti*nbti_cp
        return winding_eq_cp

    def calculate_g10_therm_cond(self):
        """
        Returns G10 thermal conductivity array, plots the data if "plotting" instance is set to "yes"
        :return: numpy array; 1st column temperature as float, 2nd column: thermal conductivity as float
        """
        temperature_profile = self.create_temperature_step(temp_max=self.temp_max, temp_min=self.temp_min, temp_step=self.temp_step)
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
        """
        Returns G10 specific heat capacity array, plots the data if "plotting" instance is set to "yes"
        :return: numpy array; 1st column temperature as float, 2nd column: spec. heat capacity as float
        """
        temperature_profile = self.create_temperature_step(temp_max=self.temp_max, temp_min=self.temp_min, temp_step=self.temp_step)
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
    @staticmethod
    def cu_rho_nist(magnetic_field, temperature, rrr):
        temp = temperature
        # Constants
        c0 = 1.553*10.0**(-8.0)  # (for RRR = 100 = R_273 / R_4)
        p1 = 1.171*10.0**(-17.0)
        p2 = 4.49
        p3 = 3.841*10.0**10.0
        p4 = 1.14
        p5 = 50.0
        p6 = 6.428
        p7 = 0.4531
        a0 = -2.662
        a1 = 0.3168
        a2 = 0.6229
        a3 = -0.1839
        a4 = 0.01827

        rho_0 = c0 / rrr
        rho_i = p1 * temp**p2 / (1.0 + p1*p3*temp**(p2-p4) * math.e**(-(p5/temp)**p6))
        rho_i0 = p7 * rho_i * rho_0 / (rho_i + rho_0)
        rho_n = rho_0 + rho_i + rho_i0

        if magnetic_field > 0.01:
            x = c0 * magnetic_field / rho_n
            log_x = math.log10(x)
            f_exp = a0 + a1 * log_x + a2 * log_x**2.0 + a3 * log_x**3.0 + a4 * log_x**4.0
            corr = 10.0**f_exp
        else:
            corr = 0.0
        resistivity = rho_n*(1+corr)
        return resistivity

    def cu_thermal_cond_nist(self, magnetic_field, temperature, rrr):
        temp = temperature
        beta = 0.634 / rrr
        beta_r = beta / (3.0*10.0**(-4.0))
        p1 = 1.754*10.0**(-8.0)
        p2 = 2.763
        p3 = 1102.0
        p4 = -0.165
        p5 = 70.0
        p6 = 1.756
        p7 = 0.838 / (beta_r**0.1661)
        w_0 = beta / temp
        w_i = p1 * temp**p2 / (1.0 + p1 * p3 * temp**(p2 + p4) * math.e**(-(p5/temp)**p6))
        w_i0 = p7 * (w_i * w_0) / (w_i + w_0)
        k_n = 1.0 / (w_0 + w_i + w_i0)
        cond = k_n * (self.cu_rho_nist(magnetic_field=0.0, temperature=temp, rrr=rrr) /
                      self.cu_rho_nist(magnetic_field=magnetic_field, temperature=temp, rrr=rrr))
        return cond

    @staticmethod
    def cu_cp_nist(temperature):
        temp = temperature
        a = -1.91844
        b = -0.15973
        c = 8.61013
        d = -18.996
        e = 21.9661
        f = -12.7328
        g = 3.54322
        h = -0.3797
        log_t = math.log10(temp)
        f_exp = a + b*log_t**1.0 + c*log_t**2.0 + d*log_t**3.0 + e*log_t**4.0 + f*log_t**5.0 + g*log_t**6.0 + h*log_t**7.0
        cp = 10.0**f_exp
        return cp

    # niobium titanium material properties
    def nb_ti_cp_cudi(self, magnetic_field, temperature):
        i = temperature
        tc = self.tc0*(1.0-magnetic_field/self.bc20)**0.59
        if i < tc:
            a0 = 0.0
            a1 = 64.0*magnetic_field
            a2 = 0.0
            a3 = 49.1
            a4 = 0.0
        elif tc <= i < 28.358:
            a0 = 0
            a1 = 928.0
            a2 = 0.0
            a3 = 16.24
            a4 = 0.0
        elif 28.358 <= i < 50.99:
            a0 = 41383.0
            a1 = -7846.1
            a2 = 553.71
            a3 = 11.9838
            a4 = -0.2177
        elif 50.99 <= i < 165.8:
            a0 = -1.53*10.0**6.0
            a1 = 83022.0
            a2 = -716.3
            a3 = 2.976
            a4 = -0.00482
        elif 165.8 <= i < 496.54:
            a0 = 1.24*10.0**6.0
            a1 = 13706.0
            a2 = -51.66
            a3 = 0.09296
            a4 = -6.29*10.0**(-5.0)
        else:
            a0 = 2.45*10.0**6.0
            a1 = 955.5
            a2 = -0.257
            a3 = 0.0
            a4 = 0.0
        cv = a0 + a1*i + a2*i**2.0 + a3*i**3.0 + a4*i**4.0
        return cv / self.nb_ti_dens

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
        log_t = math.log10(temperature)
        f_exp = a0 + a1*log_t + a2*log_t**2.0 + a3*log_t**3.0 + a4*log_t**4.0 + a5*log_t**5.0 + a6*log_t**6.0 + a7*log_t**7
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
        log_t = math.log10(temperature)
        f_exp = a + b*log_t + c*log_t**2.0 + d*log_t**3.0 + e*log_t**4.0 + f*log_t**5.0 + g*log_t**6.0 + \
                h*log_t**7.0 + i*log_t**8.0
        g10_cp = 10.0**f_exp
        return g10_cp

    # here I need to add comments as soon as I finish analyses!!!
    def calculate_current_in_copper_matrix(self, temperature, magnetic_field, current, init_temperature):
        temp_critic = self.calculate_critical_temperature(magnetic_field)
        temp_cs = self.calculate_temperature_cs(temp_critic, current, magnetic_field)
        ic = self.calculate_critical_current_ic(current, temperature, temp_critic, temp_cs)
        if temperature < temp_cs:
            return 0.0
        elif temp_cs <= temperature < temp_critic:
            return current - ic
        else:
            return current

    def calculate_critical_current_ic(self, current, temperature, critical_temperature, temp_cs):
        return current*(temperature-temp_cs)/(critical_temperature-temp_cs)

    def calculate_temperature_cs(self, critical_temperature, current, magnetic_field):
        return critical_temperature*(1.0-current/(self.c1+self.c2*magnetic_field))

    def calculate_joule_heating(self, magnetic_field, wire_diameter, current, temperature):
        temp_critic = self.calculate_critical_temperature(magnetic_field)
        temp_cs = self.calculate_temperature_cs(temp_critic, current, magnetic_field)
        reduced_area = self.reduced_wire_area(wire_diameter)*0.000001
        ic = self.calculate_critical_current_ic(current, temperature, temp_critic, temp_cs)
        cu_rho = self.cu_rho_nist(magnetic_field, temperature, rrr=self.rrr)

        if temperature < temp_cs:
            return 0.0
        elif temp_cs <= temperature < temp_critic:
            return cu_rho*(current-ic)**2.0/(reduced_area**2.0)
        else:
            return cu_rho*current**2.0/(reduced_area**2.0)

    def create_heat_gen_profile(self, magnetic_field, wire_diameter, current):
        temperature_profile = self.create_temperature_step(temp_max=200, temp_min=1, temp_step=0.1)
        heat_gen_array = np.zeros((len(temperature_profile), 2))
        for i in range(len(temperature_profile)):
            heat_gen_array[i, 0] = temperature_profile[i]
            heat_gen_array[i, 1] = self.calculate_joule_heating(magnetic_field, wire_diameter, current, temperature=temperature_profile[i])
        if self.plot == "yes":
            self.plot_properties(heat_gen_array, "Heat Generation [J/m3]")
        return heat_gen_array
