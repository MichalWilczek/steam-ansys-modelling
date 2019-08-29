
from source.material_properties import Materials
import numpy as np

class MaterialsLinear(Materials):

    def __init__(self, plot_curves="no", plotting="no"):
        self.plot_curves = plot_curves
        super().__init__(plotting)

    def calculate_qf_resistance(self, qf_down, qf_up, im_temp_profile, im_coil_geom, mag_field, wire_diameter):
        qf_resistance = 0.0
        for i in range(qf_down, qf_up):
            rho_elem = self.cu_rho()
            elem_length = abs(im_coil_geom[i, 1] - im_coil_geom[i-1, 1])
            elem_res = rho_elem*elem_length/self.reduced_wire_area(wire_diameter*0.001)
            qf_resistance += elem_res
        return qf_resistance

    def calculate_cu_rho(self, **kwargs):
        temperature_profile = self.create_temperature_step(self.temp_min, self.temp_max, self.temp_step)
        cu_rho_array = np.zeros((len(temperature_profile), 2))
        for i in range(len(temperature_profile)):
            cu_rho_array[i, 0] = temperature_profile[i]
            cu_rho_array[i, 1] = self.cu_rho()
        if self.plot == "yes":
            self.plot_properties(cu_rho_array, "Cu resistivity, [Ohm*m]")
        return cu_rho_array

    def calculate_cu_thermal_cond(self, **kwargs):
        temperature_profile = self.create_temperature_step(self.temp_min, self.temp_max, self.temp_step)
        cu_thermal_cond_array = np.zeros((len(temperature_profile), 2))
        for i in range(len(temperature_profile)):
            cu_thermal_cond_array[i, 0] = temperature_profile[i]
            cu_thermal_cond_array[i, 1] = self.cu_thermal_cond()
        if self.plot == "yes":
            self.plot_properties(cu_thermal_cond_array, "Cu thermal conductivity, [W/(m*K)]")
        return cu_thermal_cond_array

    def calculate_winding_eq_cp(self, **kwargs):
        temperature_profile = self.create_temperature_step(self.temp_min, self.temp_max, self.temp_step)
        winding_cp_array = np.zeros((len(temperature_profile), 2))
        for i in range(len(temperature_profile)):
            winding_cp_array[i, 0] = temperature_profile[i]
            winding_cp_array[i, 1] = self.cu_cp()
        if self.plot == "yes":
            self.plot_properties(winding_cp_array, "Winding equivalent cp, [J/(kg*K)]")
        return winding_cp_array

    def calculate_g10_therm_cond(self):
        temperature_profile = self.create_temperature_step(self.temp_min, self.temp_max, self.temp_step)
        g10_therm_cond_array = np.zeros((len(temperature_profile), 2))
        for i in range(len(temperature_profile)):
            g10_therm_cond_array[i, 0] = temperature_profile[i]
            g10_therm_cond_array[i, 1] = self.g10_therm_cond()
        if self.plot == "yes":
            self.plot_properties(g10_therm_cond_array, "G10 thermal conductivity, [W/(m*K)]")
        return g10_therm_cond_array

    def calculate_g10_cp(self):
        temperature_profile = self.create_temperature_step(self.temp_min, self.temp_max, self.temp_step)
        g10_cp_array = np.zeros((len(temperature_profile), 2))
        for i in range(len(temperature_profile)):
            g10_cp_array[i, 0] = temperature_profile[i]
            g10_cp_array[i, 1] = self.g10_cp()
        if self.plot == "yes":
            self.plot_properties(g10_cp_array, "G10 Cp, [J/(kg*K)]")
        return g10_cp_array

    # Copper material properties
    @staticmethod
    def cu_rho():
        resistivity = 0.00000000025
        return resistivity

    @staticmethod
    def cu_thermal_cond():
        conductivity = 0.0000001
        return conductivity

    @staticmethod
    def cu_cp():
        cu_cp = 50.0
        return cu_cp

    # G10 material properties
    @staticmethod
    def g10_therm_cond():
        g10_therm_cond = 1.0
        return g10_therm_cond

    @staticmethod
    def g10_cp():
        g10_cp = 5.0
        return g10_cp
