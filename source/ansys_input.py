
from source.ansys_table import Table
from source.ansys import AnsysCommands
from source.factory import AnalysisBuilder
from source.factory import AnalysisDirectory
from source.geometry import Geometry
import time
import os


class AnsysInput:

    # functions responsible for creation of input variable file
    @staticmethod
    def create_variable_file():
        """
        Creates an input file with parameters used by ANSYS
        """
        dimension = AnalysisBuilder().get_dimensionality()
        if dimension == "1D":
            return AnsysInput.create_variable_file_1d()
        elif dimension == "2D":
            return AnsysInput.create_variable_file_2d()
        else:
            raise ValueError(dimension)

    @staticmethod
    def create_variable_file_1d():
        """
        Creates an input file with parameters used by ANSYS
        :param division: number of elements as integer
        :param npoints: number of nodes as integer
        :param coil_length: length of the 1D domain as float
        """
        AnsysInput.variable_file_invariable_input()
        data = AnsysInput.create_variable_table_method()
        data.write_text('number_of_windings =' + str(AnalysisBuilder().get_number_of_windings()))
        data.write_text('length_per_winding =' + str(AnalysisBuilder().get_length_per_winding()))
        data.write_text('division_per_winding =' + str(AnalysisBuilder().get_division_per_winding()))
        AnsysInput.wait_for_process_to_finish()
        time.sleep(2)

    @staticmethod
    def create_variable_file_2d():
        """
        Creates an input file with parameters used by ANSYS
        """
        AnsysInput.variable_file_invariable_input()
        data = AnsysInput.create_variable_table_method()
        data.write_text('number_of_windings =' + str(AnalysisBuilder().get_number_of_windings()))
        data.write_text('length_per_winding =' + str(AnalysisBuilder().get_length_per_winding()))
        data.write_text('division_per_winding =' + str(AnalysisBuilder().get_division_per_winding()))
        data.write_text('quench_init_pos =' + str(AnalysisBuilder().get_quench_init_pos()))
        data.write_text('quench_init_length =' + str(AnalysisBuilder().get_quench_init_length()))
        data.write_text(
            'winding_plane_max_number_nodes =' + str(AnalysisBuilder().get_winding_plane_max_number_nodes()))
        data.write_text('transverse_dimension_winding =' + str(AnalysisBuilder().get_transverse_dimension_winding()))
        data.write_text(
            'transverse_dimension_insulation =' + str(AnalysisBuilder().get_transverse_dimension_insulation()))
        data.write_text('transverse_division_winding =' + str(AnalysisBuilder().get_transverse_division_winding()))
        data.write_text(
            'transverse_division_insulation =' + str(AnalysisBuilder().get_transverse_division_insulation()))
        AnsysInput.wait_for_process_to_finish()
        time.sleep(2)

    @staticmethod
    def create_variable_table_method():
        filename = os.getcwd()
        filename += '/Variable_Input'
        extension = 'inp'
        return Table(filename, ext=('.' + extension))

    @staticmethod
    def wait_for_process_to_finish():
        data = AnsysInput.create_variable_table_method()
        data.write_text('*cfopen,Process_Finished,txt')  # for reading purposes between ansys and python
        data.write_text('*vwrite,1')
        data.write_text('(1(ES16.7))')
        data.write_text('*cfclose')

    @staticmethod
    def variable_file_invariable_input():
        """
        Creates an input file with parameters used by ANSYS
        """
        data = AnsysInput.create_variable_table_method()
        data.write_text('/clear')
        data.write_text('/title,Quench_Analysis_' + AnalysisBuilder().get_dimensionality())
        data.write_text('/prep7')
        data.write_text('/nerr,999999999999')

    # functions responsible for deleting unnecessary ansys files
    @staticmethod
    def delete_old_files():
        AnsysCommands().delete_file(filename='Variable_Input.inp')
        AnsysCommands().delete_file(filename='File_Position.txt')
        AnsysCommands().delete_file(filename='Process_Finished.txt')

    @staticmethod
    def input_material_properties():
        dimension = AnalysisBuilder().get_dimensionality()
        if dimension == "1D":
            return AnsysCommands().input_file(filename='1D_Material_Properties_Superconducting', extension='inp', add_directory='Input_Files')
        elif dimension == "2D":
            return AnsysCommands().input_file(filename='2D_Material_Properties_Superconducting', extension='inp', add_directory='Input_Files')
        else:
            raise ValueError(dimension)

    @staticmethod
    def input_geometry():
        dimension = AnalysisBuilder().get_dimensionality()
        if dimension == "1D":
            return AnsysCommands().input_file(filename='1D_Geometry', extension='inp', add_directory='Input_Files')
        elif dimension == "2D":
            return AnsysCommands().input_file(filename='2D_Geometry', extension='inp', add_directory='Input_Files')
        else:
            raise ValueError(dimension)

    @staticmethod
    def select_nodes_for_multiple_dimensions(x_down_node, x_up_node):
        dimension = AnalysisBuilder().get_dimensionality()
        if dimension == "1D":
            AnsysCommands().select_nodes(node_down=x_down_node, node_up=x_up_node)
        elif dimension == "2D":
            nodes_to_select = Geometry().convert_imaginary_nodes_set_into_real_nodes(x_down_node=x_down_node, x_up_node=x_up_node)
            nodes_to_select_ansys = Geometry().prepare_ansys_nodes_selection_list(real_nodes_list=nodes_to_select)
            AnsysCommands().select_nodes_list(nodes_list=nodes_to_select_ansys)
        else:
            raise ValueError(dimension)

    @staticmethod
    def select_nodes_for_current_for_multiple_dimensions():
        dimension = AnalysisBuilder().get_dimensionality()
        if dimension == "1D":
            return
        elif dimension == "2D":
            nodes_for_current = Geometry.create_node_list_for_current()
            nodes_to_select_ansys = Geometry.prepare_ansys_nodes_selection_list(real_nodes_list=nodes_for_current)
            AnsysCommands().select_nodes_list(nodes_list=nodes_to_select_ansys)

    @staticmethod
    def set_ground_for_multiple_dimensions():
        dimension = AnalysisBuilder().get_dimensionality()
        if dimension == "1D":
            AnsysCommands().set_ground(node_number=AnalysisBuilder().get_division_in_full_coil()+1, value=0)
        elif dimension == "2D":
            nodes_for_ground = Geometry.create_node_list_for_ground()
            nodes_to_select_ansys = Geometry.prepare_ansys_nodes_selection_list(real_nodes_list=nodes_for_ground)
            AnsysCommands().select_nodes_list(nodes_list=nodes_to_select_ansys)
            AnsysCommands().set_ground(node_number="all", value=0)

    @staticmethod
    def input_solver_file_for_multiple_dimensions():
        dimension = AnalysisBuilder().get_dimensionality()
        if dimension == "1D":
            AnsysCommands().input_file(filename='1D_Solve_Get_Temp', extension='inp', add_directory='input_files')
        elif dimension == "2D":
            AnsysCommands().input_file(filename='2D_Solve_Get_Temp', extension='inp', add_directory='input_files')

    @staticmethod
    def get_temperature_profile_for_multiple_dimensions(npoints):
        dimension = AnalysisBuilder().get_dimensionality()
        if dimension == "1D":
            return
        elif dimension == "2D":
            temperature_profile_1d = Geometry().load_temperature_and_map_onto_1d_cable(directory=AnalysisDirectory.get_directory(), npoints=npoints)
            return temperature_profile_1d

    @staticmethod
    def file_length(filename):
        """
        Reads number of rows in file
        :param filename: filename to read as string
        """
        myfile = open(filename)
        return int(len(myfile.readlines()))
