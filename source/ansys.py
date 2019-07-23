
import os
from ansys_corba import CORBA
from source.factory import AnalysisDirectory
from source.ansys_input import AnsysInput


class AnsysCommands:

    def __init__(self):
        """
        :param directory: analysis_directory as string
        """
        self.analysis_directory = AnalysisDirectory().get_directory()
        os.chdir(self.analysis_directory)
        with open('aaS_MapdlID.txt', 'r') as f:
            aasMapdlKey = f.read()
        self.mapdl = CORBA.ORB_init().string_to_object(aasMapdlKey)

    @staticmethod
    def wait_python(filename, file_length=1, directory=AnalysisDirectory().get_directory()):
        """
        Makes Python wait until process in ANSYS is finished
        :param filename: filename as string given by ANSYS when it finishes processing
        :param file_length: number of rows in filename as integer
        """
        full_filename = "{}.".format(filename)
        full_path = "{}\\{}".format(directory, full_filename)
        exists = False
        while exists is False:
            exists = os.path.isfile(full_path)
            if exists and AnsysInput.file_length(full_filename) == file_length:
                os.chdir(directory)
                f = open('Process_Finished.txt', 'r')
                # print("file_input = {}".format(f.read()))
                file_input = int(float(f.read()))
                print("The value of file input = {}".format(file_input))
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
             print(self.mapdl.executeCommandToString("nsel,u,node,,{},{}".format(nodes_list[i][0], nodes_list[i][1])))

    # general commands
    def select_nodes(self, node_down, node_up):
        print(self.mapdl.executeCommandToString("nsel,s,node,,{},{}".format(node_down, node_up)))

    def select_elem_from_nodes(self):
        print(self.mapdl.executeCommandToString("esln,s,0,all"))

    def allsel(self):
        print(self.mapdl.executeCommandToString("allsel"))

    def allsel_below(self, domain):
        print(self.mapdl.executeCommandToString("allsel,below,{}".format(domain)))

    def input_file(self, filename, extension, add_directory=" "):
        print(self.mapdl.executeCommandToString("/input,{},{},{}\\{}".format(filename, extension, self.analysis_directory, add_directory)))
        self.wait_python(filename='Process_Finished.txt')
        self.delete_file(filename='Process_Finished.txt')

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
        print(self.mapdl.executeCommandToString("cp,next,{},all".format(dof)))

    def couple_interface(self, dof):
        print(self.mapdl.executeCommandToString("cpintf,{},".format(dof)))

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
        print(self.mapdl.executeCommandToString("emodif,all,type,{}".format(element_number)))

    def modify_material_constant(self, constant_number):
        print(self.mapdl.executeCommandToString("emodif,all,real,{}".format(constant_number)))

    def modify_material_number(self, material_number):
        print(self.mapdl.executeCommandToString("emodif,all,mat,{}".format(material_number)))

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
        print(self.mapdl.executeCommandToString("f,{},amps,{}".format(node_number, value)))

    def set_ground(self, node_number, value):
        print(self.mapdl.executeCommandToString("d,{},volt,{}".format(node_number, value)))

    def start_solution(self):
        self.allsel()
        print(self.mapdl.executeCommandToString('solve'))

    def set_analysis_setting(self):
        self.mapdl.executeCommand('antype,4')
        self.mapdl.executeCommand('trnopt,full')
        self.mapdl.executeCommand('kbc,1')
        self.mapdl.executeCommand('eqslv,sparse')
        self.mapdl.executeCommand('bcsoption,,default')
        self.mapdl.executeCommand('lumpm,0')
        self.mapdl.executeCommand('autots,on')
        self.mapdl.executeCommand('solcontrol,on,on')
        self.mapdl.executeCommand('neqit,1000')
        self.mapdl.executeCommand('lnsrch,on')
        self.mapdl.executeCommand('deltim,0.0025,0.00025,0.0025')
        self.mapdl.executeCommand('rescontrol,define,none,none,1')

    # postprocessor commands
    def create_file(self, filename, extension):
        print(self.mapdl.executeCommandToString("*cfopen,{},{}".format(filename, extension)))

    def close_file(self):
        print(self.mapdl.executeCommandToString('*cfclose'))

    def set_do_loop(self, min_value, max_value, jump=1):
        self.mapdl.executeCommand("*do,i,{},{},{}".format(min_value, max_value, jump))

    def end_do_loop(self):
        self.mapdl.executeCommand('*enddo')





