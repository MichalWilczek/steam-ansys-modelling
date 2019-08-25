import os
from ansys_corba import CORBA
from source.ansys_table import Table
from source.factory import AnalysisBuilder
from source.factory import AnalysisDirectory
import source.geometry as geometry
import time


class AnsysCommands(object):

    STRAND_DIAMETER = 0.7       # [mm]
    WINDING_SIDE = 0.941        # [mm]
    COIL_LONG_SIDE = 413.21     # [mm]
    COIL_SHORT_SIDE = 126.81    # [mm]
    COIL_INITIAL_RADIUS = 9.15  # [mm]

    def __init__(self):
        self.factory = AnalysisBuilder()
        self.analysis_directory = AnalysisDirectory().get_directory(self.factory.get_dimensionality())
        os.chdir(self.analysis_directory)
        with open('aaS_MapdlID.txt', 'r') as f:
            aasMapdlKey = f.read()
        self.mapdl = CORBA.ORB_init().string_to_object(aasMapdlKey)

    # functions responsible for deleting unnecessary ansys files
    def delete_old_files(self):
        """
        Deletes unnecessary files saved during previous analyses
        """
        self.delete_file(directory=self.analysis_directory, filename='Variable_Input.inp')
        self.delete_file(directory=self.analysis_directory, filename='File_Position.txt')
        self.delete_file(directory=self.analysis_directory, filename='Process_Finished.txt')

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
    def wait_for_process_to_finish(data):
        """
        Writes down in the opened file the APDL commands to create the file named "Process_Finished.txt"
        :param data: Class object to create APDL commands .txt file
        """
        data.write_text('*cfopen,Process_Finished,txt')  # for reading purposes between ansys and python
        data.write_text('*vwrite,1')
        data.write_text('(1(ES16.7))')
        data.write_text('*cfclose')

    def variable_file_invariable_input(self, data):
        """
        :param data: Class object to create APDL commands .txt file
        Creates an input file with parameters used by ANSYS
        """
        data.write_text('/clear')
        data.write_text('/title,Quench_Analysis_' + AnalysisBuilder().get_dimensionality())
        data.write_text('/prep7')
        data.write_text('/nerr,999999999999')
        data.write_text('/graphics,power')
        data.write_text('/show,png')
        data.write_text('electric_analysis={}'.format(self.factory.get_electric_analysis()))

    @staticmethod
    def wait_python(filename, directory, file_length=1):
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
                with open('Process_Finished.txt', 'r') as f:
                    file_input = int(float(f.read()))
                if file_input == 1:
                    f.close()
                    break
                else:
                    exists = False
            else:
                exists = False

    @staticmethod
    def delete_file(filename, directory):
        """
        Deletes file in directory
        :param directory: analysis directory as string
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

    # not needed anymore
    def set_gaussian_initial_temperature_distribution(self, gaussian_temperature_distr):
        """
        Sets initial temperature to all nodes according to gaussian distribution curve
        :param gaussian_temperature_distr: temperature distribution numpy array; 1st column: node number as integer,
         2nd column: temperature as float
        """
        self.allsel()
        for i in range(len(gaussian_temperature_distr[:, 0])):
            node_number = gaussian_temperature_distr[i, 0]
            temperature = gaussian_temperature_distr[i, 1]
            self.mapdl.executeCommandToString("ic,{},temp,{}".format(node_number, temperature))

    # general commands
    def create_dim_table(self, dim_name, dim_type, name1, size1, size2=" ", size3=" "):
        self.mapdl.executeCommand("*dim,{},{},{},{},{},{}".format(dim_name, dim_type, size1, size2, size3, name1))

    def fill_dim_table(self, dim_name, row, column, value):
        self.mapdl.executeCommand("{}({},{})={}".format(dim_name, row, column, value))

    def clear_all(self):
        self.mapdl.executeCommand("/clear,all,")

    def select_nodes(self, node_down, node_up):
        self.mapdl.executeCommand("nsel,s,node,,{},{}".format(node_down, node_up))

    def select_elem_from_nodes(self):
        self.mapdl.executeCommand("esln,s,1,all")

    def allsel(self):
        print(self.mapdl.executeCommandToString("allsel"))

    def allsel_below(self, domain):
        print(self.mapdl.executeCommandToString("allsel,below,{}".format(domain)))

    def input_file(self, filename, extension, add_directory=" "):
        print(self.mapdl.executeCommandToString(
            "/input,{},{},{}\\{}".format(filename, extension, self.analysis_directory, add_directory)))
        self.wait_python(filename='Process_Finished.txt', directory=self.analysis_directory)
        time.sleep(1)
        self.delete_file(filename='Process_Finished.txt', directory=self.analysis_directory)
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
    def define_temperature_for_material_property(self, temperature):
        self.mapdl.executeCommand('mptemp,{},{}'.format(temperature, temperature))

    def define_element_type(self, element_number, element_name):
        self.mapdl.executeCommand('et,{},{}'.format(element_number, element_name))

    def define_element_type_with_keyopt(self, element_number, element_name, keyopt):
        self.mapdl.executeCommand('et,{},{},{}'.format(element_number, element_name, keyopt))

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

    def set_initial_temperature(self, temperature):
        self.allsel()
        print(self.mapdl.executeCommandToString("ic,all,temp,{}".format(temperature)))

    def set_quench_temperature(self, q_temperature):
        print(self.mapdl.executeCommandToString("ic,all,temp,{}".format(q_temperature)))

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
        # print(self.mapdl.executeCommandToString('deltim,1e-5,1e-5,1e-3'))
        print(self.mapdl.executeCommandToString('deltim,5e-4,5e-4,1e-2'))
        print(self.mapdl.executeCommandToString('rescontrol,define,none,none,1'))
        print(self.mapdl.executeCommandToString('tintp,,,,1'))   # switches T calculation from trapezoidal integration (default) into backward Euler formulation

    # postprocessor commands
    def create_file(self, filename, extension):
        print(self.mapdl.executeCommandToString("*cfopen,{},{}".format(filename, extension)))

    def close_file(self):
        print(self.mapdl.executeCommandToString('*cfclose'))

    def set_do_loop(self, min_value, max_value, jump=1):
        self.mapdl.executeCommand("*do,i,{},{},{}".format(min_value, max_value, jump))

    def end_do_loop(self):
        self.mapdl.executeCommand('*enddo')
