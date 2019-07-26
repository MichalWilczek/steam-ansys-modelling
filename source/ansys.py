import os
from ansys_corba import CORBA
from source.ansys_table import Table
from source.factory import AnalysisBuilder
from source.factory import AnalysisDirectory
import source.geometry as geometry
import time


class AnsysCommands:

    def __init__(self):
        self.analysis_directory = AnalysisDirectory().get_directory()
        os.chdir(self.analysis_directory)
        with open('aaS_MapdlID.txt', 'r') as f:
            aasMapdlKey = f.read()
        self.mapdl = CORBA.ORB_init().string_to_object(aasMapdlKey)

    # functions responsible for creation of input variable file
    def create_variable_file(self):
        """
        Creates an input file with parameters used by ANSYS
        """
        dimension = AnalysisBuilder().get_dimensionality()
        if dimension == "1D":
            return self.create_variable_file_1d()
        elif dimension == "2D":
            return self.create_variable_file_2d()
        else:
            raise ValueError(dimension)

    def create_variable_file_1d(self):
        """
        Creates an input file with parameters used by ANSYS
        """
        data = self.create_variable_table_method()
        self.variable_file_invariable_input(data)
        data.write_text('number_of_windings =' + str(AnalysisBuilder().get_number_of_windings()))
        data.write_text('length_per_winding =' + str(AnalysisBuilder().get_length_per_winding()))
        data.write_text('division_per_winding =' + str(AnalysisBuilder().get_division_per_winding()))
        self.wait_for_process_to_finish(data)
        time.sleep(2)

    def create_variable_file_2d(self):
        """
        Creates an input file with parameters used by ANSYS
        """
        data = self.create_variable_table_method()
        self.variable_file_invariable_input(data)
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
        self.wait_for_process_to_finish(data)
        time.sleep(2)

    @staticmethod
    def create_variable_table_method():
        filename = AnalysisDirectory.get_directory()
        filename += '/Variable_Input'
        extension = 'inp'
        return Table(filename, ext=('.' + extension))

    @staticmethod
    def wait_for_process_to_finish(data):
        data.write_text('*cfopen,Process_Finished,txt')  # for reading purposes between ansys and python
        data.write_text('*vwrite,1')
        data.write_text('(1(ES16.7))')
        data.write_text('*cfclose')

    @staticmethod
    def variable_file_invariable_input(data):
        """
        Creates an input file with parameters used by ANSYS
        """
        data.write_text('/clear')
        data.write_text('/title,Quench_Analysis_' + AnalysisBuilder().get_dimensionality())
        data.write_text('/prep7')
        data.write_text('/nerr,999999999999')

    # functions responsible for deleting unnecessary ansys files
    def delete_old_files(self):
        self.delete_file(filename='Variable_Input.inp')
        self.delete_file(filename='File_Position.txt')
        self.delete_file(filename='Process_Finished.txt')

    def input_material_properties(self):
        dimension = AnalysisBuilder().get_dimensionality()
        print("________________ \nMaterial properties are being uploaded...")
        if dimension == "1D":
            return self.input_file(filename='1D_Material_Properties_Superconducting', extension='inp',
                                   add_directory='Input_Files')
        elif dimension == "2D":
            return self.input_file(filename='2D_Material_Properties_Superconducting', extension='inp',
                                   add_directory='Input_Files')
        else:
            raise ValueError(dimension)

    def input_geometry(self):
        dimension = AnalysisBuilder().get_dimensionality()
        print("________________ \nAnsys geometry is being uploaded...")
        if dimension == "1D":
            return self.input_file(filename='1D_Geometry', extension='inp', add_directory='Input_Files')
        elif dimension == "2D":
            return self.input_file(filename='2D_Geometry', extension='inp', add_directory='Input_Files')
        else:
            raise ValueError(dimension)

    def select_nodes_for_multiple_dimensions(self, class_geometry, x_down_node, x_up_node):
        dimension = AnalysisBuilder().get_dimensionality()
        if dimension == "1D":
            self.select_nodes(node_down=x_down_node, node_up=x_up_node)
        elif dimension == "2D":
            nodes_to_select = class_geometry.convert_imaginary_nodes_set_into_real_nodes(x_down_node=x_down_node,
                                                                                         x_up_node=x_up_node)
            nodes_to_select_ansys = class_geometry.prepare_ansys_nodes_selection_list(real_nodes_list=nodes_to_select)
            self.select_nodes_list(nodes_list=nodes_to_select_ansys)
        else:
            raise ValueError(dimension)

    def select_nodes_for_current_for_multiple_dimensions(self, class_geometry):
        dimension = AnalysisBuilder().get_dimensionality()
        if dimension == "1D":
            self.allsel()
        elif dimension == "2D":
            nodes_for_current = class_geometry.create_node_list_for_current()
            nodes_to_select_ansys = class_geometry.prepare_ansys_nodes_selection_list(real_nodes_list=nodes_for_current)
            self.select_nodes_list(nodes_list=nodes_to_select_ansys)

    def set_ground_for_multiple_dimensions(self, class_geometry):
        dimension = AnalysisBuilder().get_dimensionality()
        if dimension == "1D":
            self.set_ground(node_number=AnalysisBuilder().get_division_in_full_coil() + 1, value=0)
        elif dimension == "2D":
            nodes_for_ground = class_geometry.create_node_list_for_ground()
            nodes_to_select_ansys = class_geometry.prepare_ansys_nodes_selection_list(real_nodes_list=nodes_for_ground)
            self.select_nodes_list(nodes_list=nodes_to_select_ansys)
            self.set_ground(node_number="all", value=0)

    def input_solver_file_for_multiple_dimensions(self):
        dimension = AnalysisBuilder().get_dimensionality()
        if dimension == "1D":
            self.input_file(filename='1D_Solve_Get_Temp', extension='inp', add_directory='input_files')
        elif dimension == "2D":
            self.input_file(filename='2D_Solve_Get_Temp', extension='inp', add_directory='input_files')

    @staticmethod
    def get_temperature_profile_for_multiple_dimensions(class_geometry, npoints):
        dimension = AnalysisBuilder().get_dimensionality()
        if dimension == "1D":
            temperature_profile = class_geometry.load_1d_temperature(directory=AnalysisDirectory.get_directory(),
                                                                     npoints=npoints)
            return temperature_profile
        elif dimension == "2D":
            temperature_profile_1d = class_geometry.load_temperature_and_map_onto_1d_cable(
                directory=AnalysisDirectory.get_directory(), npoints=npoints)
            return temperature_profile_1d

    def wait_python(self, filename, file_length=1, directory=AnalysisDirectory().get_directory()):
        """
        Makes Python wait until process in ANSYS is finished
        :param directory:
        :param filename: filename as string given by ANSYS when it finishes processing
        :param file_length: number of rows in filename as integer
        """
        exists = False
        while exists is False:
            exists = os.path.isfile(directory+"\\"+filename)
            if exists and geometry.file_length(filename, analysis_directory=directory) == file_length:
                os.chdir(directory)
                f = open('Process_Finished.txt', 'r')
                file_input = int(float(f.read()))
                if file_input == 1:
                    f.close()
                else:
                    exists = False
            else:
                exists = False

    @staticmethod
    def delete_file(filename, directory=AnalysisDirectory().get_directory()):
        """
        Deletes file in directory
        :param directory:
        :param filename: filename to delete as string
        """
        full_filename = "{}.".format(filename)
        full_path = "{}\\{}".format(directory, full_filename)
        if os.path.isfile(full_path):
            os.remove(full_path)
        else:
            print("Error: {} file not found".format(full_filename))

    def select_nodes_list(self, nodes_list):
        """
        Selects a set of nodes from given list of nodes
        :param nodes_list: list of lists with lower and higher node to be selected in a set
        """
        for i in range(len(nodes_list)):
            if i == 0:
                print(self.mapdl.executeCommandToString("nsel,s,node,,{},{}".format(nodes_list[i][0], nodes_list[i][1])))
            else:
                print(self.mapdl.executeCommandToString("nsel,a,node,,{},{}".format(nodes_list[i][0], nodes_list[i][1])))

    def unselect_nodes_list(self, nodes_list):
        """
        Selects a set of nodes from given list of nodes
        :param nodes_list: list of lists with lower and higher node to be selected in a set
        """
        for i in range(len(nodes_list)):
            self.mapdl.executeCommand("nsel,u,node,,{},{}".format(nodes_list[i][0], nodes_list[i][1]))

    # general commands
    def select_nodes(self, node_down, node_up):
        self.mapdl.executeCommand("nsel,s,node,,{},{}".format(node_down, node_up))

    def select_elem_from_nodes(self):
        self.mapdl.executeCommand("esln,s,0,all")

    def allsel(self):
        print(self.mapdl.executeCommandToString("allsel"))

    def allsel_below(self, domain):
        print(self.mapdl.executeCommandToString("allsel,below,{}".format(domain)))

    def input_file(self, filename, extension, add_directory=" "):
        print(self.mapdl.executeCommandToString(
            "/input,{},{},{}\\{}".format(filename, extension, self.analysis_directory, add_directory)))
        self.wait_python(filename='Process_Finished.txt')
        self.delete_file(filename='Process_Finished.txt')
        print("File uploaded... \n________________")

    def terminate_analysis(self):
        self.mapdl.terminate()

    def save_analysis(self):
        print(self.mapdl.executeCommandToString("save"))

    def set_dof(self, dof):
        print(self.mapdl.executeCommandToString("dof,{}".format(dof)))

    # coupling commands
    def couple_nodes(self, dof):
        """
        Couples all nodes in previously defined set
        :param dof: 'volt' for voltage or 'temp' for temperature dof
        """
        self.mapdl.executeCommand("cp,next,{},all".format(dof))

    def couple_interface(self, dof):
        self.mapdl.executeCommand("cpintf,{},".format(dof))

    # restart commands
    def save_parameters(self, filename='parameter_file', extension='txt'):
        print(self.mapdl.executeCommandToString("parsav,all,{},{},".format(filename, extension)))

    def load_parameters(self, filename='parameter_file', extension='txt'):
        print(self.mapdl.executeCommandToString("parres,new,{},{},".format(filename, extension)))

    def restart_analysis(self):
        print(self.mapdl.executeCommandToString("antype,,rest,,,continue"))

    # preprocessor commands`
    def enter_preprocessor(self):
        print(self.mapdl.executeCommandToString('/prep7'))

    def modify_material_type(self, element_number):
        print("Material type was modfied")
        self.mapdl.executeCommand("emodif,all,type,{}".format(element_number))

    def modify_material_constant(self, constant_number):
        print("Material constant was modified")
        self.mapdl.executeCommand("emodif,all,real,{}".format(constant_number))

    def modify_material_number(self, material_number):
        print("Material number was modified")
        self.mapdl.executeCommand("emodif,all,mat,{}".format(material_number))

    # solver processor commands
    def enter_solver(self):
        print(self.mapdl.executeCommandToString("/solu"))

    def set_time_step(self, time_step):
        print(self.mapdl.executeCommandToString("time,{}".format(time_step)))

    def set_initial_temperature(self, temperature):
        self.allsel()
        print(self.mapdl.executeCommandToString("ic,all,temp,{}".format(temperature)))

    def set_quench_temperature(self, q_temperature):
        print(self.mapdl.executeCommandToString("ic,all,temp,{}".format(q_temperature)))

    def set_current(self, node_number, value):
        self.mapdl.executeCommand("f,{},amps,{}".format(node_number, value))

    def set_ground(self, node_number, value):
        self.mapdl.executeCommand("d,{},volt,{}".format(node_number, value))

    def start_solution(self):
        self.allsel()
        print(self.mapdl.executeCommandToString('solve'))

    def set_analysis_setting(self):
        print(self.mapdl.executeCommandToString('antype,4'))
        print(self.mapdl.executeCommandToString('trnopt,full'))
        print(self.mapdl.executeCommandToString('kbc,1'))
        print(self.mapdl.executeCommandToString('eqslv,sparse'))
        print(self.mapdl.executeCommandToString('bcsoption,,default'))
        print(self.mapdl.executeCommandToString('lumpm,0'))
        print(self.mapdl.executeCommandToString('autots,on'))
        print(self.mapdl.executeCommandToString('solcontrol,on,on'))
        print(self.mapdl.executeCommandToString('neqit,1000'))
        print(self.mapdl.executeCommandToString('lnsrch,on'))
        # print(self.mapdl.executeCommandToString('deltim,0.0005,0.0005,0.01'))
        print(self.mapdl.executeCommandToString('rescontrol,define,none,none,1'))

    # postprocessor commands
    def create_file(self, filename, extension):
        print(self.mapdl.executeCommandToString("*cfopen,{},{}".format(filename, extension)))

    def close_file(self):
        print(self.mapdl.executeCommandToString('*cfclose'))

    def set_do_loop(self, min_value, max_value, jump=1):
        self.mapdl.executeCommand("*do,i,{},{},{}".format(min_value, max_value, jump))

    def end_do_loop(self):
        self.mapdl.executeCommand('*enddo')
