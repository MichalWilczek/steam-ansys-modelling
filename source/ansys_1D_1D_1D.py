
import time
from source.ansys import AnsysCommands

import math

class AnsysCommands1D1D1D(AnsysCommands):

    STRAND_DIAMETER = 0.7   # [mm]
    WINDING_SIDE = 0.941    # [mm]

    def create_variable_file(self):
        """
        Creates an input file with parameters used by ANSYS
        """
        data = self.create_variable_table_method(self.analysis_directory)
        self.variable_file_invariable_input(data)
        data.write_text('number_of_windings =' + str(self.factory.get_number_of_windings()))
        data.write_text('division_long_side =' + str(self.factory.get_division_long_side()))
        data.write_text('division_short_side =' + str(self.factory.get_division_short_side()))
        data.write_text('division_radius =' + str(self.factory.get_division_radius()))
        data.write_text('number_of_windings =' + str(self.factory.get_number_of_windings()))
        data.write_text('number_of_windings_in_reel =' + str(self.factory.get_number_of_windings_in_reel()))
        data.write_text('elem_per_line =' + str(1))
        data.write_text('transverse_dimension_winding =' + str(self.factory.get_transverse_dimension_winding()))
        data.write_text('transverse_division_insulation =' + str(self.factory.get_transverse_division_insulation()))
        data.write_text('G10_element_area =' + str(self.calculate_insulation_area_1d_1d_1d()))
        self.wait_for_process_to_finish(data)
        time.sleep(2)

    def input_winding_non_quenched_material_properties(self, magnetic_field_map):
        self.enter_preprocessor()
        for i in range(len(magnetic_field_map.keys())):
            mat = self.choose_material_repository()
            magnetic_field = magnetic_field_map["winding"+str(i+1)]
            self.define_element_type(element_number=i+1, element_name="link68")
            equivalent_winding_area = mat.eq_winding_cu_area(AnsysCommands1D1D1D.STRAND_DIAMETER*0.001)
            self.define_element_constant(element_number=i+1, element_constant=equivalent_winding_area)  # need to calculate the area
            self.define_element_density(element_number=i+1, value=mat.cu_dens)
            cu_rho = 1.0e-16
            cu_therm_cond = mat.calculate_cu_thermal_cond(magnetic_field)
            winding_cp = mat.calculate_winding_eq_cp(magnetic_field)
            for j in range(mat.temp_min, mat.temp_max, mat.temp_step):
                self.define_temperature_for_material_property(temperature=j)
                self.define_element_resistivity(element_number=i+1, value=cu_rho)
                self.define_element_conductivity(element_number=i+1, value=cu_therm_cond[j, 1])
                self.define_element_heat_capacity(element_number=i+1, value=winding_cp[j, 1])

    def input_insulation_material_properties(self):
        self.enter_preprocessor()
        mat = self.choose_material_repository()
        element_number = 2*self.factory.get_number_of_windings() + 1
        self.define_element_type(element_number=element_number, element_name="link33")
        insulation_area = self.calculate_insulation_area_1d_1d_1d()
        self.define_element_constant(element_number=element_number, element_constant=insulation_area)
        self.define_element_density(element_number=element_number, value=mat.g10_dens)
        g10_therm_cond = mat.calculate_g10_therm_cond()
        g10_cp = mat.calculate_g10_cp()
        for j in range(mat.temp_min, mat.temp_max, mat.temp_step):
            self.define_temperature_for_material_property(temperature=j)
            self.define_element_conductivity(element_number=element_number, value=g10_therm_cond[j, 1])
            self.define_element_heat_capacity(element_number=element_number, value=g10_cp[j, 1])

    def input_winding_quench_material_properties(self, magnetic_field_map, winding_number):
        magnetic_field = magnetic_field_map["winding"+str(winding_number+self.factory.get_number_of_windings())]
        element_number = self.factory.get_number_of_windings() + winding_number + self.factory.get_number_of_windings()
        mat = self.choose_material_repository()
        self.define_element_type(element_number=element_number, element_name="link68")
        equivalent_winding_area = mat.eq_winding_cu_area(AnsysCommands1D1D1D.STRAND_DIAMETER * 0.001)
        self.define_element_constant(element_number=element_number, element_constant=equivalent_winding_area)  # need to calculate the area
        self.define_element_density(element_number=element_number, value=mat.cu_dens)
        cu_rho = mat.calculate_cu_rho(magnetic_field)
        cu_therm_cond = mat.calculate_cu_thermal_cond(magnetic_field)
        winding_cp = mat.calculate_winding_eq_cp(magnetic_field)
        for j in range(mat.temp_min, mat.temp_max, mat.temp_step):
            self.define_temperature_for_material_property(temperature=j)
            self.define_element_resistivity(element_number=element_number, value=cu_rho[j, 1])
            self.define_element_conductivity(element_number=element_number, value=cu_therm_cond[j, 1])
            self.define_element_heat_capacity(element_number=element_number, value=winding_cp[j, 1])

    def input_geometry(self):
        print("________________ \nAnsys geometry is being uploaded...")
        return self.input_file(filename='1D_1D_1D_Geometry_quadrupole', extension='inp', add_directory='Input_Files')

    def input_solver(self):
        self.input_file(filename='1D_1D_1D_Solve_Get_Temp', extension='inp', add_directory='input_files')

    def set_ground_in_analysis(self, class_geometry):
        nodes_for_ground = class_geometry.create_node_list_for_ground()
        nodes_to_select_ansys = class_geometry.prepare_ansys_nodes_selection_list(real_nodes_list=nodes_for_ground)
        self.select_nodes_list(nodes_list=nodes_to_select_ansys)
        self.set_ground(node_number="all", value=0)

    def select_nodes_in_analysis(self, class_geometry, x_down_node, x_up_node):
        nodes_to_select = class_geometry.convert_imaginary_nodes_set_into_real_nodes_1d_1d(x_down_node=x_down_node,
                                                                                           x_up_node=x_up_node)
        nodes_to_select_ansys = class_geometry.prepare_ansys_nodes_selection_list(real_nodes_list=nodes_to_select)
        self.select_nodes_list(nodes_list=nodes_to_select_ansys)

    def select_nodes_in_analysis_mag(self, class_geometry, winding_number, x_down_node, x_up_node):
        nodes_to_select = class_geometry.convert_imaginary_nodes_set_into_real_nodes_1d_1d_winding_number(winding_number=winding_number, x_down_node=x_down_node, x_up_node=x_up_node)
        nodes_to_select_ansys = class_geometry.prepare_ansys_nodes_selection_list(real_nodes_list=nodes_to_select)
        self.select_nodes_list(nodes_list=nodes_to_select_ansys)

    def select_nodes_for_current(self, class_geometry):
        nodes_to_select_ansys = [[1, 1]]
        self.select_nodes_list(nodes_list=nodes_to_select_ansys)

    def get_temperature_profile(self, class_geometry, npoints):
        temperature_profile_1d = class_geometry.load_temperature_and_map_onto_1d_cable(
            directory=self.analysis_directory, npoints=npoints)
        return temperature_profile_1d

    def calculate_insulation_area_1d_1d_1d(self):
        if self.factory.get_number_of_windings() != 1:
            strand_area = math.pi / 4.0 * AnsysCommands1D1D1D.STRAND_DIAMETER ** 2.0
            winding_area = AnsysCommands1D1D1D.WINDING_SIDE ** 2.0
            G10_volume_per_winding = (winding_area - strand_area) * self.factory.get_length_per_winding() * 1000.0  # [mm3]
            G10_total_volume = G10_volume_per_winding * self.factory.get_number_of_windings()
            total_number_of_G10_elements = (self.factory.get_number_of_windings() - 1) * (
                        self.factory.get_division_per_winding() + 1)
            volume_per_G10_element = G10_total_volume / total_number_of_G10_elements
            G10_element_length = self.factory.get_transverse_dimension_winding() * 1000.0  # [mm]
            G10_element_area = volume_per_G10_element / G10_element_length  # [mm2]
            G10_element_area_meters2 = G10_element_area * 10.0 ** (-6.0)  # [m2]
            print("G10_element_area = {} [m2]".format(G10_element_area_meters2))
            return G10_element_area_meters2
        else:
            return 1.0





    # def input_material_properties(self):
    #     print("________________ \nMaterial properties are being uploaded...")
    #     analysis_type = self.factory.get_material_properties_type()
    #     if analysis_type == "linear":
    #         self.input_file(filename='1D_1D_1D_Material_Properties_Superconducting_Linear', extension='inp',
    #                         add_directory='Input_Files')
    #     elif analysis_type == "nonlinear":
    #         self.input_file(filename='1D_1D_1D_Material_Properties_Superconducting_Nonlinear', extension='inp',
    #                         add_directory='Input_Files')