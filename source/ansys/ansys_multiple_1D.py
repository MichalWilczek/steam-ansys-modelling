
from source.ansys.ansys_network import AnsysNetwork

class AnsysMultiple1D(AnsysNetwork):

    def __init__(self, factory, ansys_input_directory):
        AnsysNetwork.__init__(self, factory, ansys_input_directory)

    def check_if_point_mass_is_applied(self):
        if self.input_data.geometry_settings.type_input.strand_to_strand_contact_correction_factor == 1.0 and \
                self.input_data.geometry_settings.type_input.resin_filling_factor <= 10e-10:
            return False
        else:
            return True

    def input_point_mass_material_properties(self, class_mat, element_name="mass71"):
        self.enter_preprocessor()
        element_number = 2*self.input_data.geometry_settings.type_input.number_of_windings + 3
        self.define_element_type(element_number=element_number, element_name=element_name)
        self.define_element_constant(element_number=element_number, element_constant="point_mass_volume")
        # real constant interpreted as volume with density and specific heat defined as material properties
        self.define_keyopt(element_number, keyopt_1=3, keyopt_2=0)
        # heat generation independent of temperature
        self.define_keyopt(element_number, keyopt_1=4, keyopt_2=0)
        self.define_element_density(element_number=element_number, value=class_mat.insulation.density_fake)

        cv_array = class_mat.insulation.calculate_volumetric_heat_capacity()
        for j in range(len(cv_array[:, 0])):
            self.define_temperature_for_material_property(table_placement=j+1, temperature=cv_array[j, 0])
            self.define_element_heat_capacity(element_number=element_number, value=cv_array[j, 1])
        return element_number

    def input_insulation_material_properties(self, class_mat):
        """
        Inputs material properties for the insulation
        """
        # normal insulation elements
        self.enter_preprocessor()
        element_number = 2*self.input_data.geometry_settings.type_input.number_of_windings + 1
        self.define_element_type(element_number=element_number, element_name="link33")
        self.define_element_constant(
            element_number=element_number,
            element_constant=self.calculate_insulation_element_area())
        self.define_element_density(element_number=element_number, value=class_mat.insulation.density_fake)
        insulation_thermal_conductivity = class_mat.insulation.calculate_thermal_conductivity()
        insulation_volumetric_heat_capacity = class_mat.insulation.calculate_volumetric_heat_capacity()

        for j in range(len(insulation_thermal_conductivity[:, 0])):
            self.define_temperature_for_material_property(
                table_placement=j+1, temperature=insulation_thermal_conductivity[j, 0])
            self.define_element_conductivity(
                element_number=element_number, value=insulation_thermal_conductivity[j, 1])
            self.define_element_heat_capacity(
                element_number=element_number, value=insulation_volumetric_heat_capacity[j, 1])

        # corner insulation elements
        self.enter_preprocessor()
        element_number = 2*self.input_data.geometry_settings.type_input.number_of_windings + 2
        self.define_element_type(element_number=element_number, element_name="link33")
        self.define_element_constant(
            element_number=element_number,
            element_constant=str(self.calculate_insulation_element_area()/2))
        self.define_element_density(element_number=element_number, value=class_mat.insulation.density_fake)
        insulation_thermal_conductivity = class_mat.insulation.calculate_thermal_conductivity()
        insulation_volumetric_heat_capacity = class_mat.insulation.calculate_volumetric_heat_capacity()

        for j in range(len(insulation_thermal_conductivity[:, 0])):
            self.define_temperature_for_material_property(
                table_placement=j+1, temperature=insulation_thermal_conductivity[j, 0])
            self.define_element_conductivity(
                element_number=element_number, value=insulation_thermal_conductivity[j, 1])
            self.define_element_heat_capacity(
                element_number=element_number, value=insulation_volumetric_heat_capacity[j, 1])

    def input_solver(self):
        """
        Inputs prepared file with APDL solver
        """
        self.input_file(filename='1D_1D_1D_Solve_Get_Temp', extension='inp', directory=self.ansys_input_directory)

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
        nodes_to_select = class_geometry.convert_imaginary_nodes_set_into_real_nodes_1d_1d_winding_number(
            winding_number=winding_number, x_down_node=x_down_node, x_up_node=x_up_node)
        nodes_to_select_ansys = class_geometry.prepare_ansys_nodes_selection_list(real_nodes_list=nodes_to_select)
        self.select_nodes_list(nodes_list=nodes_to_select_ansys)

    def select_nodes_for_current(self, **kwargs):
        nodes_to_select_ansys = [[1, 1]]
        self.select_nodes_list(nodes_list=nodes_to_select_ansys)

    def calculate_insulation_element_area(self):
        pass

    def calculate_total_winding_length(self):
        pass

    def calculate_number_of_elements_per_winding(self):
        pass
