
import time
import math
from source.class_ansys.ansys_net import AnsysNetwork

class Ansys1D(AnsysNetwork):

    def create_variable_file(self):
        """
        Creates an input file with parameters used by ANSYS
        """
        data = self.create_variable_table_method(self.analysis_directory)
        self.variable_file_invariable_input(data)

        data.write_text('number_of_windings =' + str(self.factory.get_number_of_windings()))
        data.write_text('elem_per_line =' + str(1))

        data.write_text('transverse_dimension_winding =' + str(self.calculate_insulation_length()))
        data.write_text('transverse_division_insulation =' + str(self.factory.get_transverse_division_insulation()))

        # variables required when a slab (not magnet) geometry is considered
        data.write_text('division_per_winding = ' + str(self.factory.get_division_per_winding()))
        data.write_text('length_per_winding = ' + str(self.factory.get_length_per_winding()))

        self.wait_for_process_to_finish(data)
        time.sleep(2)

    def input_geometry(self):
        print("________________ \nAnsys geometry is being uploaded...")
        return self.input_file(filename='1D_Geometry', extension='inp', add_directory='Input_Files')

    def input_solver(self):
        self.input_file(filename='1D_Solve_Get_Temp', extension='inp', add_directory='Input_Files')

    def set_ground_in_analysis(self, class_geometry):
        self.set_ground(node_number=self.factory.get_division_in_full_coil() + 1, value=0)

    def select_nodes_in_analysis(self, class_geometry, x_down_node, x_up_node):
        self.select_nodes(node_down=x_down_node, node_up=x_up_node)

    def select_nodes_for_current(self, class_geometry):
        self.allsel()

    def get_temperature_profile(self, class_geometry, npoints):
        temperature_profile = class_geometry.load_1d_temperature(directory=self.factory.get_directory(), npoints=npoints)
        return temperature_profile

    def calculate_effective_insulation_area(self):
        if self.factory.get_number_of_windings() != 1:
            eff_side = (self.WINDING_SIDE + math.pi * self.STRAND_DIAMETER/4.0)/2.0
            winding_total_length = 2.0*self.COIL_SHORT_SIDE + 2.0*self.COIL_LONG_SIDE
            total_insulation_area = eff_side * winding_total_length
            number_divisions_in_winding = (2.0 * self.factory.get_division_long_side() + 2.0 * self.factory.get_division_short_side())
            elem_ins_area = total_insulation_area / (number_divisions_in_winding+1.0)
            elem_ins_area_meters = elem_ins_area * 10.0**(-6.0)
            return elem_ins_area_meters * 4.0
        else:
            return 1.0

    def calculate_insulation_length(self):
        l_eq = 0.5*(self.WINDING_SIDE**2.0-0.25*math.pi*0.7**2.0)/(self.WINDING_SIDE+math.pi*self.STRAND_DIAMETER/4.0)*0.001
        return l_eq
