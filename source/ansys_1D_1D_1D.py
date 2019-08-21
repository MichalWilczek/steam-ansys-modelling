
import time
from source.ansys import AnsysCommands
from source.ansys_table import Table
from source.polynomial_fit import Polynomials
import math

class AnsysCommands1D1D1D(AnsysCommands):

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
        data.write_text('number_of_windings_in_reel =' + str(self.factory.get_number_of_windings_in_reel()))
        data.write_text('elem_per_line =' + str(1))
        data.write_text('transverse_dimension_winding =' + str(self.factory.get_transverse_dimension_winding()))
        data.write_text('transverse_division_insulation =' + str(self.factory.get_transverse_division_insulation()))
        data.write_text('G10_element_area =' + str(self.calculate_insulation_area_1d_1d_1d_quadrupole()))
        data.write_text('division_per_winding = ' + str(self.factory.get_division_per_winding()))
        data.write_text('length_per_winding = ' + str(self.factory.get_length_per_winding()))
        self.wait_for_process_to_finish(data)
        time.sleep(2)

    def input_winding_non_quenched_material_properties(self, magnetic_field_map, class_mat, element_name="link68"):
        """
        Inputs material properties separately for each winding as a function of magnetic field strength, resistivity negliglible
        :param magnetic_field_map: dictionary; key: winding+%number%, value: magnetic value as float
        :param element_name: ansys 1D element name to be input
        """
        self.enter_preprocessor()
        for i in range(len(magnetic_field_map.keys())):
            magnetic_field = magnetic_field_map["winding"+str(i+1)]
            equivalent_winding_area = class_mat.reduced_wire_area(AnsysCommands1D1D1D.STRAND_DIAMETER * 0.001)
            if element_name == "fluid116":
                self.define_element_type_with_keyopt(element_number=i + 1, element_name=element_name, keyopt=1)
                equivalent_winding_diameter = class_mat.reduced_wire_diameter(wire_diameter=AnsysCommands1D1D1D.STRAND_DIAMETER * 0.001)
                self.define_element_constant(element_number=i + 1, element_constant=equivalent_winding_diameter)
            elif element_name == "link33" or element_name == "link68":
                self.define_element_type(element_number=i + 1, element_name=element_name)
                self.define_element_constant(element_number=i + 1, element_constant=equivalent_winding_area)
            self.define_element_density(element_number=i+1, value=class_mat.cu_dens)
            cu_rho = 1.0e-16
            cu_therm_cond = class_mat.calculate_cu_thermal_cond(magnetic_field, rrr=class_mat.rrr)
            winding_cp = class_mat.calculate_winding_eq_cp(magnetic_field)
            for j in range(class_mat.temp_min, class_mat.temp_max, class_mat.temp_step):
                self.define_temperature_for_material_property(temperature=j)
                self.define_element_conductivity(element_number=i+1, value=cu_therm_cond[j, 1])
                self.define_element_heat_capacity(element_number=i+1, value=winding_cp[j, 1])
                if element_name == "link68":
                    self.define_element_resistivity(element_number=i + 1, value=cu_rho)

    def input_insulation_material_properties(self, class_mat):
        """
        Inputs material properties for the insulation, in this case G10
        """
        self.enter_preprocessor()
        element_number = 2*self.factory.get_number_of_windings() + 1
        self.define_element_type(element_number=element_number, element_name="link33")
        insulation_area = self.calculate_insulation_area_1d_1d_1d_quadrupole()
        self.define_element_constant(element_number=element_number, element_constant=insulation_area)
        self.define_element_density(element_number=element_number, value=class_mat.g10_dens)
        g10_therm_cond = class_mat.calculate_g10_therm_cond()
        g10_cp = class_mat.calculate_g10_cp()
        for j in range(class_mat.temp_min, class_mat.temp_max, class_mat.temp_step):
            self.define_temperature_for_material_property(temperature=j)
            self.define_element_conductivity(element_number=element_number, value=g10_therm_cond[j, 1])
            self.define_element_heat_capacity(element_number=element_number, value=g10_cp[j, 1])

    def input_winding_quench_material_properties(self, magnetic_field_map, winding_number, class_mat, element_name="link68"):
        """
        Inputs material properties separately for each winding as a function of magnetic field strength,
        coil with resistivity of copper
        :param magnetic_field_map: dictionary; key: winding+%number%, value: magnetic value as float
        :param element_name: ansys 1D element name to be input
        """
        self.enter_preprocessor()
        magnetic_field = magnetic_field_map["winding"+str(winding_number)]
        element_number = self.factory.get_number_of_windings() + winding_number
        self.define_element_type(element_number=element_number, element_name=element_name)
        equivalent_winding_area = class_mat.reduced_wire_area(AnsysCommands1D1D1D.STRAND_DIAMETER * 0.001)
        self.define_element_constant(element_number=element_number, element_constant=equivalent_winding_area)  # need to calculate the area
        self.define_element_density(element_number=element_number, value=class_mat.cu_dens)
        cu_rho = class_mat.calculate_cu_rho(magnetic_field, rrr=class_mat.rrr)
        cu_therm_cond = class_mat.calculate_cu_thermal_cond(magnetic_field, rrr=class_mat.rrr)
        winding_cp = class_mat.calculate_winding_eq_cp(magnetic_field)
        for j in range(class_mat.temp_min, class_mat.temp_max, class_mat.temp_step):
            self.define_temperature_for_material_property(temperature=j)
            self.define_element_conductivity(element_number=element_number, value=cu_therm_cond[j, 1])
            self.define_element_heat_capacity(element_number=element_number, value=winding_cp[j, 1])
            if element_name == "link68":
                self.define_element_resistivity(element_number=element_number, value=cu_rho[j, 1])

    def input_heat_generation_curve(self, class_mat, magnetic_field):
        self.enter_preprocessor()
        heat_gen_array = class_mat.create_heat_gen_profile(magnetic_field, wire_diameter=self.STRAND_DIAMETER,
                                                     current=self.factory.get_current())
        filename = "HGEN_Table"
        filename_path = self.analysis_directory + "\\" + filename
        hgen = Table(filename_path, ext='.inp')
        hgen.load('hgen_table', heat_gen_array[:, 1], [heat_gen_array[:, 0]])
        hgen.write(['HGEN'])
        self.wait_for_process_to_finish(hgen)
        hgen.close()
        self.input_file(filename=filename, extension="inp")

    def input_heat_generation_table(self, class_mat, magnetic_field):
        self.enter_preprocessor()
        heat_gen_array = class_mat.create_heat_gen_profile(magnetic_field, wire_diameter=self.STRAND_DIAMETER,
                                                     current=self.factory.get_current())
        self.create_dim_table(dim_name="heatgen", dim_type="table", size1=len(heat_gen_array[:, 0]), size2=1, size3=1, name1="temp")
        self.fill_dim_table(dim_name="heatgen", row=0, column=1, value=0.0)
        for i in range(len(heat_gen_array[:, 0])):
            self.fill_dim_table(dim_name="heatgen", row=i+1, column=0, value=heat_gen_array[i, 0])
            self.fill_dim_table(dim_name="heatgen", row=i+1, column=1, value=heat_gen_array[i, 1])

    def input_heat_flow_table(self):
        self.enter_preprocessor()
        heat_flow_array = Polynomials.extract_polynomial_function()

        self.create_dim_table(dim_name="heat_flow", dim_type="table", size1=len(heat_flow_array), size2=1, size3=1, name1="time")
        self.fill_dim_table(dim_name="heat_flow", row=0, column=1, value=0.0)
        for i in range(len(heat_flow_array[:, 0])):
            self.fill_dim_table(dim_name="heat_flow", row=i + 1, column=0, value=heat_flow_array[i, 0])
            self.fill_dim_table(dim_name="heat_flow", row=i + 1, column=1, value=heat_flow_array[i, 1])

    def input_geometry(self, filename='1D_1D_1D_Geometry_quadrupole'):
        """
        Inputs prepared file with geometry to ANSYS environment
        :param filename: geometry file name as string
        """
        print("________________ \nAnsys geometry is being uploaded...")
        self.input_file(filename=filename, extension='inp', add_directory='Input_Files')

    def input_solver(self):
        """
        Inputs prepared file with APDL solver
        """
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

    def calculate_insulation_area_1d_1d_1d_quadrupole(self):
        if self.factory.get_number_of_windings() != 1:
            strand_area = math.pi / 4.0 * AnsysCommands1D1D1D.STRAND_DIAMETER ** 2.0
            winding_area = AnsysCommands1D1D1D.WINDING_SIDE ** 2.0
            number_of_windings_in_layer = self.factory.get_number_of_windings_in_reel()
            number_of_layers = self.factory.get_number_of_windings() / number_of_windings_in_layer
            radius = self.COIL_INITIAL_RADIUS
            coil_total_length = 0.0
            for i in range(int(number_of_layers)):
                coil_total_length += (2.0*(self.COIL_LONG_SIDE+self.COIL_SHORT_SIDE) + math.pi*radius**2.0)*number_of_windings_in_layer
                radius += AnsysCommands1D1D1D.WINDING_SIDE
            G10_total_volume = coil_total_length*(winding_area-strand_area)
            number_divisions_in_winding = (2.0*self.factory.get_division_long_side()+2.0*self.factory.get_division_short_side()+self.factory.get_division_radius()*4.0)
            number_of_transverse_insulation_elements_1 = (number_divisions_in_winding+1.0)*(number_of_windings_in_layer-1)*number_of_layers
            number_of_transverse_insulation_elements_2 = (number_divisions_in_winding+1.0)*(number_of_layers-1)*number_of_windings_in_layer
            total_number_of_G10_elements = number_of_transverse_insulation_elements_1+number_of_transverse_insulation_elements_2
            volume_per_G10_element = G10_total_volume / total_number_of_G10_elements
            G10_element_length = self.factory.get_transverse_dimension_winding() * 1000.0  # [mm]
            G10_element_area = volume_per_G10_element / G10_element_length  # [mm2]
            G10_element_area_meters2 = G10_element_area * 10.0 ** (-6.0)  # [m2]
            print("G10_element_area = {} [m2]".format(G10_element_area_meters2))
            return G10_element_area_meters2
        else:
            return 1.0

    def input_material_properties_file_old(self):
        print("________________ \nMaterial properties are being uploaded...")
        analysis_type = self.factory.get_material_properties_type()
        if analysis_type == "linear":
            self.input_file(filename='1D_1D_1D_Material_Properties_Superconducting_Linear', extension='inp',
                            add_directory='Input_Files')
        elif analysis_type == "nonlinear":
            self.input_file(filename='1D_1D_1D_Material_Properties_Superconducting_Nonlinear', extension='inp',
                            add_directory='Input_Files')
