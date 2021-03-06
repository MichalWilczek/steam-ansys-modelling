
from ansys_corba import CORBA
from source.ansys_interface.ansys_table import Table
from source.common_functions.general_functions import GeneralFunctions
import os

class Ansys(object):

    def __init__(self, factory, ansys_input_directory):
        self.input_data = factory.input_data
        self.directory = factory.directory
        self.output_directory = factory.output_directory
        self.ansys_input_directory = ansys_input_directory
        os.chdir(self.directory)
        with open('aaS_MapdlID.txt', 'r') as f:
            aasMapdlKey = f.read()
        self.mapdl = CORBA.ORB_init().string_to_object(aasMapdlKey)

    def input_heat_generation_table(self, class_mat, magnetic_field):
        strand_diameter = self.input_data.geometry_settings.type_input.d_strand
        current = self.input_data.circuit_settings.electric_ansys_element_input.I_init
        heat_gen_array = class_mat.create_joule_heating_density_profile(magnetic_field, wire_diameter=strand_diameter,
                                                                        current=current)
        self.create_dim_table(dim_name="heatgen", dim_type="table", size1=len(heat_gen_array[:, 0]),
                              size2="1", size3="1", name1="temp")
        self.fill_dim_table(dim_name="heatgen", row=0, column=1, value=0.0)
        for i in range(len(heat_gen_array[:, 0])):
            self.fill_dim_table(dim_name="heatgen", row=i+1, column=0, value=heat_gen_array[i, 0])
            self.fill_dim_table(dim_name="heatgen", row=i+1, column=1, value=heat_gen_array[i, 1])

    # functions responsible for deleting unnecessary ansys_interface files
    def delete_old_ansys_analysis_files(self):
        """
        Deletes unnecessary files saved during previous analyses
        """
        GeneralFunctions.delete_file(directory=self.directory, filename='Variable_Input.inp')
        GeneralFunctions.delete_file(directory=self.directory, filename='File_Position.txt')
        GeneralFunctions.delete_file(directory=self.directory, filename='Process_Finished.txt')

    @staticmethod
    def create_variable_table_method(directory):
        """
        Creates a Class object
        :param directory: analysis_directory as string
        :return: Class for creation of ANSYS files
        """
        filename = directory
        filename += '/Variable_Input'
        extension = 'inp'
        return Table(filename, ext=('.' + extension))

    @staticmethod
    def create_apdl_commands_for_python_waiting_process(data):
        """
        Writes down in the opened file the APDL commands to create the file named "Process_Finished.txt"
        :param data: Class object to create APDL commands .txt file
        """
        data.write_text('*cfopen,Process_Finished,txt')  # for reading purposes between ansys_interface and python
        data.write_text('*vwrite,1')
        data.write_text('(1(ES16.7))')
        data.write_text('*cfclose')

    def create_first_lines_of_input_parameter_file_for_ansys(self, data):
        """
        :param data: Class object to create APDL commands .txt file
        Creates an input file with parameters used by ANSYS
        """
        data.write_text('/clear')
        data.write_text('/title,Quench_Analysis_' + self.input_data.geometry_settings.dimensionality)
        data.write_text('/prep7')
        data.write_text('/nerr,999999999999')
        data.write_text('/graphics,power')
        data.write_text('/show,png')
        data.write_text('electric_analysis={}'.format(GeneralFunctions.change_boolean_into_integer(
            self.input_data.circuit_settings.electric_ansys_elements)))
        data.write_text('insulation_analysis =' + str(GeneralFunctions.change_boolean_into_integer(
            self.input_data.geometry_settings.type_input.type_insulation_settings.insulation_analysis)))

    def select_nodes_list(self, nodes_list):
        """
        Selects a set of nodes from given list of nodes
        :param nodes_list: list of lists with lower and higher node to be selected in a set
        """
        for i in range(len(nodes_list)):
            if i == 0:
                print(self.mapdl.executeCommandToString(
                    "nsel,s,node,,{},{}".format(nodes_list[i][0], nodes_list[i][1])))
            else:
                print(self.mapdl.executeCommandToString(
                    "nsel,a,node,,{},{}".format(nodes_list[i][0], nodes_list[i][1])))

    def unselect_nodes_list(self, nodes_list):
        """
        Selects a set of nodes from given list of nodes
        :param nodes_list: list of lists with lower and higher node to be selected in a set
        """
        for i in range(len(nodes_list)):
            self.mapdl.executeCommand("nsel,u,node,,{},{}".format(nodes_list[i][0], nodes_list[i][1]))

    def unselect_element_type_from_set_of_elements(self, element_number_to_unselect):
        """
        :param element_number_to_unselect:
        """
        self.mapdl.executeCommand("esel,u,type,,{}".format(element_number_to_unselect))

    # general commands
    def create_dim_table(self, dim_name, dim_type, name1, size1, size2=" ", size3=" "):
        self.mapdl.executeCommand("*dim,{},{},{},{},{},{}".format(dim_name, dim_type, size1, size2, size3, name1))

    def fill_dim_table(self, dim_name, row, column, value):
        self.mapdl.executeCommand("{}({},{})={}".format(dim_name, row, column, value))

    def clear_all(self):
        self.mapdl.executeCommand("/clear,all,")

    def select_nodes(self, node_down, node_up):
        self.mapdl.executeCommand("nsel,s,node,,{},{}".format(node_down, node_up))

    def select_elements(self, element_down, element_up):
        self.mapdl.executeCommand("esel,s,elem,,{},{}".format(element_down, element_up))

    def select_elem_from_nodes(self):
        self.mapdl.executeCommand("esln,s,1,all")

    def allsel(self):
        print(self.mapdl.executeCommandToString("allsel"))

    def allsel_below(self, domain):
        print(self.mapdl.executeCommandToString("allsel,below,{}".format(domain)))

    def input_file(self, filename, extension, directory):
        print(self.mapdl.executeCommandToString("/input,{},{},{}".format(filename, extension, directory)))
        end_process = GeneralFunctions.make_python_wait_until_ansys_finishes(
            filename='Process_Finished.txt',
            directory=self.directory)
        if end_process:
            GeneralFunctions.delete_file(filename='Process_Finished.txt', directory=self.directory)
            print("File uploaded... \n---------------")

    def terminate_analysis(self):
        self.mapdl.terminate()

    def save_analysis(self):
        print(self.mapdl.executeCommandToString("save"))

    def set_dof(self, dof):
        print(self.mapdl.executeCommandToString("dof,{}".format(dof)))

    def finish(self):
        print(self.mapdl.executeCommandToString("finish"))

    # coupling commands
    def couple_nodes(self, dof):
        """
        Couples all nodes in previously defined set
        :param dof: 'volt' for voltage or 'temp' for temperature dof
        """
        self.mapdl.executeCommand("cp,next,{},all".format(dof))

    def delete_coupling_relation_between_nodes(self, cp_number):
        self.mapdl.executeCommand("cpdele,{}".format(cp_number))

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
    def define_temperature_for_material_property(self, table_placement, temperature):
        self.mapdl.executeCommand('mptemp,{},{}'.format(table_placement, temperature))

    def define_element_type(self, element_number, element_name):
        self.mapdl.executeCommand('et,{},{}'.format(element_number, element_name))

    def delete_element_type(self, element_number):
        self.mapdl.executeCommand('etdele,{}'.format(element_number))

    def define_parameter(self, parameter_name, parameter):
        self.mapdl.executeCommand('{}={}'.format(parameter_name, parameter))

    def define_element_type_with_keyopt(self, element_number, element_name, keyopt):
        self.mapdl.executeCommand('et,{},{},{}'.format(element_number, element_name, keyopt))

    def delete_material_number(self, material_number):
        self.mapdl.executeCommand('mpdele,all,{}'.format(material_number))

    def define_keyopt(self, element_number, keyopt_1, keyopt_2):
        self.mapdl.executeCommand('keyopt,{},{},{}'.format(element_number, keyopt_1, keyopt_2))

    def define_element_constant(self, element_number, element_constant):
        self.mapdl.executeCommand('r,{},{}'.format(element_number, element_constant))

    def define_element_constants(self, element_number, constant1, constant2):
        self.mapdl.executeCommand('r,{},{},{}'.format(element_number, constant1, constant2))

    def define_element_density(self, element_number, value):
        self.mapdl.executeCommand('mp,dens,{},{}'.format(element_number, value))

    def define_element_conductivity(self, element_number, value, direction="kxx"):
        self.mapdl.executeCommand('mpdata,{},{},,{}'.format(direction, element_number, value))

    def define_element_heat_capacity(self, element_number, value):
        self.mapdl.executeCommand('mpdata,c,{},,{}'.format(element_number, value))

    def define_element_resistivity(self, element_number, value, direction="rsvx"):
        self.mapdl.executeCommand('mpdata,{},{},,{}'.format(direction, element_number, value))

    def enter_preprocessor(self):
        print(self.mapdl.executeCommandToString('/prep7'))

    def enter_postprocessor(self):
        print(self.mapdl.executeCommandToString('/post1'))

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

    def set_time_step(self, time_step, iteration):
        """
        Sets time step and creates APDL variable "time_step" used for further post-processing plotting
        :param time_step: time step as float
        :param iteration: current analysis iteration as integer
        """
        print(self.mapdl.executeCommandToString("time_step={}".format(iteration)))
        print(self.mapdl.executeCommandToString("time,{}".format(time_step)))

    def set_initial_temperature(self, temperature, allsel=True):
        if allsel:
            self.allsel()
        print(self.mapdl.executeCommandToString("ic,all,temp,{}".format(temperature)))

    def set_current(self, node_number, value):
        self.mapdl.executeCommand("f,{},amps,{}".format(node_number, value))

    def set_ground(self, node_number, value):
        self.mapdl.executeCommand("d,{},volt,{}".format(node_number, value))

    def set_heat_generation_in_elements(self, element_number, value):
        self.mapdl.executeCommand("bfe,{},hgen,,{}".format(element_number, value))

    def set_heat_generation_in_nodes(self, node_number, value):
        self.mapdl.executeCommand("bf,{},hgen,{}".format(node_number, value))

    def set_heat_flow_into_nodes(self, value):
        self.mapdl.executeCommand("f,all,heat,{}".format(value))

    def start_solution(self):
        self.allsel()
        print(self.mapdl.executeCommandToString('solve'))

    def set_load_in_solver(self, dof, value):
        print(self.mapdl.executeCommandToString("d, all, {}, {}".format(dof, value)))

    def set_ansys_time_step_settings(self, init_time_step, min_time_step, max_time_step):
        print(self.mapdl.executeCommandToString('deltim,{},{},{}'.format(init_time_step, min_time_step, max_time_step)))

    def set_analysis_setting(self):
        print(self.mapdl.executeCommandToString('antype,4'))
        print(self.mapdl.executeCommandToString('trnopt,full'))
        print(self.mapdl.executeCommandToString('autots,on'))
        print(self.mapdl.executeCommandToString('solcontrol,on,on'))
        print(self.mapdl.executeCommandToString('neqit,1000'))
        print(self.mapdl.executeCommandToString('rescontrol,define,none,none,1'))

        # added for the external circuit
        print(self.mapdl.executeCommandToString('kbc,1'))
        print(self.mapdl.executeCommandToString('eqslv,sparse'))
        print(self.mapdl.executeCommandToString('bcsoption,, default'))
        # print(self.mapdl.executeCommandToString('dspoption,default,incore'))
        print(self.mapdl.executeCommandToString('lumpm, 0'))
        print(self.mapdl.executeCommandToString('lnsrch, on'))

    # postprocessor commands
    def create_file(self, filename, extension):
        print(self.mapdl.executeCommandToString("*cfopen,{},{}".format(filename, extension)))

    def close_file(self):
        print(self.mapdl.executeCommandToString('*cfclose'))

    def set_do_loop(self, min_value, max_value, increase=1):
        self.mapdl.executeCommand("*do,i,{},{},{}".format(min_value, max_value, increase))

    def end_do_loop(self):
        self.mapdl.executeCommand('*enddo')
