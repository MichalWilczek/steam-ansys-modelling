import time
from source.ansys.ansys import Ansys

class Ansys2D(Ansys):

    # TO BE MODIFED !!!
    def create_variable_file(self):
        """
        Creates an input file with parameters used by ANSYS
        """
        data = self.create_variable_table_method(self.analysis_directory)
        self.variable_file_invariable_input(data)
        data.write_text('number_of_windings =' + str(self.factory.number_of_windings))
        data.write_text('length_per_winding =' + str(self.factory.length_per_winding))
        data.write_text('division_per_winding =' + str(self.factory.division_per_winding))
        data.write_text('quench_init_pos =' + str(self.factory.quench_init_pos))
        data.write_text('quench_init_length =' + str(self.factory.quench_init_length))
        data.write_text('winding_plane_max_number_nodes =' + str(self.factory.winding_plane_max_number_nodes))
        data.write_text('transverse_dimension_winding =' + str(self.factory.transverse_dimension_winding))
        data.write_text('transverse_dimension_insulation =' + str(self.factory.transverse_dimension_insulation))
        data.write_text('transverse_division_winding =' + str(self.factory.transverse_division_winding))
        data.write_text('transverse_division_insulation =' + str(self.factory.transverse_division_insulation))
        self.wait_for_process_to_finish(data)
        time.sleep(2)

    def input_geometry(self):
        print("________________ \nAnsys geometry is being uploaded...")
        return self.input_file(filename='2D_Geometry', extension='inp', add_directory='Input_Files')

    def input_solver(self):
        self.input_file(filename='2D_Solve_Get_Temp', extension='inp', add_directory='input_files')

    def set_ground_in_analysis(self, class_geometry):
        nodes_for_ground = class_geometry.create_node_list_for_ground()
        nodes_to_select_ansys = class_geometry.prepare_ansys_nodes_selection_list(real_nodes_list=nodes_for_ground)
        self.select_nodes_list(nodes_list=nodes_to_select_ansys)
        self.set_ground(node_number="all", value=0)

    def select_nodes_in_analysis(self, class_geometry, x_down_node, x_up_node):
        nodes_to_select = class_geometry.convert_imaginary_nodes_set_into_real_nodes(x_down_node=x_down_node, x_up_node=x_up_node)
        nodes_to_select_ansys = class_geometry.prepare_ansys_nodes_selection_list(real_nodes_list=nodes_to_select)
        self.select_nodes_list(nodes_list=nodes_to_select_ansys)

    def select_nodes_for_current(self, class_geometry):
        nodes_for_current = class_geometry.create_node_list_for_current()
        nodes_to_select_ansys = class_geometry.prepare_ansys_nodes_selection_list(real_nodes_list=nodes_for_current)
        self.select_nodes_list(nodes_list=nodes_to_select_ansys)

    def get_temperature_profile(self, class_geometry, npoints):
        temperature_profile_1d = class_geometry.load_temperature_and_map_onto_1d_cable(directory=self.factory.get_ansys_scripts_directory(), npoints=npoints)
        return temperature_profile_1d
