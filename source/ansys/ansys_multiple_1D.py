
import math
from source.ansys.ansys_network import AnsysNetwork

class AnsysMultiple1D(AnsysNetwork):

    def __init__(self, factory, ansys_input_directory):
        AnsysNetwork.__init__(self, factory, ansys_input_directory)

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
        nodes_to_select = class_geometry.convert_imaginary_nodes_set_into_real_nodes_1d_1d_winding_number(winding_number=winding_number, x_down_node=x_down_node, x_up_node=x_up_node)
        nodes_to_select_ansys = class_geometry.prepare_ansys_nodes_selection_list(real_nodes_list=nodes_to_select)
        self.select_nodes_list(nodes_list=nodes_to_select_ansys)

    def select_nodes_for_current(self, **kwargs):
        nodes_to_select_ansys = [[1, 1]]
        self.select_nodes_list(nodes_list=nodes_to_select_ansys)

    def calculate_insulation_area_1d_1d_1d(self):

        if self.factory.number_of_windings() != 1:
            strand_area = math.pi / 4.0 * self.STRAND_DIAMETER ** 2.0
            winding_area = self.WINDING_SIDE ** 2.0
            G10_volume_per_winding = (winding_area - strand_area) * self.factory.length_per_winding() * 1000.0  # [mm3]
            G10_total_volume = G10_volume_per_winding * self.factory.number_of_windings()
            total_number_of_G10_elements = (self.factory.number_of_windings() - 1) * (self.factory.division_per_winding() + 1)
            volume_per_G10_element = G10_total_volume / total_number_of_G10_elements
            G10_element_length = self.factory.transverse_dimension_winding() * 1000.0  # [mm]
            G10_element_area = volume_per_G10_element / G10_element_length  # [mm2]
            G10_element_area_meters2 = G10_element_area * 10.0 ** (-6.0)  # [m2]
            print("G10_element_area = {} [m2]".format(G10_element_area_meters2))
            return G10_element_area_meters2
        else:
            return 1.0

    def calculate_insulation_area_1d_1d_1d_quadrupole(self):
        if self.factory.number_of_windings() != 1:
            strand_area = math.pi / 4.0 * self.STRAND_DIAMETER ** 2.0
            winding_area = self.WINDING_SIDE ** 2.0
            number_of_windings_in_layer = self.factory.number_of_windings_in_reel()
            number_of_layers = self.factory.number_of_windings() / number_of_windings_in_layer
            coil_total_length = self.factory.number_of_windings()*(2*self.COIL_SHORT_SIDE+2*self.COIL_LONG_SIDE)
            G10_total_volume = coil_total_length*(winding_area-strand_area)
            number_divisions_in_winding = (2.0 * self.factory.division_long_side() + 2.0 * self.factory.division_short_side())
            number_of_transverse_insulation_elements_1 = (number_divisions_in_winding+1.0)*(number_of_windings_in_layer-1)*number_of_layers
            number_of_transverse_insulation_elements_2 = (number_divisions_in_winding+1.0)*(number_of_layers-1)*number_of_windings_in_layer
            total_number_of_G10_elements = number_of_transverse_insulation_elements_1+number_of_transverse_insulation_elements_2
            volume_per_G10_element = G10_total_volume / total_number_of_G10_elements
            G10_element_length = self.factory.transverse_dimension_winding() * 1000.0  # [mm]
            G10_element_area = volume_per_G10_element / G10_element_length  # [mm2]
            G10_element_area_meters2 = G10_element_area * 10.0 ** (-6.0)  # [m2]
            print("G10_element_area = {} [m2]".format(G10_element_area_meters2))
            return G10_element_area_meters2
        else:
            return 1.0
