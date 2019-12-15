
from source.ansys.ansys import Ansys
from source.factory.unit_conversion import UnitConversion
from source.insulation.insulation import Insulation

class AnsysNetwork(Ansys, UnitConversion, Insulation):

    def __init__(self, factory, ansys_input_directory):
        Ansys.__init__(self, factory, ansys_input_directory)

    def input_winding_non_quenched_material_properties(self, magnetic_field_map, class_mat, element_name="link68"):
        """
        Inputs material properties separately for each winding
        as a function of magnetic field strength, resistivity negligible
        :param magnetic_field_map: dictionary; key: winding+%number%, value: magnetic value as float
        :param class_mat:
        :param element_name: ansys 1D element name to be input
        """
        strand_diameter = self.input_data.geometry_settings.type_input.strand_diameter
        for i in range(len(magnetic_field_map.keys())):
            self.delete_material_number(material_number=str(i + 1))
            magnetic_field = magnetic_field_map["winding" + str(i + 1)]
            wire_area = class_mat.wire_area(strand_diameter * UnitConversion.milimeters_to_meters)
            self.define_element_type(element_number=i + 1, element_name=element_name)
            self.define_element_constant(element_number=i + 1, element_constant=wire_area)
            self.define_element_density(element_number=i + 1, value=class_mat.normal_conductor.density_fake)
            superconductor_resistivity = 1.0e-16
            winding_thermal_conductivity = class_mat.calculate_winding_eq_thermal_conductivity(magnetic_field)
            winding_volumetric_heat_capacity = class_mat.calculate_winding_eq_cv(magnetic_field=magnetic_field)

            for j in range(len(winding_thermal_conductivity[:, 0])):
                self.define_temperature_for_material_property(
                    table_placement=j + 1, temperature=winding_thermal_conductivity[j, 0])
                self.define_element_conductivity(element_number=i + 1,
                                                 value=winding_thermal_conductivity[j, 1])
                self.define_element_heat_capacity(element_number=i + 1, value=winding_volumetric_heat_capacity[j, 1])
                if element_name == "link68":
                    self.define_element_resistivity(element_number=i + 1, value=superconductor_resistivity)

    def input_winding_quench_material_properties(self, magnetic_field_map, winding_number,
                                                 class_mat, element_name="link68"):
        """
        Inputs material properties separately for each winding as a function of magnetic field strength,
        coil with resistivity of copper
        :param magnetic_field_map: dictionary; key: winding+%number%, value: magnetic value as float
        :param winding_number:
        :param class_mat:
        :param element_name: ansys 1D element name to be input
        """
        strand_diameter = self.input_data.geometry_settings.type_input.strand_diameter
        number_of_windings = self.input_data.geometry_settings.type_input.number_of_windings

        magnetic_field = magnetic_field_map["winding"+str(winding_number)]
        element_number = number_of_windings + winding_number
        self.delete_material_number(material_number=element_number)

        self.define_element_type(element_number=element_number, element_name=element_name)
        wire_area = class_mat.wire_area(strand_diameter * UnitConversion.milimeters_to_meters)
        self.define_element_constant(element_number=element_number, element_constant=wire_area)
        self.define_element_density(element_number=element_number, value=class_mat.normal_conductor.density_fake)
        winding_resistivity = class_mat.calculate_winding_eq_resistivity(magnetic_field=magnetic_field)
        winding_thermal_conductivity = class_mat.calculate_winding_eq_thermal_conductivity(magnetic_field)
        winding_volumetric_heat_capacity = class_mat.calculate_winding_eq_cv(magnetic_field=magnetic_field)

        for j in range(len(winding_thermal_conductivity[:, 0])):
            self.define_temperature_for_material_property(
                table_placement=j+1, temperature=winding_thermal_conductivity[j, 0])
            self.define_element_conductivity(
                element_number=element_number, value=winding_thermal_conductivity[j, 1])
            self.define_element_heat_capacity(
                element_number=element_number, value=winding_volumetric_heat_capacity[j, 1])
            if element_name == "link68":
                self.define_element_resistivity(element_number=element_number, value=winding_resistivity[j, 1])

    def calculate_insulation_length(self):
        return Insulation.get_insulation_side(
            small_circle=self.input_data.geometry_settings.type_input.strand_diameter *
                         UnitConversion.milimeters_to_meters,
            large_circle=self.input_data.geometry_settings.type_input.strand_diameter_with_insulation
                         * UnitConversion.milimeters_to_meters)

    def get_temperature_profile(self, class_geometry, npoints):
        return class_geometry.load_temperature_and_map_onto_1d_cable(directory=self.directory, npoints=npoints)
