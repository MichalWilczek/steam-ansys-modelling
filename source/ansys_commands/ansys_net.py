
import math
from source.ansys_commands.ansys import AnsysCommands

class AnsysNetwork(AnsysCommands):

    def input_winding_non_quenched_material_properties(self, magnetic_field_map, class_mat, element_name="link68"):
        """
        Inputs material properties separately for each winding as a function of magnetic field strength, resistivity negliglible
        :param magnetic_field_map: dictionary; key: winding+%number%, value: magnetic value as float
        :param element_name: ansys 1D element name to be input
        """
        self.enter_preprocessor()
        for i in range(len(magnetic_field_map.keys())):
            magnetic_field = magnetic_field_map["winding"+str(i+1)]
            equivalent_winding_area = class_mat.reduced_wire_area(self.factory.STRAND_DIAMETER * 0.001)
            if element_name == "fluid116":
                self.define_element_type_with_keyopt(element_number=i + 1, element_name=element_name, keyopt=1)
                equivalent_winding_diameter = class_mat.reduced_wire_diameter(wire_diameter=self.factory.STRAND_DIAMETER * 0.001)
                self.define_element_constant(element_number=i + 1, element_constant=equivalent_winding_diameter)
            elif element_name == "link33" or element_name == "link68":
                self.define_element_type(element_number=i + 1, element_name=element_name)
                self.define_element_constant(element_number=i + 1, element_constant=equivalent_winding_area)
            self.define_element_density(element_number=i+1, value=class_mat.cu_dens)
            cu_rho = 1.0e-16
            cu_therm_cond = class_mat.calculate_cu_thermal_cond(magnetic_field=magnetic_field, rrr=class_mat.rrr)
            winding_cp = class_mat.calculate_winding_eq_cp(magnetic_field=magnetic_field)

            for j in range(len(cu_therm_cond[:, 0])):
                self.define_temperature_for_material_property(table_placement=j+1, temperature=cu_therm_cond[j, 0])
                self.define_element_conductivity(element_number=i+1, value=cu_therm_cond[j, 1])
                self.define_element_heat_capacity(element_number=i+1, value=winding_cp[j, 1])
                if element_name == "link68":
                    self.define_element_resistivity(element_number=i + 1, value=cu_rho)

    def input_hot_spot_insulation_material_properties(self, class_mat, number_of_initially_quenched_windings=1):
        self.enter_preprocessor()
        element_number = 2 * self.factory.number_of_windings + 3
        self.define_element_type(element_number=element_number, element_name="link33")

        eff_side = (self.factory.WINDING_SIDE + math.pi * self.factory.STRAND_DIAMETER / 4.0) / 2.0
        hot_spot_length = 0.002  # m
        eff_area = (eff_side*0.001) * hot_spot_length * float(number_of_initially_quenched_windings)

        self.define_element_constant(element_number=element_number, element_constant=eff_area)
        self.define_element_density(element_number=element_number, value=class_mat.g10_dens)
        g10_therm_cond = class_mat.calculate_g10_therm_cond()
        g10_cp = class_mat.calculate_g10_cp()

        for j in range(len(g10_therm_cond[:, 0])):
            self.define_temperature_for_material_property(table_placement=j+1, temperature=g10_therm_cond[j, 0])
            self.define_element_conductivity(element_number=element_number, value=g10_therm_cond[j, 1])
            self.define_element_heat_capacity(element_number=element_number, value=g10_cp[j, 1])
        return element_number

    def input_winding_quench_material_properties(self, magnetic_field_map, winding_number, class_mat, element_name="link68"):
        """
        Inputs material properties separately for each winding as a function of magnetic field strength,
        coil with resistivity of copper
        :param magnetic_field_map: dictionary; key: winding+%number%, value: magnetic value as float
        :param element_name: ansys 1D element name to be input
        """
        self.enter_preprocessor()
        magnetic_field = magnetic_field_map["winding"+str(winding_number)]
        element_number = self.factory.number_of_windings + winding_number
        self.define_element_type(element_number=element_number, element_name=element_name)
        equivalent_winding_area = class_mat.reduced_wire_area(self.factory.STRAND_DIAMETER * 0.001)
        self.define_element_constant(element_number=element_number, element_constant=equivalent_winding_area)  # need to calculate the area
        self.define_element_density(element_number=element_number, value=class_mat.cu_dens)
        cu_rho = class_mat.calculate_cu_rho(magnetic_field=magnetic_field, rrr=class_mat.rrr)
        cu_therm_cond = class_mat.calculate_cu_thermal_cond(magnetic_field=magnetic_field, rrr=class_mat.rrr)
        winding_cp = class_mat.calculate_winding_eq_cp(magnetic_field=magnetic_field)
        for j in range(len(cu_therm_cond[:, 0])):
            self.define_temperature_for_material_property(table_placement=j+1, temperature=cu_therm_cond[j, 0])
            self.define_element_conductivity(element_number=element_number, value=cu_therm_cond[j, 1])
            self.define_element_heat_capacity(element_number=element_number, value=winding_cp[j, 1])
            if element_name == "link68":
                self.define_element_resistivity(element_number=element_number, value=cu_rho[j, 1])

    def calculate_insulation_length(self):
        l_eq = 0.5*(self.factory.WINDING_SIDE**2.0-0.25*math.pi*0.7**2.0)/(self.factory.WINDING_SIDE+math.pi*self.factory.STRAND_DIAMETER/4.0)*0.001
        return l_eq*2.0

    def get_temperature_profile(self, class_geometry, npoints):
        temperature_profile_1d = class_geometry.load_temperature_and_map_onto_1d_cable(
            directory=self.analysis_directory, npoints=npoints)
        return temperature_profile_1d
