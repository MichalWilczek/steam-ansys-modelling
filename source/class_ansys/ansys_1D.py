
import time
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
