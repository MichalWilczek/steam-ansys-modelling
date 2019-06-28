
import os
from ansys_table import table
from ansys_corba import CORBA


class Commands(object):

    def __init__(self, directory):
        """
        :param directory: analysis_directory as string
        """
        self.analysis_directory = directory
        os.chdir(self.analysis_directory)
        with open('aaS_MapdlID.txt', 'r') as f:
            aasMapdlKey = f.read()
        self.mapdl = CORBA.ORB_init().string_to_object(aasMapdlKey)

    @staticmethod
    def create_variable_file(division, npoints, coil_length):
        """
        Creates an input file with parameters used by ANSYS
        :param division: number of elements as integer
        :param npoints: number of nodes as integer
        :param coil_length: length of the 1D domain as float
        """
        filename = os.getcwd()
        filename += '/Variable_Input'
        extension = 'inp'
        data = table(filename, ext=('.' + extension))
        data.write_text('/clear')
        data.write_text('/title,quench_analysis')
        data.write_text('/prep7')
        data.write_text('/nerr,999999999999')
        data.write_text('npoints =' + str(npoints))
        data.write_text('division =' + str(division))
        data.write_text('length =' + str(coil_length))
        data.write_text('*cfopen,Process_Finished,txt')     # for reading purposes between ansys and python
        data.write_text('*vwrite,1')
        data.write_text('(1(ES16.7))')
        data.write_text('*cfclose')

    def wait_python(self, filename, file_length=1):
        """
        Makes Python wait until process in ANSYS is finished
        :param filename: filename as string given by ANSYS when it finishes processing
        :param file_length: number of rows in filename as integer
        """
        full_filename = "{}.".format(filename)
        full_path = "{}\\{}".format(self.analysis_directory, full_filename)
        exists = False
        while exists is False:
            exists = os.path.isfile(full_path)
            if exists and self.file_length(full_filename) == file_length:
                os.chdir(self.analysis_directory)
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

    def delete_file(self, filename):
        """
        Deletes file in directory
        :param filename: filename to delete as string
        """
        full_filename = "{}.".format(filename)
        full_path = "{}\\{}".format(self.analysis_directory, full_filename)
        if os.path.isfile(full_path):
            os.remove(full_path)
        else:
            print("Error: {} file not found".format(full_filename))

    def file_length(self, filename):
        """
        Reads number of files in file
        :param filename: filename to read as string
        """
        myfile = open(filename)
        return int(len(myfile.readlines()))

    # general commands
    def select_nodes(self, node_down, node_up):
        print(self.mapdl.executeCommandToString("nsel,s,node,,{},{}".format(node_down, node_up)))

    def select_elem_from_nodes(self):
        print(self.mapdl.executeCommandToString("esln,s,0,all"))

    def allsel(self):
        print(self.mapdl.executeCommandToString("allsel"))

    def input_file(self, filename, extension, add_directory=" "):
        print(self.mapdl.executeCommandToString("/input,{},{},{}\\{}".format(filename, extension, self.analysis_directory, add_directory)))
        self.wait_python(filename='Process_Finished.txt')
        self.delete_file(filename='Process_Finished.txt')

    def terminate_analysis(self):
        self.mapdl.terminate()

    def save_analysis(self):
        print(self.mapdl.executeCommandToString("save"))

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
        self.allsel()
        print(self.mapdl.executeCommandToString("f,{},amps,{}".format(node_number, value)))

    def set_ground(self, node_number, value):
        self.allsel()
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





